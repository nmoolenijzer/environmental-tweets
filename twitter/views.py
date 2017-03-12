#------------------------------------------------------------------------------
# Imports
#   -all library/module imports go here-
import oauth2
import json
import random
import nltk
from nltk.corpus import names
from nltk.corpus import pros_cons
from django.shortcuts import render, redirect
from django.http import HttpResponse
import datetime
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from django.urls import reverse
from dateutil import parser
import numpy as np
import plotly.offline as pltly
import plotly.graph_objs as go
import django_rq
import time
import logging
from rq import Connection
from rq.job import Job
from redis import Redis
from django.conf import settings
import sys

data = {};
dates = []

def analyzeJSON(classifier, jsonResponse, items, data, counter):
	for obj in jsonResponse['statuses']:
		total = 0
		tokens = nltk.word_tokenize(obj['full_text'])
		pos = nltk.pos_tag(tokens)
		words_to_analyze = []
		for (word, tag) in pos:
			if not("@" in tag):
				words_to_analyze.append(word)
		for word in words_to_analyze:
			classification = classifier.classify({ 'word': word })
			score = classifier.prob_classify({ 'word': word }).prob(classification)
			if (classification == "pro"):
				if ("JJ" in word or "RB" in word): total += (score*100)
				else: total += (score*5)
			else:
				if ("JJ" in word or "RB" in word): total -= (score*100)
				else: total -= (score*5)
		avg = 0;
		if len(words_to_analyze) != 0: avg = total/float(len(words_to_analyze))

		items.append({ 'name': obj['user']['name'], 'text': obj['full_text'], 'avg': total, 'count': counter, 'tz': obj['user']['time_zone']})

		if (not(obj['user']['time_zone'] in data['timezones'])):
			data["timezones"][obj['user']['time_zone']] = 1
		else:
			data["timezones"][obj['user']['time_zone']] += 1

		if (not(obj['user']['time_zone'] in data['timezones_sentiment'])):
			data["timezones_sentiment"][obj['user']['time_zone']] = total
		else:
			data["timezones_sentiment"][obj['user']['time_zone']] += total

		datetimeObj = parser.parse(obj['created_at'])
		dates.append(datetimeObj)
		data["sentiments"].append(total)
		for i in range(obj['retweet_count']):
			data["retweets"].append(total)

		counter += 1

	return counter

def getTwitterData():

	nltk.data.path.append('./static/twitter/nltk_dir')

	labeled_pros_cons = []
	for word in pros_cons.words('IntegratedPros.txt'):
		labeled_pros_cons.append((word, 'pro'))

	for word in pros_cons.words('IntegratedCons.txt'):
		labeled_pros_cons.append((word, 'con'))

	random.shuffle(labeled_pros_cons)

	features = []
	for (word, pro_con) in labeled_pros_cons:
		features.append(({'word': word}, pro_con))

	classifier = nltk.NaiveBayesClassifier.train(features)

	consumerKey = 'eBa29YaUmi43aCmN9dDjKaTIN'
	consumerToken = 'AZOkA4JVCgmE7NJURB3jQWjIQlG5aF6oQAfKX4JFwpncHYAjpP'
	tokenKey = '827224004347977735-cq8ZzwvQMZIMvPS8ANwZ5Cq8OS3rKvy';
	tokenSecret = 'bctJjCgxtqsfMcCToRvSzOOZBVRZeIwZkP1ij34y49qMR'

	consumer = oauth2.Consumer(key=consumerKey, secret=consumerToken)
	token = oauth2.Token(key=tokenKey, secret=tokenSecret)
	client = oauth2.Client(consumer, token)
	searchUrl = 'https://api.twitter.com/1.1/search/tweets.json?q=%40EPA%20-filter%3Aretweets&result_type=recent&count=100&tweet_mode=extended&exclude_replies=true'
	resp, content = client.request(searchUrl, method="GET", body=b"", headers=None)

	stringResponse = content.decode("utf-8")
	jsonResponse = json.loads(stringResponse)

	counter = 1

	data = {}
	data["sentiments"] = []
	data["items"] = []
	data["retweets"] = []
	data["timezones"] = {}
	data["timezones_sentiment"] = {}

	counter = analyzeJSON(classifier, jsonResponse, data["items"], data, counter)

	while ('next_results' in jsonResponse['search_metadata']):
		resp, content = client.request( 'https://api.twitter.com/1.1/search/tweets.json' + str(jsonResponse['search_metadata']['next_results']) + '&tweet_mode=extended&exclude_replies=true', method="GET", body=b"", headers=None )

		stringResponse = content.decode("utf-8")
		jsonResponse = json.loads(stringResponse)

		counter = analyzeJSON(classifier, jsonResponse, data["items"], data, counter)


	return data;

def plotBaseData(data):

	data = [go.Histogram(
					x=data["sentiments"],
					opacity=0.75,
					marker=dict(
						color="#DB5461"
					),
					name='Tweets'
			),
			go.Histogram(
					x=data["retweets"],
					opacity=0.75,
					marker=dict(
						color="#8AA29E"
					),
					name='Retweets'
			)]
	layout = go.Layout(barmode='overlay', title='Sentiment Analysis of Tweets Containing @EPA',
						titlefont=dict(
							family='Raleway',
							size=18,
							color='#031634'
						),
						xaxis=dict(
							title='Sentiment',
							titlefont=dict(
								family='Raleway',
								size=18,
								color='#031634'
							),
							tickfont=dict(
								family='Raleway',
								size=12,
								color='#031634'
							)
						),
						yaxis=dict(
							title='Count',
							titlefont=dict(
								family='Raleway',
								size=18,
								color='#031634'
							),
							tickfont=dict(
								family='Raleway',
								size=12,
								color='#031634'
							)
						))
	figure = go.Figure(data = data, layout = layout)
	graph = pltly.plot(figure, output_type='div')

	graph = graph.replace('displayModeBar:"hover"', 'displayModeBar:false')
	graph = graph.replace('"showLink": true', '"showLink": false')

	return graph;

def plotTzPie(data):
	if None in data["timezones"]: del data["timezones"][None]

	data = [go.Pie(
				labels=data["timezones"].keys(),
				values=data["timezones"].values(),
				textinfo='none'
			)]
	layout = go.Layout(title='Timezones of Tweets Containing @EPA',
						titlefont=dict(
							family='Raleway',
							size=18,
							color='#031634'
						),
						font=dict(
							family='Raleway',
							size=18,
							color='#031634'
						))
	figure = go.Figure(data = data, layout = layout)
	graph = pltly.plot(figure, output_type='div')

	graph = graph.replace('displayModeBar:"hover"', 'displayModeBar:false')
	graph = graph.replace('"showLink": true', '"showLink": false')

	return graph;

def plotTzBar(data):
	if None in data["timezones_sentiment"]: del data["timezones_sentiment"][None]

	data = [go.Bar(
				x=data["timezones_sentiment"].keys(),
				y=data["timezones_sentiment"].values()
			)]
	layout = go.Layout(title='Sentiment of Tweets Containing @EPA by Timezone',
						titlefont=dict(
							family='Raleway',
							size=18,
							color='#031634'
						),
						xaxis=dict(
							title='Timezone',
							titlefont=dict(
								family='Raleway',
								size=18,
								color='#031634'
							),
							tickfont=dict(
								family='Raleway',
								size=12,
								color='#031634'
							)
						),
						yaxis=dict(
							title='Overall Sentiment',
							titlefont=dict(
								family='Raleway',
								size=18,
								color='#031634'
							),
							tickfont=dict(
								family='Raleway',
								size=12,
								color='#031634'
							)
						),
						height=600,
						margin=go.Margin(
							b=200
						))
	figure = go.Figure(data = data, layout = layout)
	graph = pltly.plot(figure, output_type='div')

	graph = graph.replace('displayModeBar:"hover"', 'displayModeBar:false')
	graph = graph.replace('"showLink": true', '"showLink": false')

	return graph;

def load_charts(request):
	try:
		connection = django_rq.get_connection()
		job = Job.fetch(request.session['job-id'], connection=connection)

		while (job.status != "finished" and job.status != "failed"):
			time.sleep(0.1)

		if (job.status == "failed"):
			return HttpResponse("Something went wrong - try refreshing.", content_type='text/plain')

		data = job.result

		data = {'graph': plotBaseData(data), 'tzGraph':plotTzPie(data), 'tsGraph':plotTzBar(data), 'items': data["items"], 'median': np.median(data["sentiments"]), 'mean': np.mean(data["sentiments"])}

		return HttpResponse(render(request, 'charts.html', data, content_type='application/html'))

	except Exception as e:
		print("--------------ERROR")
		print(e)
		print("--------------ERROR")
		sys.stdout.flush()
		return redirect('/')


def methods(request):
	return HttpResponse(render(request, 'methods.html', content_type='application/html'))

def index(request):
	try:
		job = django_rq.enqueue(getTwitterData)
		request.session['job-id'] = job.id

		return HttpResponse(render(request, 'index.html', content_type='application/html'))

	except Exception as e:
		print("--------------ERROR")
		print(e)
		print("--------------ERROR")
		sys.stdout.flush()
		return HttpResponse("Too many requests - try again in a few seconds.", content_type='text/plain')

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

	trainer = features[10000:]
	tester = features[:10000]
	classifier = nltk.NaiveBayesClassifier.train(features)

	consumer = oauth2.Consumer(key='eBa29YaUmi43aCmN9dDjKaTIN', secret='AZOkA4JVCgmE7NJURB3jQWjIQlG5aF6oQAfKX4JFwpncHYAjpP')
	token = oauth2.Token(key='827224004347977735-cq8ZzwvQMZIMvPS8ANwZ5Cq8OS3rKvy', secret='bctJjCgxtqsfMcCToRvSzOOZBVRZeIwZkP1ij34y49qMR')
	client = oauth2.Client(consumer, token)
	searchUrl = 'https://api.twitter.com/1.1/search/tweets.json?q=%40EPA%20-filter%3Aretweets&result_type=recent&count=100&tweet_mode=extended&exclude_replies=true'
	resp, content = client.request(searchUrl, method="GET", body=b"", headers=None)

	stringResponse = content.decode("utf-8")
	jsonResponse = json.loads(stringResponse)

	counter = 1

	data = {}
	data["sentiments"] = []
	data["items"] = []
	items = data["items"]
	data["retweets"] = []
	data["timezones"] = {}
	data["timezones_sentiment"] = {}

	counter = analyzeJSON(classifier, jsonResponse, items, data, counter)

	while ('next_results' in jsonResponse['search_metadata']):
		resp, content = client.request( 'https://api.twitter.com/1.1/search/tweets.json' + str(jsonResponse['search_metadata']['next_results']) + '&tweet_mode=extended&exclude_replies=true', method="GET", body=b"", headers=None )

		stringResponse = content.decode("utf-8")
		jsonResponse = json.loads(stringResponse)

		counter = analyzeJSON(classifier, jsonResponse, items, data, counter)


	# image = (buffer.getValue(), "image/png")
    # print("\nConfidence can also be analyzed:")
    # print(nltk.classify.accuracy(classifier, tester));
	#
    # print("\nAnd which training data is most important:")
    # print(classifier.show_most_informative_features(5));

	return data;

def plotBaseData(data):

	pData = [go.Histogram(
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
						xaxis=dict(
							title='Sentiment'
						),
						yaxis=dict(
							title='Count'
						))
	fig = go.Figure(data = pData, layout = layout)
	graph = pltly.plot(fig, output_type='div')

	graph = graph.replace('displayModeBar:"hover"', 'displayModeBar:false')
	graph = graph.replace('"showLink": true', '"showLink": false')

	return graph;

def plotTzPie(data):
	if None in data["timezones"]: del data["timezones"][None]

	tData = [go.Pie(
				labels=data["timezones"].keys(),
				values=data["timezones"].values()
			)]
	tzLayout = go.Layout(title='Timezones of Tweets Containing @EPA')
	tzFig = go.Figure(data = tData, layout = tzLayout)
	tzGraph = pltly.plot(tzFig, output_type='div')

	tzGraph = tzGraph.replace('displayModeBar:"hover"', 'displayModeBar:false')
	graph = tzGraph.replace('"showLink": true', '"showLink": false')

	return graph;

def plotTzBar(data):

	if None in data["timezones_sentiment"]: del data["timezones_sentiment"][None]

	tsData = [go.Bar(
				x=data["timezones_sentiment"].keys(),
				y=data["timezones_sentiment"].values()
			)]
	tsLayout = go.Layout(title='Timezones of Tweets Containing @EPA',
						xaxis=dict(
							title='Timezone'
						),
						yaxis=dict(
							title='Overall Sentiment'
						))
	tsFig = go.Figure(data = tsData, layout = tsLayout)
	tsGraph = pltly.plot(tsFig, output_type='div')

	tsGraph = tsGraph.replace('displayModeBar:"hover"', 'displayModeBar:false')
	graph = tsGraph.replace('"showLink": true', '"showLink": false')

	return graph;

def check_status(request):
	connection = django_rq.get_connection()
	job = Job.fetch(request.session['job-id'], connection=connection)

	while (job.status != "finished" and job.status != "failed"):
		time.sleep(0.1)

	data = job.result
	items = data["items"]

	data = {'graph': plotBaseData(data), 'tzGraph':plotTzPie(data), 'tsGraph':plotTzBar(data), 'items': items, 'mean': np.mean(data["sentiments"])}

	return HttpResponse(render(request, 'charts.html', data, content_type='application/html'))

def update_charts(request):
	connection = django_rq.get_connection()
	job = Job.fetch(request.session['job-id'], connection=connection)

	return HttpResponse(render(request, 'charts.html', job.result, content_type='application/html'))

def index(request):

	graphType = request.GET.get("graph")

	job = django_rq.enqueue(getTwitterData)
	request.session['job-id'] = job.id

	return HttpResponse(render(request, 'index.html', content_type='application/html'))

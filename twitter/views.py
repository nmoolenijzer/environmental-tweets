#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
__author__ = 'Nick Moolenijzer'
__contact__ = 'nicolaas.b.moolenijzer.17@dartmouth.edu'
__copyright__ = '(c) Nick Moolenijzer 2017'
__license__ = 'MIT'
__date__ = 'Thu Feb  2 14:02:12 2017'
__status__ = "initial release"
__url__ = "___"

"""
Name:           views.py
Compatibility:  Python 3.5
Description:    This program handles all the views and twitter analysis for the Django app

Requires:       oauth2, json, random, nltk, dateutil, numpy, plotly, rq, django-rq

AUTHOR:         Nick Moolenijzer
ORGANIZATION:   Dartmouth College
Contact:        nicolaas.b.moolenijzer.17@dartmouth.edu
Copyright:      (c) Nick Moolenijzer 2017

"""
#------------------------------------------------------------------------------
# Imports
#   -all library/module imports go here-
#python libraries for various tool tasks
import json
import random
import datetime
from dateutil import parser
import time
import logging
import sys

#authorization library for making GET req to Twitter
import oauth2

#NLTK libraries to classify data
import nltk
from nltk.corpus import pros_cons

#django libraries
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings

#data analysis and plotting libraries
import numpy as np
import plotly.offline as pltly
import plotly.graph_objs as go

#Redis libraries for background workers
import django_rq
from rq import Connection
from rq.job import Job
from redis import Redis

connection = django_rq.get_connection()

'''
Function used to analyze the JSON response data from Twitter
Params:
	classifier - NTLK Naive Bayes' classifier
	jsonResponse - the JSON response from Twitter REST APIs call
	data - the data structure to add to
	counter - current count of Tweets read

Returns:
	counter - current count of Tweets read

'''
def analyzeJSON(classifier, jsonResponse, data, counter):
	#if twitter didn't return statuses, return
	if (not('statuses' in jsonResponse)):
		return counter

	#for each tweet in the Twitter response
	for tweet in jsonResponse['statuses']:
		#init total as 0
		total = 0
		#tokenize the tweet
		tokens = nltk.word_tokenize(tweet['full_text'])
		#get the parts of speech from the tokens
		pos = nltk.pos_tag(tokens)
		#init empty data set to analyze
		words_to_analyze = []
		#for each word/tag pair in parts of speech analysis...
		for (word, tag) in pos:
			#check if is an @ sign or contains one - don't include if so
			if not("@" in word):
				words_to_analyze.append((word, tag))
		#for each word to analyze...
		for (word, tag) in words_to_analyze:
			#classify the word as positive or negative
			classification = classifier.classify({ 'word': word })
			#score using basic probability that it is correct
			score = classifier.prob_classify({ 'word': word }).prob(classification)
			#if pro, add to score
			if (classification == "pro"):
				#check if is adjective or adverb - if so, weight 100
				if ("JJ" in tag or "RB" in tag):
					total += (score*100)
				#check if is noun or verb - if so, weight 20
				elif ("NN" in tag or "VB" in tag):
					total += (score*20)
			#otherwise subtract
			else:
				#check if is adjective or adverb - if so, weight 100
				if ("JJ" in tag or "RB" in tag):
					total -= (score*100)
				#check if is noun or verb - if so, weight 20
				elif ("NN" in tag or "VB" in tag):
					total -= (score*20)

		#get the user's timezone
		timeZone = tweet['user']['time_zone']

		#add data about the tweet for tweet table
		data["items"].append({ 'name': tweet['user']['name'], 'text': tweet['full_text'], 'avg': total, 'count': counter, 'tz': timeZone})

		#increment or init the timezone count
		if (not(timeZone in data['timezones'])):
			data["timezones"][timeZone] = 1
		else:
			data["timezones"][timeZone] += 1

		#add the total for timezone sentiment analysis
		if (not(timeZone in data['timezones_sentiment'])):
			data["timezones_sentiment"][timeZone] = total
		else:
			data["timezones_sentiment"][timeZone] += total

		#add date and time of tweet
		datetimetweet = parser.parse(tweet['created_at'])
		data["dates"].append(datetimetweet)

		#add total sentiment to data
		data["sentiments"].append(total)

		#add total weighted by retweet count
		for i in range(tweet['retweet_count']):
			data["retweets"].append(total)

		#increment counter
		counter += 1

	#return current count
	return counter

'''
Function used to create the classifier using NLTK Naive Bayes' classifier
Params: NONE

Returns:
	classifier - classifier object created by NLTK library

'''
def createClassifier():
	#add data path to nltk
	nltk.data.path.append('./static/twitter/nltk_dir')

	#add labeled pros and cons
	labeled_pros_cons = []
	#label pros
	for word in pros_cons.words('IntegratedPros.txt'):
		labeled_pros_cons.append((word, 'pro'))
	#label cons
	for word in pros_cons.words('IntegratedCons.txt'):
		labeled_pros_cons.append((word, 'con'))

	#shuffle order to mix up pros/cons
	random.shuffle(labeled_pros_cons)

	#add feature list, just word refernce
	features = []
	for (word, pro_con) in labeled_pros_cons:
		features.append(({'word': word}, pro_con))

	#return classifier
	return nltk.NaiveBayesClassifier.train(features)

'''
Function used to retrieve the JSON response data from Twitter
Params: NONE

Returns:
	data - all of the parsed JSON data returned by Twitter API call

'''
def getTwitterData(cap):
	#create classifier
	classifier = createClassifier();

	#Twitter consumer and token keys
	consumerKey = 'eBa29YaUmi43aCmN9dDjKaTIN'
	consumerToken = 'AZOkA4JVCgmE7NJURB3jQWjIQlG5aF6oQAfKX4JFwpncHYAjpP'
	tokenKey = '827224004347977735-cq8ZzwvQMZIMvPS8ANwZ5Cq8OS3rKvy';
	tokenSecret = 'bctJjCgxtqsfMcCToRvSzOOZBVRZeIwZkP1ij34y49qMR'

	#create consumer/token/client with auth keys
	consumer = oauth2.Consumer(key=consumerKey, secret=consumerToken)
	token = oauth2.Token(key=tokenKey, secret=tokenSecret)
	client = oauth2.Client(consumer, token)

	#make twitter search API request
	searchUrl = 'https://api.twitter.com/1.1/search/tweets.json?q=%40EPA%20-filter%3Aretweets&result_type=recent&count=100&tweet_mode=extended&exclude_replies=true'
	resp, content = client.request(searchUrl, method="GET", body=b"", headers=None)

	#decode and parse result
	stringResponse = content.decode("utf-8")
	jsonResponse = json.loads(stringResponse)

	#start counter at 1
	counter = 1

	#create data dictionary with each necessary part
	data = {}
	data["sentiments"] = []
	data["items"] = []
	data["dates"] = []
	data["retweets"] = []
	data["timezones"] = {}
	data["timezones_sentiment"] = {}


	#if twitter didn't return statuses, return error
	if (not('search_metadata' in jsonResponse)):
		print("--------------START ERROR--------------")
		print("Maximum requests reached - try again in 15 minutes")
		print(jsonResponse)
		print("--------------END ERROR--------------")
		sys.stdout.flush()
		return {"failed": "Twitter rate limites reached - wait 15 minutes and try again"}
	#otherwise...
	else:
		#analyze first response
		counter = analyzeJSON(classifier, jsonResponse, data, counter)

		#while next results are available
		while ('search_metadata' in jsonResponse and 'next_results' in jsonResponse['search_metadata'] and counter <= cap):
			#get next response with new search URL
			searchUrl = 'https://api.twitter.com/1.1/search/tweets.json' + str(jsonResponse['search_metadata']['next_results']) + '&tweet_mode=extended&exclude_replies=true'
			resp, content = client.request(searchUrl, method="GET", body=b"", headers=None)

			stringResponse = content.decode("utf-8")
			jsonResponse = json.loads(stringResponse)

			#analyze next batch
			counter = analyzeJSON(classifier, jsonResponse, data, counter)

		#if twitter didn't return statuses, return
		if (not('search_metadata' in jsonResponse)):
			print("--------------START ERROR--------------")
			print("Twitter rate limites reached - wait 15 minutes and try again")
			print(jsonResponse)
			print("--------------END ERROR--------------")
			sys.stdout.flush()
			#still have some results - return those
			data["error"] = "Twitter rate limites were reached - there may be incomplete data"
			return data

		return data;

'''
Function used to create base histogram
Params:
	data - analyzed data from Twitter search

Returns:
	graph - HTML for graph created by plotly

'''
def plotBaseData(data):
	#set data for chart
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
	#set colors/fonts/titles for chart
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
	#create figure and graph
	figure = go.Figure(data = data, layout = layout)
	graph = pltly.plot(figure, output_type='div')

	#remove mod bar and plotly link
	graph = graph.replace('displayModeBar:"hover"', 'displayModeBar:false')
	graph = graph.replace('"showLink": true', '"showLink": false')

	return graph;

'''
Function used to create time zone pie chart
Params:
	data - analyzed data from Twitter search

Returns:
	graph - HTML for graph created by plotly

'''
def plotTzPie(data):
	#remove none type time zones
	if None in data["timezones"]: del data["timezones"][None]

	#set data for chart
	data = [go.Pie(
				labels=data["timezones"].keys(),
				values=data["timezones"].values(),
				textinfo='none'
			)]

	#set colors/fonts/titles for chart
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
	#create figure and graph
	figure = go.Figure(data = data, layout = layout)
	graph = pltly.plot(figure, output_type='div')

	#remove mod bar and plotly link
	graph = graph.replace('displayModeBar:"hover"', 'displayModeBar:false')
	graph = graph.replace('"showLink": true', '"showLink": false')

	return graph;

'''
Function used to create time zone bar graph
Params:
	data - analyzed data from Twitter search

Returns:
	graph - HTML for graph created by plotly

'''
def plotTzBar(data):
	#delete none type time zones
	if None in data["timezones_sentiment"]: del data["timezones_sentiment"][None]

	#get the data for bar chart
	data = [go.Bar(
				x=data["timezones_sentiment"].keys(),
				y=data["timezones_sentiment"].values()
			)]

	#set colors/fonts/titles for chart
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
	#create figure and graph
	figure = go.Figure(data = data, layout = layout)
	graph = pltly.plot(figure, output_type='div')
	#remove mod bar and plotly link
	graph = graph.replace('displayModeBar:"hover"', 'displayModeBar:false')
	graph = graph.replace('"showLink": true', '"showLink": false')

	return graph;

'''
Function used to load charts and data into web template
Params:
	request - GET request

Returns:
	HttpResponse - response to be served

'''
def load_charts(request):
	try:
		#get job and check status for fnish;failed - wait if is not
		job = Job.fetch(request.session['job-id'], connection=connection)

		while (job.status != "finished" and job.status != "failed"):
			time.sleep(0.1)

		#if failed, tell user something went wrong
		if (job.status == "failed"):
			return HttpResponse("Something went wrong - most likely Redis is full. Wait 30 seconds and try returning to the homepage.", content_type='text/plain')

		#get the job data
		data = job.result

		#if failed, this means Twitter responded with error - tell user
		if ("failed" in data):
			return HttpResponse(data["failed"], content_type='text/plain')

		#if error, tell user
		if ("error" in data):
			pageData = {'error': data["error"], 'graph': plotBaseData(data), 'tzGraph':plotTzPie(data), 'tsGraph':plotTzBar(data), 'items': data["items"], 'median': np.median(data["sentiments"]), 'mean': np.mean(data["sentiments"])}
		#otehrwise send nornal page data
		else:
			pageData = {'graph': plotBaseData(data), 'tzGraph':plotTzPie(data), 'tsGraph':plotTzBar(data), 'items': data["items"], 'median': np.median(data["sentiments"]), 'mean': np.mean(data["sentiments"])}


		#serve the charts page with data dictionary
		return HttpResponse(render(request, 'charts.html', pageData, content_type='application/html'))

	except Exception as e:
		print("--------------START ERROR--------------")
		print(e)
		print("--------------END ERROR--------------")
		sys.stdout.flush()
		return redirect('/')

'''
Function used to check status of the current job
Params:
	request - GET request

Returns:
	job.status - status of the worker job

'''
def check_status(request):
	try:
		#get job id and check status - send to user
		job = Job.fetch(request.session['job-id'], connection=connection)
		return HttpResponse(job.status, content_type='text/plain')

	except Exception as e:
		print("--------------START ERROR--------------")
		print(e)
		print("--------------END ERROR--------------")
		sys.stdout.flush()
		return redirect('/')

'''
Function used to serve the methods page
Params:
	request - GET request

Returns:
	HttpResponse - response to be served

'''
def methods(request):
	return HttpResponse(render(request, 'methods.html', content_type='application/html'))

'''
Function used to serve the index and start the worker
Params:
	request - GET request

Returns:
	HttpResponse - response to be served

'''
def index(request):
	try:
		try:
			#get tweet cap
			cap = int(request.GET.get("cap"))
		except Exception as e:
			#set tweet cap as default
			cap = 500

		#queue the worker to get Twitter data and analyze
		job = django_rq.enqueue(getTwitterData, cap, timeout=600, result_ttl=30)
		#store job id to ref later
		request.session['job-id'] = job.id

		return HttpResponse(render(request, 'index.html', content_type='application/html'))

	except Exception as e:
		print("--------------START ERROR--------------")
		print(e)
		print("--------------END ERROR--------------")
		sys.stdout.flush()
		return HttpResponse("Too many requests - try again in a few seconds.", content_type='text/plain')

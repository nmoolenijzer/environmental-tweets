#------------------------------------------------------------------------------
# Imports
#   -all library/module imports go here-
import oauth2
import json
import random
import nltk
from nltk.corpus import names
from nltk.corpus import pros_cons
from django.shortcuts import render
from django.http import HttpResponse

def analyzeJSON(classifier, jsonResponse, items, counter):
	for obj in jsonResponse['statuses']:
		total = 0
		tokens = nltk.word_tokenize(obj['full_text'])
		pos = nltk.pos_tag(tokens)
		words_to_analyze = []
		for (word, tag) in pos:
			if ("JJ" in tag or "RB" in tag) and (not("@" in tag)):
				words_to_analyze.append(word)
		for word in words_to_analyze:
			classification = classifier.classify({ 'word': word })
			score = classifier.prob_classify({ 'word': word }).prob(classification)
			if (classification == "pro"):
				total += (score*100)
			else:
				total -= (score*100)
		avg = 0;
		if len(words_to_analyze) != 0: avg = total/float(len(words_to_analyze))

		items.append({ 'name': obj['user']['name'], 'text': obj['full_text'], 'avg': avg, 'count': counter })

		counter += 1

	return counter

def index(request):
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
	resp, content = client.request( 'https://api.twitter.com/1.1/search/tweets.json?q=%40EPA%20-filter%3Aretweets&result_type=recent&count=100&tweet_mode=extended&exclude_replies=true', method="GET", body=b"", headers=None )

	stringResponse = content.decode("utf-8")
	jsonResponse = json.loads(stringResponse)

	counter = 1;
	items = [];

	counter = analyzeJSON(classifier, jsonResponse, items, counter)

	while ('next_results' in jsonResponse['search_metadata'] and counter < 102):
		resp, content = client.request( 'https://api.twitter.com/1.1/search/tweets.json' + str(jsonResponse['search_metadata']['next_results']) + '&tweet_mode=extended&exclude_replies=true', method="GET", body=b"", headers=None )

		stringResponse = content.decode("utf-8")
		jsonResponse = json.loads(stringResponse)

		counter = analyzeJSON(classifier, jsonResponse, items, counter)

    # print("\nConfidence can also be analyzed:")
    # print(nltk.classify.accuracy(classifier, tester));
	#
    # print("\nAnd which training data is most important:")
    # print(classifier.show_most_informative_features(5));

	return HttpResponse(render(request, 'index.html', {'items': items}, content_type='application/html'))

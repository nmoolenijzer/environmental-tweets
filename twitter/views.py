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

def index(request):
	# -you main code starts here-


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
	classifier = nltk.NaiveBayesClassifier.train(trainer)



	consumer = oauth2.Consumer(key='eBa29YaUmi43aCmN9dDjKaTIN', secret='AZOkA4JVCgmE7NJURB3jQWjIQlG5aF6oQAfKX4JFwpncHYAjpP')
	token = oauth2.Token(key='827224004347977735-cq8ZzwvQMZIMvPS8ANwZ5Cq8OS3rKvy', secret='bctJjCgxtqsfMcCToRvSzOOZBVRZeIwZkP1ij34y49qMR')
	client = oauth2.Client(consumer, token)
	resp, content = client.request( 'https://api.twitter.com/1.1/search/tweets.json?q=%40EPA%20-filter%3Aretweets&result_type=recent&count=100&tweet_mode=extended&exclude_replies=true', method="GET", body=b"", headers=None )

	stringVal = content.decode("utf-8")
	jsonObj = json.loads(stringVal)

	counter = 1;
	currDate = 0;
	printVal = "<link href=\"https://fonts.googleapis.com/css?family=Raleway:200\" rel=\"stylesheet\">"
	printVal += "<div style='font-weight: 200; font-family: sans-serif; background-color: white; top: 0; left: 0; position: absolute; width: 100%; height: 100%'>"
	printVal += "<h1 style='font-weight: 200; font-family: sans-serif; text-align: center;'>Sentiment Analysis of Environmental Twitter Activity</h1>"
	printVal += "<table style='margin-left: auto; margin-right: auto; color: #031634; border-collapse: collapse;'>";
	print(resp)
	for obj in jsonObj['statuses']:
		total = 0
		tokens = nltk.word_tokenize(obj['full_text'])
		pos = nltk.pos_tag(tokens)
		words_to_analyze = []
		for (word, tag) in pos:
			if "JJ" in tag or "RB" in tag:
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
		printVal += "<tr><td style='border: 1px solid #031634; padding: 10px;'>" + str(counter) + "</td><td style='border: 1px solid #031634; padding: 10px;'>" + obj['user']['name'].encode('utf-8') + "</td><td style='border: 1px solid #031634; padding: 10px;'>" + obj['full_text'].encode('utf-8') + "</td><td style='border: 1px solid #031634; padding: 10px;'>" + str(total) + "</td></tr>"
		# printVal += "<br />"
		# prevDate = currDate
		# currDate = parse(obj['created_at'])
		# print(prevDate)
		# print(currDate)
		# print(relativedelta(prevDate, currDate))
		# stringVal += '\n'
		counter += 1

	print(str(jsonObj['search_metadata']))

	while ('next_results' in jsonObj['search_metadata'] and counter < 102):
		resp, content = client.request( 'https://api.twitter.com/1.1/search/tweets.json' + str(jsonObj['search_metadata']['next_results']) + '&tweet_mode=extended&exclude_replies=true', method="GET", body=b"", headers=None )

		stringVal = content.decode("utf-8")
		jsonObj = json.loads(stringVal)

		for obj in jsonObj['statuses']:
			total = 0
			tokens = nltk.word_tokenize(obj['full_text'])
			pos = nltk.pos_tag(tokens)
			words_to_analyze = []
			for (word, tag) in pos:
				if "JJ" in tag or "RB" in tag:
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
			printVal += "<tr><td style='border: 1px solid #031634; padding: 10px;'>" + str(counter) + "</td><td style='border: 1px solid #031634; padding: 10px;'>" + obj['user']['name'].encode('utf-8') + "</td><td style='border: 1px solid #031634; padding: 10px;'>" + obj['full_text'].encode('utf-8') + "</td><td style='border: 1px solid #031634; padding: 10px;'>" + str(total) + "</td></tr>"
			# printVal += "<br />"
			# prevDate = currDate
			# currDate = parse(obj['created_at'])
			# print(prevDate)
			# print(currDate)
			# print(relativedelta(prevDate, currDate))
			# stringVal += '\n'
			counter += 1

	printVal += "</table></div>"

    # print("\nThe classifier is often right:")
	print("The word 'good' is most likely: " + classifier.classify({ 'word': 'good' }))
    # print("The word 'bad' is most likely: " + classifier.classify({ 'word': 'bad' }))
    # print("The word 'amazing' is most likely: " + classifier.classify({ 'word': 'amazing' }))
    # print("The word 'terrible' is most likely: " + classifier.classify({ 'word': 'terrible' }))
    # print("The word 'horrible' is most likely: " + classifier.classify({ 'word': 'horrible' }))
    # print("The word 'great' is most likely: " + classifier.classify({ 'word': 'great' }))
	#
    # print("\nConfidence can also be analyzed:")
    # print(nltk.classify.accuracy(classifier, tester));
	#
    # print("\nAnd which training data is most important:")
    # print(classifier.show_most_informative_features(5));

	# print("count: " + str(counter))
	return HttpResponse(printVal)

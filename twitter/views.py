from django.shortcuts import render
from django.http import HttpResponse

#------------------------------------------------------------------------------
# Imports
#   -all library/module imports go here-
import oauth2
import json

def index(request):
	# -you main code starts here-
	consumer = oauth2.Consumer(key='eBa29YaUmi43aCmN9dDjKaTIN', secret='AZOkA4JVCgmE7NJURB3jQWjIQlG5aF6oQAfKX4JFwpncHYAjpP')
	token = oauth2.Token(key='827224004347977735-cq8ZzwvQMZIMvPS8ANwZ5Cq8OS3rKvy', secret='bctJjCgxtqsfMcCToRvSzOOZBVRZeIwZkP1ij34y49qMR')
	client = oauth2.Client(consumer, token)
	resp, content = client.request( 'https://api.twitter.com/1.1/search/tweets.json?q=%40EPA%20-filter%3Aretweets&result_type=recent&count=100&tweet_mode=extended&exclude_replies=true', method="GET", body=b"", headers=None )

	stringVal = content.decode("utf-8")
	jsonObj = json.loads(stringVal)

	counter = 0;
	currDate = 0;
	printVal = "";
	for obj in jsonObj['statuses']:
		printVal += obj['user']['name'].encode('utf-8') + ":" + obj['full_text'].encode('utf-8')
		printVal += "<br />"
		# prevDate = currDate
		# currDate = parse(obj['created_at'])
		# print(prevDate)
		# print(currDate)
		# print(relativedelta(prevDate, currDate))
		# stringVal += '\n'
		# counter += 1

	# print(jsonObj['search_metadata'])
	# print("count: " + str(counter))
	return HttpResponse(printVal)

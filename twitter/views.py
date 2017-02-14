#------------------------------------------------------------------------------
# Imports
#   -all library/module imports go here-
import oauth2
import json
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
	# -you main code starts here-
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
	for obj in jsonObj['statuses']:
		printVal += "<tr><td style='border: 1px solid #031634; padding: 10px;'>" + str(counter) + "</td><td style='border: 1px solid #031634; padding: 10px;'>" + obj['user']['name'].encode('utf-8') + "</td><td style='border: 1px solid #031634; padding: 10px;'>" + obj['full_text'].encode('utf-8') + "</td></tr>"
		# printVal += "<br />"
		# prevDate = currDate
		# currDate = parse(obj['created_at'])
		# print(prevDate)
		# print(currDate)
		# print(relativedelta(prevDate, currDate))
		# stringVal += '\n'
		counter += 1

	printVal += "</table></div>"
	# print(jsonObj['search_metadata'])
	# print("count: " + str(counter))
	return HttpResponse(printVal)

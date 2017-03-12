# Snapshots of Environmental Twitter Activity
## Overview
Visit the website here: [environmental-twitter.herokuapp.com](https://environmental-twitter.herokuapp.com/)

## Background
Since the inauguration of Donald Trump as the 45th President of the United States, the EPA has faced severe funding cuts and deregulation. One of the biggest centers of community response has been on Twitter, where many users have expressed their outrage - and some their praise - over the recent changes to environmental protection in the US. To capture this well of public opinion, I poll Twitter data and perform sentiment analysis on it in order to better understand how the public feels about the EPA at a given time. The site does not track or store data over long periods, but rather looks at a quick snapshot of Twitter activity that is captured on every page load. I do not argue that this provides context long term trend analysis, but rather that it allows users to get insight into how the public feels about the EPA in the instant that they load the site.

## Methods
In a general sense, the website will read current Tweets about the EPA (any recent tweets that tags @EPA) and will perform sentiment analysis on those tweets, searching for positive or negative sentiment. The results are then graphed in various charts that look at tweet counts, retweet counts, and break down sentiment by timezone.

Learn more about my methods here: [methods](https://environmental-twitter.herokuapp.com/methods/)

## Input Data
The input for the analysis is a JSON object that is returned by the Twitter REST APIs. I focus on the following attributes in the input data:
- jsonResponse['statuses'] - this contains all the tweet objects that were returned in the latest search
- tweet['full_text'] - this extracts the full text of the current status
- tweet['user']['name'] - gives the username of the person who tweeted the current status
- tweet['user']['time_zone'] - gives the timezone of the user
- tweet['retweet_count'] - the retweet count of the current tweet (how many times other users have retweeted it)
- tweet['created_at'] - gives the date and time the tweet was posted

## Output Data
The data that I plot is broken into the following segments:
- data["sentiments"] - the sentiment total of each tweet
- data["items"] - the raw tweet data (e.g. username, text, etc.)
- data["retweets"] - the sentiment totals weighted by retweet count (see methodology above)
- data["timezones"] - the count of tweets from each timezone
- data["timezones_sentiment"] - the overall sentiment at each timezone

## Display of Data
Finally, I display the data using two histograms (sentiment count from tweets themselves, and sentiment count from retweets), a pie chart (timezone distribution), and a bar chart (the overall sentiment from each timezone)

## Deploying
To deploy the website, I simply push updated files to this repo, which automatically deploys to Heroku. If the app crashes, let me know and I can restart the dynos.

## Author
This web app was created by Nick Moolenijzer (nick@moolenijzer.com) - contact me with any questions!

## Architecture
- [Django](https://www.djangoproject.com/) - used Django framework to serve and render HTML files with output from Python data analysis
- [Heroku](http://heroku.com) - builds and hosts the web app
- [Redis To Go](https://elements.heroku.com/addons/redistogo) - Heroku add-on for simple Redis implementation

## Libraries
- [python-oauth2](https://github.com/joestump/python-oauth2) - utilized to authorize GET requests using Twitter auth tokens
- [Natural Language Toolkit](http://www.nltk.org/) - necessary tools for analyzing tweets for sentiment (e.g. tokenizing, POS analysis, classifying)
- [plotly](https://plot.ly/) - used to plot the results of text analysis
- [NumPy](http://www.numpy.org/) - helps with various calculations and scientific analysis
- [Django-RQ](https://github.com/ui/django-rq) - provides framework for background workers to analyze Twitter data off the web dyno
- [Redis](https://redis.io/) - provides back-end for RQ background workers/queueing

## APIs
- [Twitter REST APIs](https://dev.twitter.com/rest/public) - allows for programmatic search of Twitter activity

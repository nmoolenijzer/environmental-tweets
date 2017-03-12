# Snapshots of Environmental Twitter Activity
## Overview
Visit the website here: [environmental-twitter.herokuapp.com](https://environmental-twitter.herokuapp.com/)

The default tweet cap is set at 500 tweets so that the Twitter rate limit doesn't quickly block using the website. If you would like to increase the cap, change the text box next to the reload button to a higher number (must be multiple of 100). Twitter may still return fewer tweets if there aren't enough available or if the rate limit is reached. Increase the cap at your own risk.

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
- data["dates"] - the dates of each tweet
- data["retweets"] - the sentiment totals weighted by retweet count (see methodology above)
- data["timezones"] - the count of tweets from each timezone
- data["timezones_sentiment"] - the overall sentiment at each timezone

## Display of Data
I display the data using two histograms (sentiment count from tweets themselves, and sentiment count from retweets), a pie chart (timezone distribution), and a bar chart (the overall sentiment from each timezone)

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

## Assets
- [Google Material Icons](https://material.io/icons/) - icons for web use

## License
All of my written code is licensed under the MIT License open source license, but all libraries, data, and external resources may have their own licenses that must be followed.

## Sources, Tutorials, and Helpful References
Bird, Steven, Ewan Klein, and Edward Loper. Natural Language Processing with Python. Beijing: O'Reilly, 2009. <http://www.nltk.org/book_1ed/>.

Kantrowitz, Mark, and Bill Ross. "Names Corpus." N.p., 29 Mar. 1994. Web. 30 Jan. 2017. <http://www-2.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/nlp/corpora/names/>.

Liu, Bing. "Pros and Cons." N.p., 2008. Web. <https://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html#datasets>.

Loper, Edward. "Source Code for Nltk.classify.naivebayes." Nltk.classify.naivebayes — NLTK 3.0 Documentation. N.p., n.d. Web. 30 Jan. 2017.

NLTK. "Classifiers." Classifiers. N.p., n.d. Web. 30 Jan. 2017.

NLTK. "Natural Language Toolkit." Natural Language Toolkit — NLTK 3.0 Documentation. N.p., n.d. Web. 30 Jan. 2017.

NLTK. "Nltk Package." Nltk Package — NLTK 3.0 Documentation. N.p., n.d. Web. 30 Jan. 2017.

NLTK. "Nltk.classify Package." Nltk.classify Package — NLTK 3.0 Documentation. N.p., n.d. Web. 30 Jan. 2017.

Perkins, Jacob. "Python NLTK Demos for Natural Language Text Processing." Python NLTK Demos for Natural Language Text Processing and NLP. N.p., n.d. Web. 30 Jan. 2017.

Poole, David, and Alan Mackworth. "Artificial Intelligence." Artificial Intelligence - Foundations of Computational Agents -- 7.3.3 Bayesian Classifiers. N.p., 2010. Web. 30 Jan. 2017

5. Categorizing and Tagging Words. (n.d.). Retrieved March 12, 2017, from http://www.nltk.org/book/ch05.html

Asynchronous tasks and jobs in Django with RQ | en.proft.me. (n.d.). Retrieved March 11, 2017, from http://en.proft.me/2016/10/4/asynchronous-tasks-and-jobs-django-rq/

Background Tasks in Python with RQ | Heroku Dev Center. (n.d.). Retrieved March 7, 2017, from https://devcenter.heroku.com/articles/python-rq

Coolors. (n.d.). Retrieved March 11, 2017, from https://coolors.co/9f7e69-d2bba0-f2efc7-f7ffe0-ffeee2

Deploying Python and Django Apps on Heroku | Heroku Dev Center. (n.d.). Retrieved February 16, 2017, from https://devcenter.heroku.com/articles/deploying-python

django - Connection refused for Redis on Heroku - Stack Overflow. (n.d.). Retrieved March 11, 2017, from http://stackoverflow.com/questions/11813470/connection-refused-for-redis-on-heroku

GET search/tweets — Twitter Developers. (n.d.). Retrieved March 9, 2017, from https://dev.twitter.com/rest/reference/get/search/tweets

Google Fonts. (n.d.). Retrieved March 8, 2017, from https://fonts.google.com/

Heroku Redis | Heroku Dev Center. (n.d.). Retrieved March 11, 2017, from https://devcenter.heroku.com/articles/heroku-redis#connecting-in-python

Histograms. (n.d.). Retrieved March 11, 2017, from https://plot.ly/python/histograms/

How to use sessions | Django documentation | Django. (n.d.). Retrieved March 11, 2017, from https://docs.djangoproject.com/en/1.10/topics/http/sessions/

HTTP GET request in JavaScript? - Stack Overflow. (n.d.). Retrieved March 11, 2017, from http://stackoverflow.com/questions/247483/http-get-request-in-javascript

javascript - What’s the easiest way to call a function every 5 seconds in jQuery? - Stack Overflow. (n.d.). Retrieved March 11, 2017, from
http://stackoverflow.com/questions/2170923/whats-the-easiest-way-to-call-a-function-every-5-seconds-in-jquery

joestump/python-oauth2. (n.d.). Retrieved March 12, 2017, from https://github.com/joestump/python-oauth2

joestump/python-oauth2: A fully tested, abstract interface to creating OAuth clients and servers. (n.d.). Retrieved February 16, 2017, from https://github.com/joestump/python-oauth2

Managing static files (e.g. images, JavaScript, CSS) | Django documentation | Django. (n.d.). Retrieved February 16, 2017, from https://docs.djangoproject.com/en/1.10/howto/static-files/

Material icons - Material Design. (n.d.). Retrieved March 12, 2017, from https://material.io/icons/

Natural Language Toolkit — NLTK 3.0 documentation. (n.d.). Retrieved March 12, 2017, from http://www.nltk.org/

NumPy — NumPy. (n.d.). Retrieved March 12, 2017, from http://www.numpy.org/

Personal apps | Heroku. (n.d.). Retrieved March 12, 2017, from https://dashboard.heroku.com/apps

Pie Charts. (n.d.). Retrieved March 11, 2017, from https://plot.ly/python/pie-charts/

pyplot — Matplotlib 2.0.0 documentation. (n.d.). Retrieved March 8, 2017, from http://matplotlib.org/api/pyplot_api.html

python - Adding config modes to Plotly.Py offline - modebar - Stack Overflow. (n.d.). Retrieved March 9, 2017, from
http://stackoverflow.com/questions/36554705/adding-config-modes-to-plotly-py-offline-modebar

python - Embedding a Plotly chart in a Django template - Stack Overflow. (n.d.). Retrieved March 9, 2017, from
http://stackoverflow.com/questions/36846395/embedding-a-plotly-chart-in-a-django-template

python - Flask: passing around background worker job (rq, redis) - Stack Overflow. (n.d.). Retrieved March 11, 2017, from
http://stackoverflow.com/questions/12162021/flask-passing-around-background-worker-job-rq-redis

Python: How to get job result by RQ - Stack Overflow. (n.d.). Retrieved March 11, 2017, from http://stackoverflow.com/questions/22776924/python-how-to-get-job-result-by-rq

Redis. (n.d.). Retrieved March 12, 2017, from https://redis.io/

redis - How to get Job by id in RQ python? - Stack Overflow. (n.d.). Retrieved March 11, 2017, from http://stackoverflow.com/questions/15181630/how-to-get-job-by-id-in-rq-python

Redis: OOM command not allowed when used memory > “maxmemory.” (2016, May 16). Retrieved from https://ma.ttias.be/redis-oom-command-not-allowed-used-memory-maxmemory/

Redis To Go - Add-ons - Heroku Elements. (n.d.). Retrieved March 12, 2017, from https://elements.heroku.com/addons/redistogo

REST APIs — Twitter Developers. (n.d.). Retrieved February 16, 2017, from https://dev.twitter.com/rest/public

RQ: Simple job queues for Python. (n.d.). Retrieved March 11, 2017, from http://python-rq.org/

Simple Job Queues with django_rq | Imaginary Landscape. (n.d.). Retrieved March 11, 2017, from https://www.imagescape.com/blog/2013/06/13/simple-job-queues-django_rq/

Single-user OAuth with Examples — Twitter Developers. (n.d.). Retrieved February 16, 2017, from https://dev.twitter.com/oauth/overview/single-user

Smistad, E. (n.d.). Making charts and output them as images to the browser in Django – Erik Smistad. Retrieved from
https://www.eriksmistad.no/making-charts-and-outputing-them-as-images-to-the-browser-in-django/

Stack Overflow. (n.d.). Retrieved March 7, 2017, from http://stackoverflow.com/

Street, A. (n.d.). Using redis-queue for asynchronous calls with Django. Retrieved from http://racingtadpole.com/blog/redis-queue-with-django/

The Web framework for perfectionists with deadlines | Django. (n.d.). Retrieved March 12, 2017, from https://www.djangoproject.com/

Thumbnail gallery — Matplotlib 2.0.0 documentation. (n.d.). Retrieved March 7, 2017, from http://matplotlib.org/gallery.html

ui/django-rq. (n.d.). Retrieved March 12, 2017, from https://github.com/ui/django-rq

Visualize Data, Together. (n.d.). Retrieved March 12, 2017, from https://plot.ly/

Worldvectorlogo — Brand logos free to download. (n.d.). Retrieved March 7, 2017, from https://worldvectorlogo.com/

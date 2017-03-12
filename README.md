# Snapshots of Environmental Twitter Activity
## Overview
Visit the website here: [environmental-twitter.herokuapp.com](https://environmental-twitter.herokuapp.com/)

## Background
Since the inauguration of Donald Trump as the 45th President of the United States, the EPA has faced severe funding cuts and deregulation. One of the biggest centers of community response has been on Twitter, where many users have expressed their outrage - and some their praise - over the recent changes to environmental protection in the US. To capture this well of public opinion, I poll Twitter data and perform sentiment analysis on it in order to better understand how the public feels about the EPA at a given time. The site does not track or store data over long periods, but rather looks at a quick snapshot of Twitter activity that is captured on every page load. I do not argue that this provides context long term trend analysis, but rather that it allows users to get insight into how the public feels about the EPA in the instant that they load the site.

## Methods
Learn more about my methods here: [methods](https://environmental-twitter.herokuapp.com/methods/)

## Deploying
To deploy the website, I simply push updated files to this repo, which automatically deploys to Heroku. If the app crashes, let me know and I can restart the dynos.

## Author
This web app was created by Nick Moolenijzer (nick@moolenijzer.com) - contact me with any questions!

## Architecture/Libraries/APIs
- [Django](https://www.djangoproject.com/)
- [Heroku](http://heroku.com)
- [python-oauth2](https://github.com/joestump/python-oauth2)
- [Twitter REST APIs](https://dev.twitter.com/rest/public)
- [Django-RQ](https://github.com/ui/django-rq)
- [Natural Language Toolkit](http://www.nltk.org/)
- [plotly](https://plot.ly/)
- [NumPy](http://www.numpy.org/)
- [redis](https://redis.io/)

web: gunicorn environmentaltweets.wsgi --log-file=-
worker: python manage.py rqworker high default low

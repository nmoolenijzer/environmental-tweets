from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^update_charts/$', views.update_charts, name='update_charts'),
	url(r'^check_status/$', views.check_status, name='check_status'),
    # url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root', setttings.STATIC_ROOT })
]

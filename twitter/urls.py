from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^show_chart/$', views.show_chart, name='show_chart'),
    # url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root', setttings.STATIC_ROOT })
]

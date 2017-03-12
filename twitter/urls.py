from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^load_charts/$', views.load_charts, name='load_charts'),
	url(r'^methods/$', views.methods, name='methods'),
	url(r'^check_status/$', views.check_status, name='check_status'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

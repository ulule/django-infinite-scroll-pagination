from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^page/$', views.pagination_ajax, name='pagination-ajax'),
    url(r'^page/(?P<pk>\d+)/$', views.pagination_ajax, name='pagination-ajax'),
]

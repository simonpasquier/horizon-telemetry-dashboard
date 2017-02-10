from django.conf.urls import patterns, url
from .views import ProjectOverview, ProxyView

urlpatterns = patterns(
    '',
    url(r'^proxy/', ProxyView.as_view(), name='proxy'),
    url(r'^$', ProjectOverview.as_view(), name='index'),
)

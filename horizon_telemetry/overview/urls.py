
from django.conf.urls import patterns, url
from .views import ProjectOverview, DataView
from horizon_telemetry.utils.graphite_proxy import graphite_render

urlpatterns = patterns('',
                       url(r'^data$', DataView.as_view(), name='data'),
                       url(r'^$', ProjectOverview.as_view(), name='index'),
                       url(r'^render/', graphite_render, name='render_graphite'),
                       )

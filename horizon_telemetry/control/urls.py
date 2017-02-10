
from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from . import views


urlpatterns = patterns(
    'horizon_telemetry.control.views',
    url(r'^(?P<hypervisor>.*)/data$', views.DataView.as_view(), name='data'),
    url(r'^(?P<hypervisor>[^/]+)/detail$',
        views.AdminDetailView.as_view(),
        name='detail'),
    url(r'^$', views.AdminIndexView.as_view(), name='index')
)


from django.conf.urls import patterns
from django.conf.urls import url

from horizon_telemetry.views import ProjectDataView, ProjectGraphView
from openstack_dashboard.dashboards.project.overview.views import WarningView

urlpatterns = patterns('telemetry_dashboard.views',
                       url(r'^graphs$', ProjectGraphView.as_view(), name='graphs'),
                       url(r'^warning$', WarningView.as_view(), name='warning'),
                       )
#url(r'^data$', ProjectDataView.as_view(), name='data'),

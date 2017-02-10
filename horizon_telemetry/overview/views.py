
import datetime
import json
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.template.defaultfilters import capfirst, floatformat
from django.utils.translation import ugettext_lazy as _
# for data view can be deleted
from django.views.generic import TemplateView
from horizon import exceptions, forms
from horizon.utils import csvbase
# for data view can be deleted
from horizon_telemetry.utils import graphite_context
from horizon_telemetry.utils.graphite import get_instance_data
from openstack_dashboard import api, usage
from openstack_dashboard.dashboards.project.overview.views import \
    ProjectUsageCsvRenderer

from .tables import ProjectUsageTable


class ProjectOverview(usage.UsageView):
    table_class = ProjectUsageTable
    usage_class = usage.ProjectUsage
    template_name = 'telemetry/overview/index.html'
    csv_response_class = ProjectUsageCsvRenderer

    @graphite_context
    def get_context_data(self, *args, **kwargs):
        context = super(ProjectOverview, self).get_context_data(
            *args, **kwargs)

        return context

    def get_data(self):
        super(ProjectOverview, self).get_data()
        return self.usage.get_instances()


from horizon_telemetry.utils.graphite import get_instance_data


class DataView(TemplateView):
    template_name = 'telemetry/test.html'

    def get_usage_list(self, start, end):
        instances = []
        terminated_instances = []
        usage = api.nova.usage_get(self.request, self.project_id, start, end)
        # Attribute may not exist if there are no instances
        if hasattr(usage, 'server_usages'):
            for server_usage in usage.server_usages:
                # This is a way to phrase uptime in a way that is compatible
                # with the 'timesince' filter. (Use of local time intentional.)
                if server_usage['ended_at']:
                    terminated_instances.append(server_usage)
                else:
                    instances.append(server_usage)
        usage.server_usages = instances
        return (usage,)

    def get(self, *args, **kwargs):

        self.project_id = self.kwargs.get('project_id',
                                          self.request.user.tenant_id)

        today = datetime.now()
        instances = self.get_usage_list(today, datetime.now())

        data = []

        for instance in instances[0].to_dict()['server_usages']:
            instance.update({
                'cpu': get_instance_data(instance['instance_id'])
                })
            data.append(instance)

        return HttpResponse(json.dumps(data), content_type='application/json')

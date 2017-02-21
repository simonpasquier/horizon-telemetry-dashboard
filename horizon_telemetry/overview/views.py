import datetime
import json
from datetime import datetime

from django.conf import settings
from django.http import (HttpResponse,
                         HttpResponseBadRequest,
                         HttpResponseNotFound)
from django.template.defaultfilters import capfirst, floatformat
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from horizon import exceptions, forms
from horizon.utils import csvbase

from horizon_telemetry.utils import influxdb_client
from openstack_dashboard import api, usage
from openstack_dashboard.dashboards.project.overview.views import \
    ProjectUsageCsvRenderer

from .tables import ProjectUsageTable


class ProjectOverview(usage.UsageView):
    table_class = ProjectUsageTable
    usage_class = usage.ProjectUsage
    template_name = 'telemetry/overview/index.html'
    csv_response_class = ProjectUsageCsvRenderer

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectOverview, self).get_context_data(
            *args, **kwargs)
        return context

    def get_data(self):
        super(ProjectOverview, self).get_data()
        return self.usage.get_instances()


class ProxyView(TemplateView):
    """Proxy class to InfluxDB

    It translates requests from Cubism/D3 clients to InfluxDB queries and
    convert the datapoints to a compatible format (eg a list of values).
    """

    METRIC_PARAMETERS = {
        'virt_cpu_time': ['instance_id'],
        'virt_disk_octets_read': ['instance_id'],
        'virt_disk_octets_write': ['instance_id'],
        'virt_if_octets_rx': ['instance_id'],
        'virt_if_octets_tx': ['instance_id'],
    }

    def get(self, request, *args, **kwargs):
        for param in ('metric', 'start', 'end', 'interval'):
            if param not in request.GET:
                return HttpResponseBadRequest(
                    '{{"error":"{} parameter is required"}}'.format(param),
                    content_type='application/json')

        metric = request.GET.get('metric')
        start = request.GET.get('start')
        end = request.GET.get('end')
        interval = request.GET.get('interval')

        for parameter in self.METRIC_PARAMETERS.get(metric, []):
            if param not in request.GET:
                return HttpResponseBadRequest(
                    '{{"error":"{} parameter is required"}}'.format(param),
                    content_type='application/json')

        instance_id = request.GET.get('instance_id')
        if instance_id:
            try:
                api.nova.server_get(self.request, instance_id)
            except Exception:
                return HttpResponseNotFound(
                    '{{"error":"instance {} not found"}}'.format(instance_id),
                    content_type='application/json')

        where = ''
        group = ['time({}s)'.format(interval)]
        if metric == 'virt_cpu_time':
            select = 'mean("value") / 10000000 as value'
            where = '"instance_id" =~ /^{}$/'.format(instance_id)
        elif metric in ['virt_disk_octets_read', 'virt_disk_octets_write']:
            select = 'mean("value") as value'
            where = '"instance_id" =~ /^{}$/'.format(instance_id)
            group.append('device')
        elif metric in ['virt_if_octets_rx', 'virt_if_octets_tx']:
            select = 'mean("value") as value'
            where = '"instance_id" =~ /^{}$/'.format(instance_id)
            group.append('interface')
        else:
            return HttpResponseBadRequest(
                '{{"error":"{} metric is not supported"}}'.format(metric),
                content_type='application/json')

        where += ' AND environment_label =~ /^{}$/'.format(
            settings.ENVIRONMENT_LABEL)
        where += ' AND time >= {}s AND time <= {}s'.format(start, end)

        query = 'SELECT {select} FROM "{measurement}" WHERE {where} GROUP BY {group} fill(0)'.format(
            select=select,
            measurement=metric,
            where=where,
            group=','.join(group)
        )

        # sum datapoints from different series (eg InfluxDB tags) into a single
        # array
        data = []
        for i, serie in enumerate(influxdb_client.query(query)):
            for j, point in enumerate(serie):
                if i == 0:
                    data.append(point['value'])
                else:
                    data[j] += point['value']

        return HttpResponse(json.dumps(data), content_type='application/json')

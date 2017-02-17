import datetime
import json

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from horizon import exceptions, tables
from horizon_telemetry.forms import DateForm
from horizon_telemetry.utils.influxdb_client import (get_host_usage_metrics,
                                                     get_host_cpu_metric,
                                                     get_host_disk_metric,
                                                     get_host_memory_metric,
                                                     get_host_network_metric)
from openstack_dashboard import api


from . import tables as project_tables


class AdminIndexView(tables.DataTableView):
    table_class = project_tables.AdminHypervisorsTable
    template_name = 'telemetry/compute/index.html'

    def get_data(self):
        hypervisors = []
        try:
            hypervisors = api.nova.hypervisor_list(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve hypervisor information.'))

        return hypervisors

    def get_context_data(self, **kwargs):
        context = super(AdminIndexView, self).get_context_data(**kwargs)
        try:
            context["stats"] = api.nova.hypervisor_stats(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve hypervisor statistics.'))
        return context


class AdminDetailView(TemplateView):
    template_name = 'telemetry/compute/detail.html'

    def get_data(self):
        pass

    def get_context_data(self, **kwargs):
        context = super(AdminDetailView, self).get_context_data(**kwargs)

        today = datetime.date.today()
        date_range = {
            'start': self.request.GET.get("start", today - datetime.timedelta(1)),
            'end': self.request.GET.get('end', today)
        }
        form = DateForm(date_range)

        self.request.session.update(date_range)

        # convert inputs to date objects
        if not isinstance(date_range['start'], datetime.date):
            date_range['start'] = datetime.datetime.strptime(date_range['start'], "%Y-%m-%d").date()
            date_range['end'] = datetime.datetime.strptime(date_range['end'], "%Y-%m-%d").date()

        hour_interval = (date_range['end'] - date_range['start']).total_seconds() / 3600
        if hour_interval > 24:
            context['tickFormat'] = "%x"
        else:
            context['tickFormat'] = "%H:%M"

        context['dateform'] = form
        node = context['node'] = context['hypervisor']

        context['cpu_data'] = json.dumps(
            get_host_cpu_metric(settings.ENVIRONMENT_LABEL, node,
                                date_range['start'], date_range['end'])
        )
        context['mem_data'] = json.dumps(
            get_host_memory_metric(settings.ENVIRONMENT_LABEL, node,
                                   date_range['start'], date_range['end'])
        )
        context['hdd_data'] = json.dumps(
            get_host_disk_metric(settings.ENVIRONMENT_LABEL, node,
                                 date_range['start'], date_range['end'])
        )
        context['net_data'] = json.dumps(
            get_host_network_metric(settings.ENVIRONMENT_LABEL, node,
                                    date_range['start'], date_range['end'],
                                   getattr(settings, 'TELEMETRY_COMPUTE_INTERFACES', None))
        )

        return context


class DataView(TemplateView):
    template_name = 'telemetry/dummy.html'

    def get(self, *args, **kwargs):
        data = get_host_usage_metric(settings.ENVIRONMENT_LABEL,
                                     self.kwargs.get('hypervisor'))

        return HttpResponse(json.dumps(data), content_type='application/json')

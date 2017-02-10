import datetime
import json
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from horizon import exceptions, tables
from horizon_telemetry.forms import DateForm
from horizon_telemetry.utils import graphite_context
from horizon_telemetry.utils.graphite import (get_cpu_data,
                                              get_mem_data,
                                              get_hdd_data,
                                              get_ctl_net_data,
                                              get_hypervisor_data)
from openstack_dashboard import api

from . import tables as project_tables
from .utils import get_all_controllers


class AdminIndexView(tables.DataTableView):
    table_class = project_tables.AdminHypervisorsTable
    template_name = 'telemetry/control/index.html'

    def get_data(self):
        hypervisors = []
        try:
            hypervisors = get_all_controllers(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve control nodes informations.'))

        return hypervisors

    @graphite_context
    def get_context_data(self, **kwargs):
        context = super(AdminIndexView, self).get_context_data(**kwargs)
        try:
            context["stats"] = api.nova.hypervisor_stats(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve control nodes statistics.'))

        return context


class AdminDetailView(TemplateView):
    template_name = 'telemetry/control/detail.html'

    def get_data(self):
        pass

    @graphite_context
    def get_context_data(self, **kwargs):
        context = super(AdminDetailView, self).get_context_data(**kwargs)

        # NVD3 graph - date filter and graph data
        today = datetime.date.today()
        yesterday = datetime.date.today() - datetime.timedelta(1)

        cleaned_data = {
            'start': self.request.GET.get("start", yesterday),
            'end': self.request.GET.get('end', today)
        }
        form = DateForm(cleaned_data)

        self.request.session.update(cleaned_data)

        if not isinstance(cleaned_data['start'], datetime.date):
            cleaned_data['start'] = datetime.datetime.strptime(cleaned_data['start'], "%Y-%m-%d").date()
            cleaned_data['end'] = datetime.datetime.strptime(cleaned_data['end'], "%Y-%m-%d").date()

        timeDiff = cleaned_data['end'] - cleaned_data['start']
        timeDiff = timeDiff.total_seconds() / 3600

        if timeDiff > 24:
            context['tickFormat'] = "%x"
        else:
            context['tickFormat'] = "%H:%M"

        context['dateform'] = form

        controllers = get_all_controllers(self.request)
        node = context['hypervisor']

        context['node'] = node

        context['cpu_data'] = json.dumps(
            get_cpu_data(node, cleaned_data['start'], cleaned_data['end']
                         ))

        context['mem_data'] = json.dumps(
            get_mem_data(node, cleaned_data['start'], cleaned_data['end']
                         ))

        context['hdd_data'] = json.dumps(
            get_hdd_data(node, cleaned_data['start'], cleaned_data['end']
                         ))

        context['net_data'] = json.dumps(
            get_ctl_net_data(node, cleaned_data['start'], cleaned_data['end']
                             ))

        return context


from horizon_telemetry.utils.memoized import memoized

# thats all !
@memoized
def get_cached_data(id):
    """Called just once in one minute"""

    return get_hypervisor_data(id)


class DataView(TemplateView):
    """Load data for control nodes."""

    template_name = 'telemetry/dummy.html'

    def get(self, *args, **kwargs):

        hypervisors = get_all_controllers(self.request)

        id = self.kwargs.get('hypervisor')

        # this is evauluate data just once..
        print "Loading from %s" % id
        data = get_cached_data(id)
        print "Loaded from %s" % id

        return HttpResponse(json.dumps(data), content_type='application/json')

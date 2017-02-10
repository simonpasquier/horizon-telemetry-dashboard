
import datetime
from django.conf import settings
from django.template.defaultfilters import capfirst
from django.template.defaultfilters import floatformat
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from horizon import forms
from horizon import exceptions
from horizon.utils import csvbase

from openstack_dashboard import api
from openstack_dashboard import usage
from horizon_telemetry.utils import graphite_context
from openstack_dashboard.dashboards.project.overview.views \
    import ProjectUsageCsvRenderer

# for data view can be deleted
from django.views.generic import TemplateView
from django.http import HttpResponse
import json
import requests
from horizon_telemetry.utils.graphite import get_instance_data


def graphite_render(request, username=None):
    '''Just proxy for Graphite render method

    bind on /render*
    '''
    original_url = request.get_full_path()
    url = '%s%s' % (settings.GRAPHITE_ENDPOINT, original_url)

    # we don't want serialize data here
    response = requests.get(url).text

    return HttpResponse(response)


class ProjectDataView(TemplateView):
    template_name = 'telemetry/test.html'

    def get(self, *args, **kwargs):
        # maybe call graphite here not on the client
        instance_data = get_instance_data("4ffe5beb-c6f2-4e08-9306-4b5cc910abb7")

        data = {
            "series": [
                {
                    "name": "instance-00000005",
                    "data": [
                        {"y": 160, "x": "2013-08-21T11:21:25"},
                        {"y": 181, "x": "2013-08-21T11:22:25"},
                        {"y": 191, "x": "2013-08-21T11:23:25"}
                    ]
                }, {
                    "name": "instance-00000005",
                    "data": [
                        {"y": 141, "x": "2013-08-21T11:23:25"},
                        {"y": 160, "x": "2013-08-21T11:00:25"}
                    ]
                }
            ],
            "settings": {
                'renderer': 'StaticAxes',
                'higlight_last_point': True,
                "auto_size": False,
                'auto_resize': True,
                "axes_x": False,
                "axes_y": False,
                'bar_chart_settings': {
                    'orientation': 'vertical',
                    'used_label_placement': 'left',
                    'width': 30,
                    'color_scale_domain': [0, 80, 80, 100],
                    'color_scale_range': ['#00FE00', '#00FF00', '#FE0000', '#FF0000'],
                    'average_color_scale_domain': [0, 100],
                    'average_color_scale_range': ['#0000FF', '#0000FF']
                }
            },
            "stats": {
                'average': 20,
                'used': 30,
                'tooltip_average': "tooltip_average"
            }
        }
        return HttpResponse(json.dumps(data), content_type='application/json')


class ProjectGraphView(TemplateView):
    template_name = 'telemetry/test.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectGraphView, self).get_context_data(
            *args, **kwargs)

        return context

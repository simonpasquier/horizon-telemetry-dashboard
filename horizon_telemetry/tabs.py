
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from .utils.views import graphite_context


class TelemetryTab(tabs.Tab):
    name = _("Telemetry")
    slug = "telemetry"
    template_name = ("telemetry/_instance_detail_telemetry.html")

    @graphite_context
    def get_context_data(self, request):
        return {
            "instance": self.tab_group.kwargs['instance']
        }

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

class TelemetryTab(tabs.Tab):
    name = _("Telemetry")
    slug = "telemetry"
    template_name = ("telemetry/_instance_detail_telemetry.html")

    def get_context_data(self, request):
        return {
            "instance": self.tab_group.kwargs['instance']
        }

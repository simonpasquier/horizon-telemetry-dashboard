
import horizon
from horizon_telemetry import dashboard
from django.utils.translation import ugettext as _


class OverviewPanel(horizon.Panel):
    name = _("Overview")
    slug = 'overview'

dashboard.Telemetry.register(OverviewPanel)

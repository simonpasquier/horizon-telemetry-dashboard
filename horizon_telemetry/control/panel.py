
from django.utils.translation import ugettext_lazy as _

import horizon
from horizon_telemetry import dashboard


class Control(horizon.Panel):
    name = _("Control nodes")
    slug = 'control'
    permissions = ('openstack.roles.admin',)


dashboard.Telemetry.register(Control)

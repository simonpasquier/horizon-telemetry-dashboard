
from django.utils.translation import ugettext_lazy as _

import horizon


class Telemetry(horizon.Dashboard):
    name = _("Telemetry")
    slug = "telemetry"
    panels = ('overview', 'compute', 'control')
    default_panel = 'overview'
    #permissions = ('openstack.roles.admin',)

horizon.register(Telemetry)

# ensure that overrides is applied when telemetry is used
try:
    from .overrides import *
except:
    pass

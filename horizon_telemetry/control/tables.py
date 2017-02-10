
from django.utils.translation import ugettext_lazy as _

from horizon import tables


class AdminHypervisorsTable(tables.DataTable):

    host = tables.Column("host",
                         link=("horizon:telemetry:control:detail"),
                         verbose_name=_("Host"))

    service = tables.Column("service",
                            verbose_name=_("Service"))

    def get_object_id(self, hypervisor):
        return hypervisor['host']

    class Meta:
        name = "hypervisors"
        verbose_name = _("Control Nodes Details")

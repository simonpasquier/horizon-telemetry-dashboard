from django.utils.translation import ugettext_lazy as _

from horizon import tables


class AdminHypervisorsTable(tables.DataTable):

    host = tables.Column("host",
                         link=("horizon:telemetry:control:detail"),
                         verbose_name=_("Host"))

    service = tables.Column("service",
                            verbose_name=_("Service"))

    def get_object_id(self, control_node):
        return control_node['host']

    class Meta:
        name = "control_nodes"
        verbose_name = _("Control Nodes Details")

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import tables

from django.utils.html import format_html


from horizon_telemetry.utils.tables import InstanceGraphColumn, InstanceGraphColumnTwoRow, GraphColumn


def link_detail(datum=None):

    return reverse(
        "horizon:project:instances:detail",
        kwargs={'instance_id': datum['instance_id']}) + '?tab=instance_details__telemetry'


class InstanceCPUGraphColumn(GraphColumn):

    def get_metric(self, datum):
        uuid = self.get_uuid(datum)
        return 'asPercent(sumSeries(default_prd.{0}.libvirt.virt_vcpu.*), default_prd.{0}.libvirt.virt_cpu_total)'.format(uuid)


class ProjectUsageTable(tables.DataTable):
    name = tables.Column(
        'name', verbose_name=_('Name'),
        link=link_detail,
        classes=['telemetry_name_column']
    )

    cpu_util = InstanceCPUGraphColumn(
        'cpu_util',
        verbose_name=_('CPU Utilisation'),
        graph_id="cpu_util"
    )

    network = InstanceGraphColumnTwoRow(
        'network',
        verbose_name=_('Net In/Out'),
        graph_id_first="network_in",
        graph_metric_first='libvirt.if_octets.*.rx',
        graph_id_second="network_out",
        graph_metric_second='libvirt.if_octets.*.tx'
    )

    storage_write = InstanceGraphColumnTwoRow(
        'storage',
        verbose_name=_('HDD Write/Read'),
        graph_id_first="storage_write",
        graph_metric_first='libvirt.disk_ops.*.write',
        graph_id_second="storage_read",
        graph_metric_second='libvirt.disk_ops.*.read'
    )

    def get_object_id(self, datum):
        return datum['instance_id']

    class Meta:
        name = "usage"
        verbose_name = _("Project Usage")

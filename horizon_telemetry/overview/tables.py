from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html

from horizon import tables
from horizon_telemetry.utils.tables import InstanceGraphColumn, InstanceGraphColumnTwoRow


def link_detail(datum=None):

    return reverse(
        "horizon:project:instances:detail",
        kwargs={'instance_id': datum['instance_id']}) + '?tab=instance_details__telemetry'


class ProjectUsageTable(tables.DataTable):
    name = tables.Column(
        'name',
        verbose_name=_('Name'),
        link=link_detail,
        classes=['telemetry_name_column']
    )

    cpu_util = InstanceGraphColumn(
        'cpu_util',
        verbose_name=_('CPU Utilization'),
        metric='virt_cpu_time'
    )

    network = InstanceGraphColumnTwoRow(
        'network',
        verbose_name=_('Net Rx/Tx'),
        metric="virt_if_octets_rx",
        second_metric="virt_if_octets_tx",
    )

    storage_write = InstanceGraphColumnTwoRow(
        'storage',
        verbose_name=_('Disk Write/Read'),
        metric="virt_disk_octets_write",
        second_metric="virt_disk_octets_read",
    )

    def get_object_id(self, datum):
        return datum['instance_id']

    class Meta:
        name = "usage"
        verbose_name = _("Project Usage")

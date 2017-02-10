
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon.templatetags import sizeformat


class AdminHypervisorsTable(tables.DataTable):
    hostname = tables.Column("hypervisor_hostname",
                             link=("horizon:telemetry:compute:detail"),
                             verbose_name=_("Hostname"))

    hypervisor_type = tables.Column("hypervisor_type",
                                    verbose_name=_("Type"))

    vcpus = tables.Column("vcpus",
                          verbose_name=_("VCPUs (total)"))

    vcpus_used = tables.Column("vcpus_used",
                               verbose_name=_("VCPUs (used)"))

    memory_mb = tables.Column('memory_mb',
                              verbose_name=_("RAM (total)"),
                              attrs={'data-type': 'size'},
                              filters=(sizeformat.mbformat,))

    memory_used = tables.Column('memory_mb_used',
                                verbose_name=_("RAM (used)"),
                                attrs={'data-type': 'size'},
                                filters=(sizeformat.mbformat,))

    local = tables.Column('local_gb',
                          verbose_name=_("Storage (total)"),
                          attrs={'data-type': 'size'},
                          filters=(sizeformat.diskgbformat,),)

    local_used = tables.Column('local_gb_used',
                               verbose_name=_("Storage (used)"),
                               attrs={'data-type': 'size'},
                               filters=(sizeformat.diskgbformat,))

    running_vms = tables.Column("running_vms",
                                verbose_name=_("Instances"))

    def get_object_id(self, hypervisor):
        return hypervisor.hypervisor_hostname

    class Meta:
        name = "hypervisors"
        verbose_name = _("Compute Nodes Details")

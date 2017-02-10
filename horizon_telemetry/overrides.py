

from horizon_telemetry.tabs import TelemetryTab
from openstack_dashboard.dashboards.project.instances.tabs import \
    InstanceDetailTabs

InstanceDetailTabs.tabs += (TelemetryTab,)

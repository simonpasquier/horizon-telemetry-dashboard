
from django.conf import settings
from horizon import exceptions
from horizon import tabs
from openstack_dashboard.api import cinder
from openstack_dashboard.api import heat
from openstack_dashboard.api import neutron
from openstack_dashboard.api import nova


def get_all_controllers(self):
    """returns control nodes from settings
    """
    _nodes = getattr(settings, 'OPENSTACK_CONTROL_NODES', {})
    nodes = []

    for _node, _service in _nodes.iteritems():
        node = {"host": _node, "service": _service}
        nodes.append(node)

    return sorted(nodes)

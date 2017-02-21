from django.conf import settings


def get_all_controllers(self):
    """returns control nodes from the settings
    """
    _nodes = getattr(settings, 'OPENSTACK_CONTROL_NODES', {})
    nodes = []

    for _node, _service in _nodes.iteritems():
        node = {"host": _node, "service": _service}
        nodes.append(node)

    return sorted(nodes)

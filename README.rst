========================
Horizon Telemetry Panels
========================

Simple Telemetry Dashboard for Horizon. Uses Cubism.js for ploting data from Graphite.


Settings
========


.. code-block:: python

    GRAPHITE_ENDPOINT = 'http://mygraphite.com:80'
    
    GRAPHITE_PREFIX = 'default_prd'

	AUTHENTICATION_URLS += ['horizon_telemetry.graphite_urls']


Optionaly you can specify Control Nodes mapping which is used for control panel where we don't know who is controller.

.. code-block:: python

    OPENSTACK_CONTROL_ZONE = 'internal'

    OPENSTACK_CONTROL_NODES = {
        'ctl01': 'ctl01.vpc.prd.tcp.cloudlab.cz'
    }


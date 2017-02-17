========================
Horizon Telemetry Panels
========================

A simple Telemetry Dashboard for Horizon showing metrics for virtual instances
and physical nodes. It uses Cubism.js and D3 for graphing the metrics and
relies on InfluxDB as the metric backend.

Settings
========

.. code-block:: python

    INFLUXDB_HOST = 'mtr.example.com'
    #INFLUXDB_PORT = '8086'
    INFLUXDB_USERNAME = 'horizon'
    INFLUXDB_PASSWORD = 'supersecret'
    INFLUXDB_DATABASE = 'lma'
    ENVIRONMENT_LABEL = 'default_prd'

You may also specify the servers which will be showed in the "Control Nodes" panel.

.. code-block:: python

    OPENSTACK_CONTROL_NODES = [
        'ctl01.example.com'
        'ctl02.example.com'
        'ctl03.example.com'
    ]

You may also specify the network interface(s) that should be graphed for the
compute nodes.

.. code-block:: python

    # For OpenContrail
    TELEMETRY_COMPUTE_INTERFACES = [
        'vhost0'
    ]

    # For OpenvSwitch
    TELEMETRY_COMPUTE_INTERFACES = [
        'br-mgmt', 'br-mesh'
    ]

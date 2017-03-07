import logging
import re

from django.conf import settings
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError


logger = logging.getLogger(__name__)
CLIENT = InfluxDBClient(
    settings.INFLUXDB_HOST,
    getattr(settings, 'INFLUXDB_PORT', '8086'),
    settings.INFLUXDB_USERNAME,
    settings.INFLUXDB_PASSWORD,
    settings.INFLUXDB_DATABASE,
    timeout=5
)


def _compute_group_by_interval(start, end):
    return "{}m".format(max(0, (end - start).days) * 10 + 10)


def _get_short_hostname(hostname):
    return re.sub(r'^([^.]+).*$', r'\1', hostname)


def _get_host_metric_query(measurement, start, end, environment, host,
                           where=None, group=None):
    return """select mean(value) as value from {measurement}
    where time >= '{start}' and time < '{end}' + 1d
    and environment_label = '{environment}'
    and hostname = '{host}' {where}
    group by time({interval}){group} fill(none)""".format(
        measurement=measurement,
        start=start.isoformat(),
        end=end.isoformat(),
        environment=environment,
        host=_get_short_hostname(host),
        interval=_compute_group_by_interval(start, end),
        where='and {}'.format(where) if where else '',
        group=',{}'.format(group) if group else '',
    )


def _get_first_value(result, measurement=None):
    return list(result.get_points(measurement))[0]['value']


def _sum_points(result, measurement=None):
    points = {}
    # get_points() returns all datapoints for the given measurement
    # irrespective of the tag(s)
    for point in result.get_points(measurement):
        if point['time'] not in points:
            points[point['time']] = 0
        points[point['time']] += point['value']
    return [[points[t], t] for t in sorted(points.keys())]


def query(query):
    '''Return the result of the InfluxDB query

    None if the query failed
    '''
    logger.debug(query)
    try:
        return CLIENT.query(query, params={"epoch": "s"})
    except (InfluxDBClientError, InfluxDBServerError) as e:
        logger.error(e)
        if settings.DEBUG:
            raise e

    return

def get_host_usage_metrics(environment, host, interval=600):
    """Return key usage metrics for the host in the last interval.

    {
        'cpu': 25,
        'memory': 60,
        'disk': 10,
    }
    """
    where = "time > now() - {interval}s and hostname='{host}' and environment_label='{environment_label}'".format(
        interval=interval,
        host=_get_short_hostname(host),
        environment_label=environment,
    )
    queries = {
        "cpu": "select (100 - mean(value)) as value from cpu_idle where {}".format(where),
        "memory": "select last(value) as value from /^memory_(used|free|cached|buffered)/ where {}".format(where),
        "disk": "select last(value) as value from fs_space_percent_used where {} and fs='/'".format(where),
    }

    metrics = {}
    for label, q in queries.iteritems():
        result = query(q)
        if not result:
            continue

        value = 0
        if label == "memory":
            total = sum([_get_first_value(result, 'memory_{}'.format(i)) for i in ['used', 'free', 'cached', 'buffered']])
            if total > 0:
                value = (_get_first_value(result, 'memory_used') * 100) / total
        else:
            value = _get_first_value(result)
        metrics[label] = value

    return metrics


def get_host_cpu_metric(environment, hostname, start, end):
    result = query(_get_host_metric_query('/^cpu_/', start, end, environment,
                                          hostname))

    data = []
    for metric in ('cpu_idle', 'cpu_interrupt', 'cpu_nice', 'cpu_softirq', 'cpu_steal', 'cpu_system', 'cpu_user', 'cpu_wait'):
        data.append({
            'key': metric.replace('cpu_', '').capitalize(),
            'values': [[point['value'], point['time']] for point in result.get_points(metric)]
        })
    return data


def get_host_disk_metric(environment, hostname, start, end):
    result = query(_get_host_metric_query(
        '/^disk_octets_(read|write)$/',
        start,
        end,
        environment,
        hostname,
        where='device =~ /^[a-z]+$/',
        group='device'
    ))

    return [{
            'key': 'Write Bytes/s',
            'area': 'true',
            'color': '#FF7F0E',
            'values': _sum_points(result, 'disk_octets_write')
        }, {
            'key': 'Read Bytes/s',
            'area': 'true',
            'values': _sum_points(result, 'disk_octets_read')
        },
    ]


def get_host_memory_metric(environment, hostname, start, end):
    memory_metrics = ('memory_used', 'memory_buffered', 'memory_cached', 'memory_free')
    result = query(_get_host_metric_query(
        '/^({})$/'.format('|'.join(memory_metrics)),
        start,
        end,
        environment,
        hostname))

    data = []
    total_memory = sum([_get_first_value(result, m) for m in memory_metrics])
    if total_memory <= 0:
        return []

    for metric in memory_metrics:
        data.append({
            'key': metric.replace('memory_', '').capitalize(),
            'values': [[point['value'] * 100 / total_memory, point['time']] for point in result.get_points(metric)]
        })
    return data


def get_host_network_metric(environment, hostname, start, end, interfaces=None):
    result = query(_get_host_metric_query(
        '/^if_octets_(rx|tx)$/',
        start,
        end,
        environment,
        hostname,
        where='interface =~ /^({})$/'.format('|'.join(interfaces)) if interfaces else '',
        group='interface'
    ))

    return [{
            'key': 'Tx Bytes/s',
            'area': 'true',
            'color': '#FF7F0E',
            'values': _sum_points(result, 'if_octets_tx')
        }, {
            'key': 'Rx Bytes/s',
            'area': 'true',
            'values': _sum_points(result, 'if_octets_rx')
        },
    ]

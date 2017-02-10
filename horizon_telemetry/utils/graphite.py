from datetime import date
from datetime import datetime, timedelta
import requests
from django.conf import settings
from django.utils import six


def get_instance_data(instance_id, date_from=None, date_until=None):

    targets = {
        'cpu': 'virt_cpu_util?instance_id={}'.format(instance_id),
        'storage_write': 'virt_disk_ops_write?instance_id={}'.format(instance_id),
        'storage_read': 'virt_disk_ops_read?instance_id={}'.format(instance_id),
        'network_in': ''.format(instance_id),
        'network_out': 'integral(nonNegativeDerivative(sumSeries(default_prd.{0}.libvirt.if_octets.*.tx)))'.format(instance_id)
    }

    output = {}

    for metric, target in targets.iteritems():
        now = date.today().isoformat().replace("-", "")
        payload = {
            'target': target,
            'format': 'json',
            'from': '-10min'
        }

        url = '%s/render' % settings.GRAPHITE_ENDPOINT

        response = requests.get(url, params=payload)

        data = response.json()
        for datum in data:

            output[metric] = datum['datapoints']

    return output


def get_hypervisor_data(instance_id):

    targets = {
        'cpu': 'transformNull(offset(scale(asPercent(nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.idle)),nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.*))),-1),100),0)'.format(instance_id.replace(".", "_")),
        'memory': 'transformNull(offset(scale(asPercent(sumSeries(sumSeriesWithWildcards(default_prd.{0}.memory.{{free,buffered,cached}})),sumSeries(default_prd.{0}.memory.*)),-1),100),0)'.format(instance_id.replace(".", "_")),
        'disk': 'transformNull(offset(scale(asPercent(default_prd.{0}.partition.root.free, sumSeries(default_prd.{0}.partition.root.*)),-1),100),0)'.format(instance_id.replace(".", "_"))
    }

    output = {}

    for metric, target in targets.iteritems():
        now = date.today().isoformat().replace("-", "")
        payload = {
            'target': target,
            'format': 'json',
            'from': '-10min'
        }

        url = '%s/render' % settings.GRAPHITE_ENDPOINT

        response = requests.get(url, params=payload, timeout=60)

        try:
            data = response.json()
        except:
            # skip now
            continue

        for datum in data:
            output[metric] = datum['datapoints'][7][0]

    return output

def get_cpu_data(node, date_from, date_until):

    if not isinstance(date_from, six.string_types):
        date_from = date_from.isoformat()
        date_until = date_until.isoformat()

    time_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    time_until = datetime.strptime(date_until, "%Y-%m-%d").date()
    time_diff = time_until - time_from

    if time_diff.days == 0:
      sum_days = 10
    else:
      sum_days = int(time_diff.days) * 10 + 10

    targets = {
        'Idle': 'transformNull(summarize(asPercent(nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.idle)),nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.*))), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
        'Interrupt': 'transformNull(summarize(asPercent(nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.interrupt)),nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.*))), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
        'Nice': 'transformNull(summarize(asPercent(nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.nice)),nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.*))), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
        'Softirq': 'transformNull(summarize(asPercent(nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.softirq)),nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.*))), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
        'Steal': 'transformNull(summarize(asPercent(nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.steal)),nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.*))), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
        'System': 'transformNull(summarize(asPercent(nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.system)),nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.*))), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
        'User': 'transformNull(summarize(asPercent(nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.user)),nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.*))), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
        'Wait': 'transformNull(summarize(asPercent(nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.wait)),nonNegativeDerivative(sumSeries(default_prd.{0}.cpu.*.*))), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days)
    }

    output = []

    for metric, target in targets.iteritems():
        payload = {
            'target': target,
            'format': 'json',
            'from': '00:00_%s' % date_from.replace("-", ""),
            'until': '23:59_%s' % date_until.replace("-", "")
        }

        url = '%s/render' % settings.GRAPHITE_ENDPOINT

        response = requests.get(url, params=payload)

        data = response.json()
        for datum in data:
            output.append({
                'key': metric,
                'values': datum['datapoints']
            })

    return output

def get_mem_data(node, date_from, date_until):

    if not isinstance(date_from, six.string_types):
        date_from = date_from.isoformat()
        date_until = date_until.isoformat()

    time_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    time_until = datetime.strptime(date_until, "%Y-%m-%d").date()
    time_diff = time_until - time_from

    if time_diff.days == 0:
      sum_days = 10
    else:
      sum_days = int(time_diff.days) * 10 + 10

    targets = {
        'Free': 'transformNull(summarize(asPercent(default_prd.{0}.memory.free,sum(default_prd.{0}.memory.*)), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
        'Buffered': 'transformNull(summarize(asPercent(default_prd.{0}.memory.buffered,sum(default_prd.{0}.memory.*)), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
        'Cached': 'transformNull(summarize(asPercent(default_prd.{0}.memory.cached,sum(default_prd.{0}.memory.*)), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
        'Used': 'transformNull(summarize(asPercent(default_prd.{0}.memory.used,sum(default_prd.{0}.memory.*)), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
    }

    output = []

    for metric, target in targets.iteritems():
        payload = {
            'target': target,
            'format': 'json',
            'from': '00:00_%s' % date_from.replace("-", ""),
            'until': '23:59_%s' % date_until.replace("-", "")
        }

        url = '%s/render' % settings.GRAPHITE_ENDPOINT

        response = requests.get(url, params=payload)

        data = response.json()
        for datum in data:
            output.append({
                'key': metric,
                'values': datum['datapoints']
            })

    return output

def get_hdd_data(node, date_from, date_until):

    if not isinstance(date_from, six.string_types):
        date_from = date_from.isoformat()
        date_until = date_until.isoformat()

    time_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    time_until = datetime.strptime(date_until, "%Y-%m-%d").date()
    time_diff = time_until - time_from

    if time_diff.days == 0:
      sum_days = 10
    else:
      sum_days = int(time_diff.days) * 10 + 10

    targets = {
        'Read': 'transformNull(summarize(scale(nonNegativeDerivative(sumSeries(default_prd.{0}.disk.s*.read_ops)),0.016666667), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days),
        'Write': 'transformNull(summarize(scale(nonNegativeDerivative(sumSeries(default_prd.{0}.disk.s*.write_ops)),0.016666667), "{1}minute", "avg"),0)'.format(node.replace(".", "_"), sum_days)
    }

    output = []

    for metric, target in targets.iteritems():
        payload = {
            'target': target,
            'format': 'json',
            'from': '00:00_%s' % date_from.replace("-", ""),
            'until': '23:59_%s' % date_until.replace("-", "")
        }

        url = '%s/render' % settings.GRAPHITE_ENDPOINT

        response = requests.get(url, params=payload)
        data = response.json()

        if target == targets['Write']:
            for datum in data:
                output.append({
                    'key': metric,
                    'area': 'true',
                    'color': '#FF7F0E',
                    'values': datum['datapoints']
                })
        else:
            for datum in data:
                output.append({
                    'key': metric,
                    'area': 'true',
                    'values': datum['datapoints']
                })

    return output

def get_cpt_net_data(compute, date_from, date_until):

    if not isinstance(date_from, six.string_types):
        date_from = date_from.isoformat()
        date_until = date_until.isoformat()

    time_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    time_until = datetime.strptime(date_until, "%Y-%m-%d").date()
    time_diff = time_until - time_from

    if time_diff.days == 0:
      sum_days = 10
    else:
      sum_days = int(time_diff.days) * 10 + 10

    targets = {
        'Received': 'transformNull(summarize(scale(nonNegativeDerivative(default_prd.{0}.interface.vhost0.rx_octets),0.000016276), "{1}minute", "avg"),0)'.format(compute.replace(".", "_"), sum_days),
        'Transferred': 'transformNull(summarize(scale(nonNegativeDerivative(default_prd.{0}.interface.vhost0.tx_octets),0.000016276), "{1}minute", "avg"),0)'.format(compute.replace(".", "_"), sum_days)
    }

    output = []

    for metric, target in targets.iteritems():
        payload = {
            'target': target,
            'format': 'json',
            'from': '00:00_%s' % date_from.replace("-", ""),
            'until': '23:59_%s' % date_until.replace("-", "")
        }

        url = '%s/render' % settings.GRAPHITE_ENDPOINT

        response = requests.get(url, params=payload)
        data = response.json()

        if target == targets['Transferred']:
            for datum in data:
                output.append({
                    'key': metric,
                    'area': 'true',
                    'color': '#FF7F0E',
                    'values': datum['datapoints']
                })
        else:
            for datum in data:
                output.append({
                    'key': metric,
                    'area': 'true',
                    'values': datum['datapoints']
                })

    return output

def get_ctl_net_data(control, date_from, date_until):

    if not isinstance(date_from, six.string_types):
        date_from = date_from.isoformat()
        date_until = date_until.isoformat()

    time_from = datetime.strptime(date_from, "%Y-%m-%d").date()
    time_until = datetime.strptime(date_until, "%Y-%m-%d").date()
    time_diff = time_until - time_from

    if time_diff.days == 0:
      sum_days = 10
    else:
      sum_days = int(time_diff.days) * 10 + 10

    targets = {
        'Received': 'transformNull(summarize(scale(nonNegativeDerivative(default_prd.{0}.interface.eth0.rx_octets),0.000016276), "{1}minute", "avg"),0)'.format(control.replace(".", "_"), sum_days),
        'Transferred': 'transformNull(summarize(scale(nonNegativeDerivative(default_prd.{0}.interface.eth0.tx_octets),0.000016276), "{1}minute", "avg"),0)'.format(control.replace(".", "_"), sum_days)
    }

    output = []

    for metric, target in targets.iteritems():
        payload = {
            'target': target,
            'format': 'json',
            'from': '00:00_%s' % date_from.replace("-", ""),
            'until': '23:59_%s' % date_until.replace("-", "")
        }

        url = '%s/render' % settings.GRAPHITE_ENDPOINT

        response = requests.get(url, params=payload)
        data = response.json()

        if target == targets['Transferred']:
            for datum in data:
                output.append({
                    'key': metric,
                    'area': 'true',
                    'color': '#FF7F0E',
                    'values': datum['datapoints']
                })
        else:
            for datum in data:
                output.append({
                    'key': metric,
                    'area': 'true',
                    'values': datum['datapoints']
                })

    return output

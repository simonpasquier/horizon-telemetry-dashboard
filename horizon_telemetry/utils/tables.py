
from django.conf import settings
from horizon import tables
from django.utils.html import format_html

GRAPHITE_PREFIX = getattr(settings, 'GRAPHITE_PREFIX', 'stats')


class GraphColumn(tables.base.Column):

    """Simple Graph column

    wrapps data with id {{column_name}}_{{self.table.get_object_id}}
    if is not object_id provided

    :attribute:graph_id - asdadasd-asdasd-asdad-asd

    :attribute:graph_metric - libvirt.disk_ops.*.write

    """

    def __init__(self, *args, **kw):
        graph_id = kw.pop('graph_id', None)
        graph_metric = kw.pop('graph_metric', None)
        full_path = kw.pop('full_path', False)
        super(GraphColumn, self).__init__(*args, **kw)
        self.graph_id = graph_id
        self.graph_metric = graph_metric
        self.full_path = full_path

    def get_graphite_prefix(self):
        return GRAPHITE_PREFIX

    def get_metric(self, datum):

        uuid = self.get_uuid(datum)
        if GRAPHITE_PREFIX and not self.full_path:
            return '{}.{}.{}'.format(
                GRAPHITE_PREFIX, uuid, self.graph_metric or 'specify_metric')
        elif GRAPHITE_PREFIX and self.full_path:
            return '{}.{}'.format(
                GRAPHITE_PREFIX, self.graph_metric or 'specify_metric')
        return '{}.{}'.format(uuid, self.graph_metric or 'specify_metric')

    def get_uuid(self, datum):
        return getattr(self, self.graph_id, None) or self.table.get_object_id(datum)

    def get_raw_data(self, datum):

        return format_html("""
            <div id="graph_{name}_{uuid}" data-name="{name}" data-metric="{metric}"></div>
            """.format(**{
            'name': self.name,
            'uuid': self.get_uuid(datum),
            'metric': self.get_metric(datum)}))


class InstanceGraphColumn(GraphColumn):

    def get_raw_data(self, datum):

        return format_html("""
            <div id="graph_{name}_{uuid}" data-name="{name}" data-metric="{metric}"></div>
            """.format(**{
            'name': self.name,
            'uuid': self.get_uuid(datum),
            'metric': self.get_metric(datum)}))

    def get_uuid(self, datum):
        return self.table.get_object_id(datum)

    def get_metric(self, datum):

        return 'nonNegativeDerivative(default_prd.{}.{})'.format(
            self.get_uuid(datum),
            self.graph_metric
            )


class InstanceGraphColumnTwoRow(GraphColumn):

    def __init__(self, *args, **kw):
        graph_id_first = kw.pop('graph_id_first', None)
        graph_id_second = kw.pop('graph_id_second', None)
        graph_metric_first = kw.pop('graph_metric_first', None)
        graph_metric_second = kw.pop('graph_metric_second', None)
        full_path = kw.pop('full_path', False)
        super(GraphColumn, self).__init__(*args, **kw)
        self.graph_id_first = graph_id_first
        self.graph_id_second = graph_id_second
        self.graph_metric_first = graph_metric_first
        self.graph_metric_second = graph_metric_second
        self.full_path = full_path

    def get_raw_data(self, datum):

        return format_html("""
            <div id="graph_{idFirst}_{uuidFirst}" class="telemetry_first_canvas" data-name="{idFirst}" data-metric="{metricFirst}"></div><div id="graph_{idSecond}_{uuidSecond}" class="telemetry_second_canvas" data-name="{idSecond}" data-metric="{metricSecond}"></div>
            """.format(**{
            'idFirst': self.graph_id_first,
            'uuidFirst': self.get_uuid(datum),
            'metricFirst': self.get_first_metric(datum),
            'idSecond': self.graph_id_second,
            'uuidSecond': self.get_uuid(datum),
            'metricSecond': self.get_second_metric(datum)
            }))

    def get_uuid(self, datum):
        return self.table.get_object_id(datum)

    def get_first_metric(self, datum):

        return 'nonNegativeDerivative(default_prd.{}.{})'.format(
            self.get_uuid(datum),
            self.graph_metric_first
            )

    def get_second_metric(self, datum):

        return 'scale(nonNegativeDerivative(default_prd.{}.{}),-1)'.format(
            self.get_uuid(datum),
            self.graph_metric_second
            )

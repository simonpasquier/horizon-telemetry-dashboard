from django.conf import settings
from horizon import tables
from django.utils.html import format_html


class InstanceGraphColumn(tables.base.Column):

    def __init__(self, *args, **kw):
        metric = kw.pop('metric')
        super(InstanceGraphColumn, self).__init__(*args, **kw)
        self.metric = metric

    def get_uuid(self, datum):
        return self.table.get_object_id(datum)

    def get_raw_data(self, datum):
        return format_html("""
            <div id="graph_{name}_{uuid}" metric="{metric}"></div>
            """.format(**{
            'name': self.name,
            'uuid': self.get_uuid(datum),
            'metric': self.metric
        }))


class InstanceGraphColumnTwoRow(InstanceGraphColumn):

    def __init__(self, *args, **kw):
        second_metric = kw.pop('second_metric')
        super(InstanceGraphColumnTwoRow, self).__init__(*args, **kw)
        self.second_metric = second_metric

    def get_raw_data(self, datum):
        return format_html("""
            <div id="graph_1_{name}_{uuid}" class="telemetry_first_canvas" metric="{first_metric}"></div><div id="graph_2_{name}_{uuid}" class="telemetry_second_canvas" metric="{second_metric}"></div>
            """.format(**{
            'name': self.name,
            'uuid': self.get_uuid(datum),
            'first_metric': self.metric,
            'second_metric': self.second_metric,
        }))

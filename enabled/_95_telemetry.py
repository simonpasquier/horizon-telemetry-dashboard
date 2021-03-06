
DASHBOARD = 'telemetry'

ENABLED = True

ADD_INSTALLED_APPS = [
    'horizon_telemetry'
]

ADD_SCSS_FILES = [
    'telemetry/scss/telemetry.scss'
]

ADD_JS_FILES = [
    'telemetry/js/cubism.js',
    'telemetry/js/graph_utils.js',
    'telemetry/js/radial-progress-chart.min.js',
    'telemetry/js/nv.d3.min.js'
]

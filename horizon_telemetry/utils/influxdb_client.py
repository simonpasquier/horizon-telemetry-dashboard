import logging

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

def query(query):
    '''Return the result of the InfluxDB query

    None if the query failed
    '''
    logger.debug(query)
    try:
        return CLIENT.query(query,params={"epoch": "s"})
    except (InfluxDBClientError, InfluxDBServerError) as e:
        logger.error(e)
        if settings.DEBUG:
            raise e

    return

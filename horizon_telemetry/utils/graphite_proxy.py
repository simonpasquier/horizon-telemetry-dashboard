import requests
from django.http import HttpResponse
from django.conf import settings
from .memoized import memoized
from django.core.urlresolvers import reverse


def graphite_render(request):
    '''Just proxy for Graphite render method

    bind on /render*
    '''

    #@memoized
    def get_data(url):
        '''Just memoized by url'''
        # We don't want serialize data here
        return requests.get(url).text

    if hasattr(request, 'user') and request.user.is_authenticated():

        original_url = request.get_full_path().replace(
            reverse('horizon:telemetry:overview:render_graphite'), '')
        url = '%s%s' % (settings.GRAPHITE_ENDPOINT, original_url)

        try:
            response = get_data(url)
        except Exception as e:
            if settings.DEBUG:
                raise e
            return HttpResponse('Undefined error.', status=500)
        else:
            return HttpResponse(response)

    return HttpResponse('Unauthorized', status=401)

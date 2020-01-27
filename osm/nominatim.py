"""
The module provides methods to query Nominatim API for ids of geographical
locations.
"""

import logging
import shelve

import requests


def shelve_it(file_name):
    d = shelve.open(file_name)

    def decorator(func):
        def new_func(param):
            if param not in d:
                d[param] = func(param)
            return d[param]

        return new_func

    return decorator


def enable_logging_http():
    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.
    import http.client as http_client
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


base_url = 'https://nominatim.openstreetmap.org'


@shelve_it('cache.shelve')
def find_all(query):
    params = {
        'format': 'json',
        'q': query
    }
    r = requests.get(f'{base_url}/search', params)
    return r.json()


def find_first(query):
    results = find_all(query)
    if len(results) == 0:
        raise LookupError(f'No place found for query: {query}')
    return results[0]


enable_logging_http()

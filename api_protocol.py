import logging

import requests

from requests.exceptions import RequestException, JSONDecodeError


class NightscoutApiProtocol:
    def __init__(self, base_url, timeout):
        self.base_url = base_url
        self.timeout = timeout

    def get(self, resource, params={}, timeout=None):
        if timeout is None:
            timeout = self.timeout

        try:
            r = requests.get(self.base_url + resource, params=params, timeout=timeout)
            logging.debug('GET request to {} returned with status code {}'.format(r.url, r.status_code))
            return r.json()
        
        except JSONDecodeError:
            raise NightscoutNonJsonResponseException('GET request to {} returned Non JSON response'.format(self.base_url + resource))

        except RequestException:
            raise NightscoutCommunicationException('GET request to {} failed with connection error'.format(self.base_url + resource))


class NightscoutCommunicationException(Exception):
    pass

class NightscoutNonJsonResponseException(Exception):
    pass

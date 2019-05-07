from api_protocol import NightscoutApiProtocol

class Nightscout:
    def __init__(self, url):
        self.api = NightscoutApiProtocol(url + '/api/v1/', timeout=5)

    def get_last_entry(self):
        return self.api.get('entries.json')

    def get_entries_since(self, timestamp=None):
        return self.api.get('entries.json', params={'find[date][$gt]': timestamp})

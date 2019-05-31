from config import nightscout as night_conf
from api_protocol import NightscoutApiProtocol

class Nightscout:
    def __init__(self):
        self.timeout = int(night_conf.get('default_timeout', 5))
        self.default_entries_count = int(night_conf.get('default_entries_count', 30))
        self.api = NightscoutApiProtocol(night_conf.get('base_url'), self.timeout)

    def get_last_entry(self):
        return self.api.get('/api/v1/entries/current.json')

    def get_entries_since(self, timestamp=None, count=None, entry_type=None):
        return self.api.get('/api/v1/entries.json', params={'find[date][$gt]': timestamp, 'count': count or self.default_entries_count, 'find[type]': entry_type})

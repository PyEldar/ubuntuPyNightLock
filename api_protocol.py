import requests

class ApiProtocol:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, *args, **kwargs):
        raise NotImplementedError()

    def post(self, *args, **kwargs):
        raise NotImplementedError()

    def patch(self, *args, **kwargs):
        raise NotImplementedError()

    def head(self, *args, **kwargs):
        raise NotImplementedError()


class NightscoutApiProtocol:
    pass
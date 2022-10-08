import hassapi as hass
import requests

class HttpFetch(hass.Hass):
    def initialize(self):
        self.run_daily(self.fetch, self.args['when'])
        #self.fetch({})

    def fetch(self, kwargs):
        fn = getattr(requests, self.args.get('method', 'get').lower())
        res = fn(self.args['url'])
        print(res.text)


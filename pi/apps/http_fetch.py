import hassapi as hass
import requests

class HttpFetch(hass.Hass):
    def initialize(self):
        self.run_daily(self.fetch, self.args['when'])

    def fetch(self, kwargs):
        res = requests.get(self.args['url'])
        print(res.text)


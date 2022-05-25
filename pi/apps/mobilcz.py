import re
import time
import requests
import hassapi as hass

def get_balance(username, password):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    }

    session = requests.Session()
    session.headers.update(headers)
    body = {
        'username': username,
        'password': password,
        'nextURL': 'checkStatus.jsp',
        'errURL': 'clickError.jsp',
    }
    session.get('https://samoobsluha.mobil.cz/muj-prehled')
    res = session.post('https://samoobsluha.mobil.cz/.gang/login/username', data=body)

    components = '|'.join(['.'.join(x) for x in re.findall('data-lazy-loading="{&quot;rk&quot;:&quot;([^&]+)&quot;}" lazy-loading-module-code="dashboard" id="([^"]+)"', res.text)])

    res = session.post(f'https://samoobsluha.mobil.cz/muj-prehled?p_p_id=mobilczvcc_WAR_vcc&p_p_lifecycle=0&p_p_state=exclusive&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&_mobilczvcc_WAR_vcc_moduleCode=dashboard&_mobilczvcc_WAR_vcc_lazyLoading=true&_mobilczvcc_WAR_vcc_componentIds={components}', headers={'X-Requested-With': 'XMLHttpRequest'})

    time.sleep(2)
    res = session.post(f'https://samoobsluha.mobil.cz/muj-prehled?p_p_id=mobilczvcc_WAR_vcc&p_p_lifecycle=0&p_p_state=exclusive&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&_mobilczvcc_WAR_vcc_moduleCode=dashboard&_mobilczvcc_WAR_vcc_lazyLoading=true&_mobilczvcc_WAR_vcc_componentIds={components}', headers={'X-Requested-With': 'XMLHttpRequest'})

    m = re.search('([0-9]+) Kč', res.text)
    if m:
        return m.group(1)
    return -1

class MobilCZ(hass.Hass):
    def initialize(self):
       self.run_daily(self.fetch, "10:00:00", random_start=-3600 * 2, random_end=3600 * 5)

    def fetch(self, kwargs):
        balance = get_balance(self.args['username'], self.args['password'])
        self.notify(f"{self.name} {balance}")
        self.set_state(f"sensor.{self.name}", state=balance, device_class="monetary", unit_of_measurement="CZK")

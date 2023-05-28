import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

def get_balance(username, password):
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=/tmp/selenium") 
    driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://extranet.edenred.cz/')
    #driver.implicitly_wait(5)

    if 'sso' in driver.current_url:
        try:
            driver.find_element(By.ID, 'onetrust-reject-all-handler').click()
        except NoSuchElementException as e:
            pass

        driver.find_element(By.ID, 'ctl00_MainCPH_UsernameTB').send_keys(username)
        driver.find_element(By.ID, 'ctl00_MainCPH_PasswordTB').send_keys(password)
        driver.implicitly_wait(1)
        driver.find_element(By.ID, 'ctl00_MainCPH_LoginBtn').click()


    wait = WebDriverWait(driver, 30)
    wait.until(EC.presence_of_element_located((By.ID, 'ctl00_MainCPH_UserCardListUC_OnlyCurrentCardsChB')))


    el = driver.find_element(By.ID, 'ctl00_MainCPH_UserCardListUC_ProgressUP')
    text = el.get_attribute('innerText')

    driver.quit()

    m = re.search('Ticket Restaurant Balance: ([0-9,.]+) CZK', text)
    if m:
        balance = float(m.group(1).replace(',', ''))
        print(balance)
        return int(balance)
    else:
        return -1

if __name__ == "__main__":
    import yaml
    from pathlib import Path
    with open(Path(__file__).parent.parent / "secrets.yaml") as f:
        c = yaml.safe_load(f)
    balance = get_balance(c['edenred_username'], c['edenred_password'])
    print(balance)
else:
    import hassapi as hass
    import datetime
    import dbus
    import threading
    from gi.repository import GObject
    from dbus.mainloop.glib import DBusGMainLoop

    class Edenred(hass.Hass):
        def initialize(self):
            DBusGMainLoop(set_as_default=True)
            bus = dbus.SystemBus()
            bus.add_signal_receiver(self.fetch, 'PrepareForSleep', 'org.freedesktop.login1.Manager', 'org.freedesktop.login1')

            def thread_fn():
                loop = GObject.MainLoop()
                loop.run()
            self.t = threading.Thread(target=thread_fn)
            self.t.start()



        def fetch(self, sleeping):
            if sleeping:
                return

            if datetime.datetime.now().hour < 10:
                self.log("Too early")
                return

            path = os.path.join("/tmp", f".edenred.{datetime.datetime.now().date()}")
            if os.path.exists(path):
                self.log("Already fetched today")
                return

            with open(path, "w") as f:
                pass

            self.log("triggered")

            time.sleep(60)

            balance = get_balance(self.args['username'], self.args['password'])
            self.notify(f"{self.name} {balance}")
            self.set_state(f"sensor.{self.name}", state=balance, device_class="monetary", unit_of_measurement="CZK")

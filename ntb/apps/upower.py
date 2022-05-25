import subprocess
import hassapi as hass

def upower():
    out = subprocess.check_output(["upower", "-d"], text=True)
    devices = {}
    current_dev = None
    for line in out.splitlines():
        if line.startswith('Device: '):
            name = line.split(' ', 1)[1]
            devices[name] = {}
            current_dev = devices[name]
        elif not line.startswith(' '):
            current_dev = None
        elif current_dev is not None:
            parts = [s.strip() for s in line.split(':', 1)]
            if len(parts) == 2:
                current_dev[parts[0]] = parts[1]
    return devices

class UPower(hass.Hass):
    def initialize(self):
        self.run_every(self.fetch, 'now', 5 * 60)

    def fetch(self, kwargs):
        data = upower().get(self.args['path'], None)
        if not data:
            self.log(f"Power device {self.args['path']} not found")
            return

        self.set_state(
            f"sensor.{self.name}",
            state=data['percentage'].replace('%', ''),
            unit_of_measurement='%',
            device_class="battery",
        )

        if 'state' in data:
            self.set_state(
                f"sensor.{self.name}_state",
                state=data['state'] == 'charging',
                device_class="plug",
            )



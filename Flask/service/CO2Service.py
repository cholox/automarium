# @Author: Carlos Isaza <Cholox>
# @Date:   22-Nov-2017
# @Project: https://github.com/cholox/automarium
# @Last modified by:   Carlos Isaza
# @Last modified time: 18-Dec-2017
# @License: MIT

class CO2Service(object):
    """Manage the aquarium CO2 for the plants. The ESP8266 controls the valve
       with a servo.
    """
    def __init__(self, mqtt_app, configparser):
        self.mqtt = mqtt_app
        self.parser = configparser

    def open_co2(self):
        self.mqtt.publish('home/aquarium/co2', '1')
        self.parser.set('co2', 'value', '1')
        self.write_to_file()
        print('open_co2')

    def close_co2(self):
        self.mqtt.publish('home/aquarium/co2', '0')
        self.parser.set('co2', 'value', '0')
        self.write_to_file()
        print('close_co2')

    def write_to_file(self):
        with open('backup.ini', 'w') as backupfile:
            self.parser.write(backupfile)

    def backup(self):
        self.parser.read('backup.ini')
        current_value = self.parser.getint('co2', 'value')
        if current_value:
            self.open_co2()
        else:
            self.close_co2()

# @Author: Carlos Isaza
# @Date:   13-Dec-2017
# @Project: https://github.com/cholox/automarium
# @Last modified by:   Carlos Isaza
# @Last modified time: 18-Dec-2017
# @License: MIT

class Relay2ervice(object):
    """Manage the aquarium relay 2"""
    def __init__(self, mqtt_app, configparser):
        self.mqtt = mqtt_app
        self.parser = configparser

    def turn_relay2_on(self):
        self.mqtt.publish('home/aquarium/relay2', '1')
        self.parser.set('relay2', 'value', '1')
        self.write_to_file()
        print('turn relay2 on')

    def turn_relay2_off(self):
        self.mqtt.publish('home/aquarium/relay2', '0')
        self.parser.set('relay2', 'value', '0')
        self.write_to_file()
        print('turn relay2 off')

    def write_to_file(self):
        with open('backup.ini', 'w') as backupfile:
            self.parser.write(backupfile)

    def backup(self):
        self.parser.read('backup.ini')
        current_value = self.parser.getint('relay2', 'value')
        if current_value:
            self.turn_relay2_on()
        else:
            self.turn_relay2_off()

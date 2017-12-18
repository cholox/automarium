# @Author: Carlos Isaza <Cholox>
# @Date:   22-Nov-2017
# @Project: https://github.com/cholox/automarium
# @Last modified by:   Carlos Isaza
# @Last modified time: 18-Dec-2017
# @License: MIT

class LightService(object):
    """Manage the aquarium main light with a relay module"""
    def __init__(self, mqtt_app, configparser):
        self.mqtt = mqtt_app
        self.parser = configparser

    def turn_lights_on(self):
        self.mqtt.publish('home/aquarium/light', '1')
        self.parser.set('light', 'value', '1')
        self.write_to_file()
        print('turn light on')

    def turn_lights_off(self):
        self.mqtt.publish('home/aquarium/light', '0')
        self.parser.set('light', 'value', '0')
        self.write_to_file()
        print('turn light off')

    def write_to_file(self):
        with open('backup.ini', 'w') as backupfile:
            self.parser.write(backupfile)

    def backup(self):
        self.parser.read('backup.ini')
        current_value = self.parser.getint('light', 'value')
        if current_value:
            self.turn_lights_on()
        else:
            self.turn_lights_off()

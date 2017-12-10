# @Author: Carlos Isaza <Cholox>
# @Date:   22-Nov-2017
# @Project: https://github.com/cholox/automarium
# @Last modified by:   Cholox
# @Last modified time: 22-Nov-2017
# @License: MIT

class LightService(object):
    """Manage the aquarium main light with a relay module"""
    def __init__(self, mqtt_app):
        self.mqtt = mqtt_app

    def turn_lights_on(self):
        self.mqtt.publish('home/aquarium/light', '1')
        print('turn light on')

    def turn_lights_off(self):
        self.mqtt.publish('home/aquarium/light', '0')
        print('turn light off')

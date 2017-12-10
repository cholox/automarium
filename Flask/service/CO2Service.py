# @Author: Carlos Isaza <Cholox>
# @Date:   22-Nov-2017
# @Project: https://github.com/cholox/automarium
# @Last modified by:   Cholox
# @Last modified time: 22-Nov-2017
# @License: MIT

class CO2Service(object):
    """Manage the aquarium CO2 for the plants. The ESP8266 controls the valve
       with a servo.
    """
    def __init__(self, mqtt_app):
        self.mqtt = mqtt_app

    def open_co2(self):
        self.mqtt.publish('home/aquarium/co2', '1')
        print('open_co2')

    def close_co2(self):
        self.mqtt.publish('home/aquarium/co2', '0')
        print('close_co2')

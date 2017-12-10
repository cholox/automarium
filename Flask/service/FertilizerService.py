# @Author: Carlos Isaza <Cholox>
# @Date:   22-Nov-2017
# @Project: https://github.com/cholox/automarium
# @Last modified by:   Cholox
# @Last modified time: 22-Nov-2017
# @License: MIT

import schedule

class FertilizerService(object):
    """Manage the aquarium fertilizer. The ESP8266 modules manages this with
       a peristaltic pump.
    """
    def __init__(self, mqtt_app):
        self.mqtt = mqtt_app

    def fertilize_ml(self, ml):
        self.mqtt.publish('home/aquarium/fertilizer', ml)
        print('fertilize')

    def empty_tube(self):
        self.mqtt.publish('home/aquarium/fertilizer', '0')
        print('empty fertilizer')

# @Author: Carlos Isaza <Cholox>
# @Date:   22-Nov-2017
# @Project: https://github.com/cholox/automarium
# @Last modified by:   cholox
# @Last modified time: 10-Dec-2017
# @License: MIT

import json
import eventlet
import schedule
import threading
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

from service.LightService import LightService
from service.FertilizerService import FertilizerService
from service.CO2Service import CO2Service

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET'] = '213hfSDkj435yxc*k3242_23'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = '192.168.0.4'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'pi'
app.config['MQTT_PASSWORD'] = '1FjqrZ78*'
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False
app.config['MQTT_LAST_WILL_TOPIC'] = 'home/lastwill'
app.config['MQTT_LAST_WILL_MESSAGE'] = 'bye'
app.config['MQTT_LAST_WILL_QOS'] = 2

mqtt = Mqtt(app)
socketio = SocketIO(app, async_mode="eventlet")

light_service = LightService(mqtt)
co2_service = CO2Service(mqtt)
fertilizer_service = FertilizerService(mqtt)

schedule_thread = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test')
def test_route():
    return render_template('test.html')


# @socketio.on('publish')
# def handle_publish(json_str):
#     data = json.loads(json_str)
#     mqtt.publish(data['topic'], data['message'])
#     print('Publishing to topic: %s, message: %s' % (data['topic'], data['message']))


@socketio.on('connect')
def subscribe_to_aquarium():
    global schedule_thread
    if schedule_thread is None:
        print('Start thread')
        schedule_thread = socketio.start_background_task(target=run_schedule)
    mqtt.subscribe('home/aquarium/#')


@socketio.on('change_light_schedule')
def change_light_schedule(data):
    data = json.loads(data)
    print(data)
    turn_on_time = data['time1']
    turn_off_time = data['time2']
    schedule.clear('light')
    try:
        # schedule.every().day.at(turn_on_time).do(light_service.turn_lights_on).tag('light')
        schedule.every(3).seconds.do(light_service.turn_lights_on).tag('light')
        # schedule.every().day.at(turn_off_time).do(light_service.turn_lights_off).tag('light')
        schedule.every(4).seconds.do(light_service.turn_lights_off).tag('light')
    except Exception as e:
        socketio.emit('error', e)


@socketio.on('change_co2_schedule')
def change_co2_schedule(data):
    data = json.loads(data)
    print(data)
    turn_on_time = data['time1']
    turn_off_time = data['time2']
    schedule.clear('co2')
    try:
        # schedule.every().day.at(turn_on_time).do(co2_service.open_co2).tag('co2')
        schedule.every(3).seconds.do(co2_service.open_co2).tag('co2')
        # schedule.every().day.at(turn_off_time).do(co2_service.close_co2).tag('co2')
        schedule.every(4).seconds.do(co2_service.close_co2).tag('co2')
    except Exception as e:
        socketio.emit('error', e)

@socketio.on('change_fertilizer_schedule')
def change_fertilizer_schedule(data):
    data = json.loads(data)
    print(data)
    fertilize_time = data['time']
    fertilizer_amount = data['amount']
    schedule.clear('fertilizer')
    try:
        # schedule.every().day.at(fertilize_time).do(fertilizer_service.fertilize_ml, fertilizer_amount).tag('fertilizer')
        schedule.every(4).seconds.do(fertilizer_service.fertilize_ml, fertilizer_amount).tag('fertilizer')
    except Exception as e:
        socketio.emit('error', e)


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    # print(data)
    socketio.emit('mqtt_message', data)


#-------------------------------Direct Commands---------------------------------
@socketio.on('turn_lights_on')
def turn_lights_on_command():
    light_service.turn_lights_on()


@socketio.on('turn_lights_off')
def turn_lights_off_command():
    light_service.turn_lights_off()
#-------------------------------------------------------------------------------

# @mqtt.on_log()
# def handle_logging(client, userdata, level, buf):
#     #print(level, buf)
def run_schedule():
    while True:
        schedule.run_pending()
        socketio.sleep(1)
    print('Schedule stopped')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8900,  use_reloader=True, debug=True)

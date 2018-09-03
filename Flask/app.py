# @Author: Carlos Isaza <Cholox>
# @Date:   22-Nov-2017
# @Project: https://github.com/cholox/automarium
# @Last modified by:   isaza
# @Last modified time: 05-Apr-2018
# @License: MIT

import json
import eventlet
import schedule
import threading
import configparser
from flask import Flask, render_template, Response, \
redirect, url_for, request, session, abort
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask.ext.login import LoginManager, UserMixin, \
login_required, login_user, logout_user

from service.LightService import LightService
from service.FertilizerService import FertilizerService
from service.CO2Service import CO2Service
from service.Relay2Service import Relay2ervice

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET'] = '213hfSDkj435yxc*k3242_23'
app.config['SECRET_KEY'] = '213hfSDkj435yxc*k3242_23_231'
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

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# silly user model
class User(UserMixin):

    def __init__(self, id, name = "", password = ""):
        self.id = id
        self.name = name
        self.password = password

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


# create some users with ids 1 to
users = [tato]


mqtt = Mqtt(app)
socketio = SocketIO(app, async_mode="eventlet")
parser = configparser.ConfigParser()
parser.read('backup.ini')

light_service = LightService(mqtt, parser)
co2_service = CO2Service(mqtt, parser)
fertilizer_service = FertilizerService(mqtt)
relay2_service = Relay2ervice(mqtt, parser)

schedule_thread = None

def schedule_backup():
    light_time1 = parser.get('light', 'time1')
    light_time2 = parser.get('light', 'time2')
    light_time3 = parser.get('light', 'time3')
    light_time4 = parser.get('light', 'time4')
    co2_time1 = parser.get('co2', 'time1')
    co2_time2 = parser.get('co2', 'time2')
    co2_time3 = parser.get('co2', 'time3')
    co2_time4 = parser.get('co2', 'time4')
    relay2_time1 = parser.get('relay2', 'time1')
    relay2_time2 = parser.get('relay2', 'time2')
    fertilizer_time = parser.get('fertilizer', 'time')
    fertilizer_amount = parser.get('fertilizer', 'amount')

    schedule.every().day.at(light_time1).do(light_service.turn_lights_on).tag('light')
    schedule.every().day.at(light_time2).do(light_service.turn_lights_off).tag('light')
    if light_time3 != '' and light_time4 != '':
        schedule.every().day.at(light_time3).do(light_service.turn_lights_on).tag('light')
        schedule.every().day.at(light_time4).do(light_service.turn_lights_off).tag('light')
    schedule.every().day.at(co2_time1).do(co2_service.open_co2).tag('co2')
    schedule.every().day.at(co2_time2).do(co2_service.close_co2).tag('co2')
    if co2_time3 != '' and co2_time4 != '':
        schedule.every().day.at(co2_time3).do(co2_service.open_co2).tag('co2')
        schedule.every().day.at(co2_time4).do(co2_service.close_co2).tag('co2')
    schedule.every().day.at(relay2_time1).do(relay2_service.turn_relay2_on).tag('relay2')
    schedule.every().day.at(relay2_time2).do(relay2_service.turn_relay2_off).tag('relay2')
    schedule.every().day.at(fertilizer_time).do(fertilizer_service.fertilize_sec, fertilizer_amount).tag('fertilizer')


def run_backup():
    light_service.backup()
    co2_service.backup()
    relay2_service.backup()
    schedule_backup()

def write_to_backup():
    with open('backup.ini', 'w') as backupfile:
        parser.write(backupfile)

@app.route('/')
@login_required
def index():
    saved_data = {'light_time1': parser.get('light', 'time1'),
                  'light_time2': parser.get('light', 'time2'),
                  'light_time3': parser.get('light', 'time3'),
                  'light_time4': parser.get('light', 'time4'),
                  'co2_time1': parser.get('co2', 'time1'),
                  'co2_time2': parser.get('co2', 'time2'),
                  'co2_time3': parser.get('co2', 'time3'),
                  'co2_time4': parser.get('co2', 'time4'),
                  'relay2_time1': parser.get('relay2', 'time1'),
                  'relay2_time2': parser.get('relay2', 'time2'),
                  'fertilizer_time': parser.get('fertilizer', 'time'),
                  'fertilizer_amount': parser.get('fertilizer', 'amount')}
    return render_template('index.html', data=saved_data)


@app.route('/test')
@login_required
def test_route():
    return render_template('test.html')


# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        for user in users:
            if user.password == password:
                id = user.id
                login_user(user)
                return redirect(request.args.get("next"))
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)


@socketio.on('connect')
def subscribe_to_aquarium():
    global schedule_thread
    if schedule_thread is None:
        print('Start thread')
        schedule_thread = socketio.start_background_task(target=run_schedule)
    mqtt.subscribe('home/aquarium/#')


@socketio.on('change_light_schedule')
def change_light_schedule(data):
    print(data)
    data = json.loads(data)
    print(data)
    turn_on_time1 = data['time1']
    turn_off_time2 = data['time2']
    turn_on_time3 = data['time3']
    turn_off_time4 = data['time4']
    schedule.clear('light')
    try:
        parser.set('light', 'time1', turn_on_time1)
        parser.set('light', 'time2', turn_off_time2)
        parser.set('light', 'time3', turn_on_time3)
        parser.set('light', 'time4', turn_off_time4)
        write_to_backup()
        schedule.every().day.at(turn_on_time1).do(light_service.turn_lights_on).tag('light')
        # schedule.every(3).seconds.do(light_service.turn_lights_on).tag('light')
        schedule.every().day.at(turn_off_time2).do(light_service.turn_lights_off).tag('light')
        # schedule.every(4).seconds.do(light_service.turn_lights_off).tag('light')
        if turn_on_time3 != '' and turn_off_time4 != '':
            schedule.every().day.at(turn_on_time3).do(light_service.turn_lights_on).tag('light')
            schedule.every().day.at(turn_off_time4).do(light_service.turn_lights_off).tag('light')
    except Exception as e:
        socketio.emit('error', e)

@socketio.on('turn_off_light')
def clean_light_schedule():
    schedule.clear('light')


@socketio.on('change_co2_schedule')
def change_co2_schedule(data):
    data = json.loads(data)
    turn_on_time1 = data['time1']
    turn_off_time2 = data['time2']
    turn_on_time3 = data['time3']
    turn_off_time4 = data['time4']
    schedule.clear('co2')
    try:
        parser.set('co2', 'time1', turn_on_time1)
        parser.set('co2', 'time2', turn_off_time2)
        parser.set('co2', 'time3', turn_on_time3)
        parser.set('co2', 'time4', turn_off_time4)
        write_to_backup()
        schedule.every().day.at(turn_on_time1).do(co2_service.open_co2).tag('co2')
        #schedule.every(3).seconds.do(co2_service.open_co2).tag('co2')
        schedule.every().day.at(turn_off_time2).do(co2_service.close_co2).tag('co2')
        #schedule.every(4).seconds.do(co2_service.close_co2).tag('co2')
        if turn_on_time3 != '' and turn_off_time4 != '':
            schedule.every().day.at(turn_on_time3).do(co2_service.open_co2).tag('co2')
            #schedule.every(3).seconds.do(co2_service.open_co2).tag('co2')
            schedule.every().day.at(turn_off_time4).do(co2_service.close_co2).tag('co2')
    except Exception as e:
        socketio.emit('error', e)

@socketio.on('turn_off_co2')
def clean_co2_schedule():
    schedule.clear('co2')

@socketio.on('change_fertilizer_schedule')
def change_fertilizer_schedule(data):
    data = json.loads(data)
    fertilizer_time = data['time']
    fertilizer_amount = data['amount']
    schedule.clear('fertilizer')
    try:
        parser.set('fertilizer', 'time', fertilizer_time)
        parser.set('fertilizer', 'amount', fertilizer_amount)
        write_to_backup()
        schedule.every().day.at(fertilizer_time).do(fertilizer_service.fertilize_sec, fertilizer_amount).tag('fertilizer')
        #schedule.every(4).seconds.do(fertilizer_service.fertilize_sec, fertilizer_amount).tag('fertilizer')
    except Exception as e:
        socketio.emit('error', e)

@socketio.on('turn_off_fertilizer')
def clean_fertilizer_schedule():
    schedule.clear('fertilizer')

@socketio.on('change_relay2_schedule')
def change_relay2_schedule(data):
    data = json.loads(data)
    print(data)
    turn_on_time = data['time1']
    turn_off_time = data['time2']
    schedule.clear('relay2')
    try:
        parser.set('relay2', 'time1', turn_on_time)
        parser.set('relay2', 'time2', turn_off_time)
        write_to_backup()
        schedule.every().day.at(turn_on_time).do(relay2_service.turn_relay2_on).tag('relay2')
        # schedule.every(3).seconds.do(relay2_service.turn_relay2s_on).tag('relay2')
        schedule.every().day.at(turn_off_time).do(relay2_service.turn_relay2_off).tag('relay2')
        # schedule.every(4).seconds.do(relay2_service.turn_relay2s_off).tag('relay2')
    except Exception as e:
        socketio.emit('error', e)

@socketio.on('turn_off_relay2')
def clean_relay2_schedule():
    schedule.clear('relay2')


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


@socketio.on('turn_relay2_on')
def turn_relay2_on_command():
    relay2_service.turn_relay2_on()


@socketio.on('turn_relay2_off')
def turn_relay2_off_command():
    relay2_service.turn_relay2_off()


@socketio.on('turn_motor_on')
def turn_motor_on_command():
    fertilizer_service.turn_motor_on()


@socketio.on('turn_motor_off')
def turn_motor_off_command():
    fertilizer_service.empty_tube()


@socketio.on('fertilize_secs')
def fertilize_secs_command(data):
    data = json.loads(data)
    fertilizer_amount = data['amount']
    fertilizer_service.fertilize_sec(fertilizer_amount)


@socketio.on('open_co2')
def open_co2_command():
    co2_service.open_co2()


@socketio.on('close_co2')
def close_co2_command():
    co2_service.close_co2()
#-------------------------------------------------------------------------------

# @mqtt.on_log()
# def handle_logging(client, userdata, level, buf):
#     #print(level, buf)
def run_schedule():
    run_backup()
    while True:
        schedule.run_pending()
        socketio.sleep(1)
    print('Schedule stopped')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8900,  use_reloader=True, debug=True)

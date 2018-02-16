import eventlet
import json
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET'] = ''
app.config['MQTT_BROKER_URL'] = '0.0.0.0'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5   # ping timeout interval (sec)
app.config['MQTT_TLS_ENABLED'] = False

mqtt = Mqtt(app)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

# connect
@socketio.on('connect')
def handle_socketio_connect():
    socketio.emit('dump', {'data': 'Client connected to SocketIO'})

# disconnect
@socketio.on('disconnect')
def handle_socketio_disconnect():
    print('Client disconnected from SocketIO')

@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'])
    socketio.emit('dump', {'data': 'Published to topic {}: {}'.format(data['topic'], data['message'])})

@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])
    socketio.emit('dump', {'data': 'Subscribed to topic {}'.format(data['topic'])})

@socketio.on('unsubscribe')
def handle_unsubscribe(json_str):
    data = json.loads(json_str)
    mqtt.unsubscribe(data['topic'])
    socketio.emit('dump', {'data': 'Unsubscribed from topic {}'.format(data['topic'])})

@mqtt.on_message()
def handle_mqtt_message(client, userdata, msg):
    data = dict(
        topic=msg.topic,
        payload=msg.payload.decode()
    )
    socketio.emit('mqtt_msg', data=data)

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=True, debug=True)
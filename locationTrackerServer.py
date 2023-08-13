from flask import Flask, request, jsonify
from flask_mqtt import Mqtt

import random
import time

app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = 'broker.emqx.io'
app.config['MQTT_BROKER_PORT'] = 1883
# Set this item when you need to verify username and password
app.config['MQTT_USERNAME'] = ''
# Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
# If your broker supports TLS, set it True
app.config['MQTT_TLS_ENABLED'] = False
topic = '/flask/mqtt'


# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'

mqtt_client = Mqtt(app)


# Sample user data
users = [
    {'email': 'a@a1.com', 'password': 'password1'},
    {'email': 'a@a2.com', 'password': 'password2'},
    {'email': 'a@a3.com', 'password': 'password3'},
    {'email': 'a@a4.com', 'password': 'password4'},
    {'email': 'a@a5.com', 'password': 'password5'}
]


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe(topic)  # subscribe topic
        mqtt_client.publish('/hello', 'I am Cooray')
    else:
        print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print(
        'Received message on topic: {topic} with payload: {payload}'.format(**data))


@app.route('/publish', methods=['POST'])
def publish_message():
    request_data = request.get_json()
    publish_result = mqtt_client.publish(
        request_data['topic'], request_data['msg'])
    return jsonify({'code': publish_result[0]})


@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password are required.'}), 400

    email = data['email']
    password = data['password']

    user = next((user for user in users if user['email'] == email), None)

    if user and user['password'] == password:
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

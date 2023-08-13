from flask import Flask, request, jsonify
from flask_mqtt import Mqtt

import random
import time
import json


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

topic_ontrip = '/crrtripdetails'


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

# on connect to broker


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe(topic_ontrip)  # subscribe topic
        mqtt_client.publish('/hello', 'I am Cooray')
    else:
        print('Bad connection. Code:', rc)

# handle mqtt incoming messages


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )

    # print(
    #     'Received message on topic: {topic} with payload: {payload}'.format(**data))

    if message.topic == topic_ontrip:
        # on trip details
        data_dict = json.loads(message.payload.decode())

        # Access individual values
        cr_uemail = data_dict['uemail']
        traveled_meters = data_dict['traveledmeters']
        cr_relapsed_time_seconds = data_dict['crrelapsedtimeseconds']

        print("Current user :", cr_uemail)
        print("Traveled Meters:", traveled_meters)
        print("CR Relapsed Time Seconds:", cr_relapsed_time_seconds)

# app route defulat


@app.route('/')
def hello_world():
    return 'Hello, Fiteness Tracker Backend on'

# test publish


@app.route('/publish', methods=['POST'])
def publish_message():
    request_data = request.get_json()
    publish_result = mqtt_client.publish(
        request_data['topic'], request_data['msg'])
    return jsonify({'code': publish_result[0]})

# user login app route


@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password are required.', 'status': 400}), 400

    email = data['email']
    password = data['password']

    user = next((user for user in users if user['email'] == email), None)

    if user and user['password'] == password:
        return jsonify({'message': 'Login successful', 'status': 200}), 200
    else:
        return jsonify({'message': 'Invalid email or password try again', 'status': 401}), 401


# user results
@app.route('/get_results', methods=['POST'])
def get_results():
    data = request.get_json()

    if not data or 'email' not in data:
        return jsonify({'message': 'Email  are required.', 'status': 400}), 400

    email = data['email']

    # get asking user data

    # 1 distance should be  in  meters
    # 2 calories hould be number
    # 3 time should send as seconds

    sendRet = [1200, 500, 67000,   'Explore the scenic beauty of the countryside with a weekend getaway',
               'Delve into the world of classic literature with a novel by Jane Austen',
               'Embark on a culinary adventure and try your hand at cooking Thai cuisine',]

    return jsonify({'message': sendRet, 'status': 200}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

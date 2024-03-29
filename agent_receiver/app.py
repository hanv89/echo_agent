# import eventlet
# eventlet.monkey_patch()

import json

from flask import Flask, render_template, session, request
from kafka import KafkaProducer

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
producer = KafkaProducer(bootstrap_servers='localhost:9092',value_serializer=lambda m: json.dumps(m, separators=(',', ':')).encode('utf-8'))

@app.route('/send', methods=['POST'])
def send_msg():
    data = request.get_json()
    print(data)
    message = data.get('message','Empty response!')
    sid = data.get('sid', '')
    session['receive_count'] = session.get('receive_count', 0) + 1

    data_message = {'data': 'agent_receiver said: '+message, 'count': session['receive_count'],'sid':sid}
    producer.send('to_bot', data_message)

    return {
        'message':message,
        'code': 0
    }
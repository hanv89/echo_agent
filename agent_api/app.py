#!/usr/bin/env python
import eventlet
eventlet.monkey_patch()
import json
import requests

from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode, message_queue='amqp://')

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route('/send', methods=['POST'])
def send_msg():
    data = request.get_json()
    print(data)
    message = data.get('message','Empty response!')
    socketio.emit('my_event', {'data': message}, namespace='/test')

    return {
        'message':message,
        'code': 0
    }

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'api said: '+message['data'], 'count': session['receive_count']}, broadcast=True)

    print('asking:' + message['data'])
    response = requests.post('http://localhost:5012/send', json={'message':message['data'],'sid':request.sid})
    json_response = response.json()
    print('json_response:' + json.dumps(json_response))

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.on('my_ping', namespace='/test')
def ping_pong():
    emit('my_pong')


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5010)

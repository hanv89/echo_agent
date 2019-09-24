# import eventlet
# eventlet.monkey_patch()

from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(async_mode=async_mode, message_queue='redis://')

@app.route('/send', methods=['POST'])
def send_msg():
    data = request.get_json()
    print(data)
    message = data.get('message','Empty response!')
    session['receive_count'] = session.get('receive_count', 0) + 1

    socketio.emit('my_response',
         {'data': 'receiver said: '+message, 'count': session['receive_count']}, namespace='/test')
    return {
        'message':message,
        'code': 0
    }
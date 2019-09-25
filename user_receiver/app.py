# import eventlet
# eventlet.monkey_patch()

from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(async_mode=async_mode, message_queue='amqp://')

@app.route('/send', methods=['POST'])
def send_msg():
    data = request.get_json()
    message = data.get('message','Empty response!')
    sid = data.get('sid', '')
    print('message:' + message)
    session['receive_count'] = session.get('receive_count', 0) + 1

    socketio.emit('my_response',
         {'data': 'from ' + sid + ':user_receiver said: '+message, 'count': session['receive_count'],'sid':sid}, namespace='/test', room=sid)

    return {
        'message':message,
        'code': 0
    }
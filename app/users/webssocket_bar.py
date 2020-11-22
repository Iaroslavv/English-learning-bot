from app import socketio
from flask_login import current_user
from flask_socketio import emit
import json


@socketio.on('my event')
def receive__message(message):
    emit('my response', {'data': 'Backend saw "' + json.dumps(message['data']) + '" from the frontend'})
    print("Received from message data:" + json.dumps(message['data']))
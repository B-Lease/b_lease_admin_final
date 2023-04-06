from flask_socketio import SocketIO, send, emit
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

app.secret_key = "b-lease2022"
#=====================================================
CORS(app)


socketio = SocketIO(app, async_mode='gevent', engineio_logger=True, cors_allowed_origins='*')



@socketio.on('disconnect')
def handle_disconnect():
    emit('users-changed', {'user': 'allain', 'event': 'left'})

@socketio.on('set-nickname')
def handle_set_nickname(data):
    nickname = 'allain'
    emit('users-changed', {'user': nickname, 'event': 'joined'}, broadcast=True)
    app.flask.session['nickname'] = nickname

@socketio.on('add-message')
def handle_add_message(data):
    emit('message', {'leasingID': data['leasingID'], 'msg_senderID': data['msg_senderID'],'msg_receiverID': data['msg_receiverID'], 'msg_content': data['msg_content'], 'sent_at': data['sent_at']}, broadcast=True)

if __name__ == "__main__":
#     # server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
#     # server.serve_forever()
    from geventwebsocket.handler import WebSocketHandler
    from gevent.pywsgi import WSGIServer
    
    http_server = WSGIServer(('0.0.0.0', 5001,), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, join_room, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# IMPORTANT: threading mode (no eventlet)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

rooms = {}
clients = {}
messages = {}   # in-memory messages


@app.route('/')
def home():
    return render_template('index.html')


# JOIN ROOM
@socketio.on('join')
def on_join(data):
    username = data['user']
    room = data['room']
    sid = request.sid

    join_room(room)

    # store client
    clients[sid] = {"user": username, "room": room}

    # add to room
    if room not in rooms:
        rooms[room] = []
    if username not in rooms[room]:
        rooms[room].append(username)

    # send user list
    emit('user_list', rooms[room], to=room)

    # send old messages
    if room in messages:
        for msg in messages[room]:
            emit('message', msg)

    send(f"{username} joined {room}", to=room)


# SEND MESSAGE
@socketio.on('message')
def handle_message(data):
    room = data['room']

    # store messages
    if room not in messages:
        messages[room] = []
    messages[room].append(data)

    send(data, to=room)


# DISCONNECT
@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid

    if sid in clients:
        user = clients[sid]['user']
        room = clients[sid]['room']

        if room in rooms and user in rooms[room]:
            rooms[room].remove(user)

        emit('user_list', rooms.get(room, []), to=room)
        send(f"{user} left the room", to=room)

        del clients[sid]


# RUN APP (Railway compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
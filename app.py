import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, join_room, emit
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# IMPORTANT for deployment
socketio = SocketIO(app, cors_allowed_origins="*")

# store users
rooms = {}
clients = {}

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

    # store client info
    clients[sid] = {"user": username, "room": room}

    # add user to room
    if room not in rooms:
        rooms[room] = []
    if username not in rooms[room]:
        rooms[room].append(username)

    # send updated user list
    emit('user_list', rooms[room], to=room)

    # load old messages
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute("SELECT username, message FROM messages WHERE room=?", (room,))
    old_msgs = c.fetchall()
    conn.close()

    for msg in old_msgs:
        emit('message', {'user': msg[0], 'text': msg[1]})

    send(f"{username} joined {room}", to=room)


# SEND MESSAGE
@socketio.on('message')
def handle_message(data):
    username = data['user']
    room = data['room']
    message = data['text']

    # save message
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (username, room, message) VALUES (?, ?, ?)",
        (username, room, message)
    )
    conn.commit()
    conn.close()

    send(data, to=room)


# DISCONNECT (remove user)
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


# RUN APP (IMPORTANT FOR RAILWAY)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
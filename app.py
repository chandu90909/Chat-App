from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, join_room, leave_room, emit
import sqlite3
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
rooms = {}
clients = {}   # NEW

@app.route('/')
def home():
    return render_template('index.html')


# JOIN ROOM
@socketio.on('join')
def on_join(data):
    username = data['user']
    room = data['room']
    sid = request.sid   # unique session id

    join_room(room)

    # store client info
    clients[sid] = {"user": username, "room": room}

    # add user to room list
    if room not in rooms:
        rooms[room] = []
    rooms[room].append(username)

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


# DISCONNECT (FIXED)
@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid

    if sid in clients:
        user = clients[sid]['user']
        room = clients[sid]['room']

        # remove user
        if room in rooms and user in rooms[room]:
            rooms[room].remove(user)

        # update user list
        emit('user_list', rooms[room], to=room)

        send(f"{user} left the room", to=room)

        del clients[sid]


# SEND MESSAGE
@socketio.on('message')
def handle_message(data):
    username = data['user']
    room = data['room']
    message = data['text']

    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (username, room, message) VALUES (?, ?, ?)",
              (username, room, message))
    conn.commit()
    conn.close()

    send(data, to=room)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
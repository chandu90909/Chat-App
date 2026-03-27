from flask import Flask, render_template, request, redirect

app = Flask(__name__)

rooms = {}  # {room_name: [messages]}

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/join', methods=['POST'])
def join():
    username = request.form['username']
    room = request.form['room']

    if room not in rooms:
        rooms[room] = []

    return redirect(f"/chat?username={username}&room={room}")


@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    messages = rooms.get(room, [])

    return render_template('chat.html', username=username, room=room, messages=messages)


@app.route('/send', methods=['POST'])
def send():
    username = request.form['username']
    room = request.form['room']
    message = request.form['message']

    rooms[room].append(f"{username}: {message}")

    return redirect(f"/chat?username={username}&room={room}")
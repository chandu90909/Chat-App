from flask import Flask, render_template, request, redirect

app = Flask(__name__)

messages = []

@app.route('/')
def home():
    return render_template('index.html', messages=messages)

@app.route('/send', methods=['POST'])
def send():
    username = request.form['username']
    message = request.form['message']

    messages.append(f"{username}: {message}")

    return redirect('/')
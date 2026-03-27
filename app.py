from flask import Flask, render_template, request, redirect
import os

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

# IMPORTANT for Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
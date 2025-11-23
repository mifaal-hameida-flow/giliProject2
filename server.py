from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect, url_for
import asyncio
import bcrypt
import random
from shazamio import Shazam

app = Flask(__name__)
app.secret_key = 'secretkey'
# 
# This is a dictionary that will hold the user credentials. In a real application, this should be stored in a database.
def read_users_file():
    with open('users.txt', 'r') as f:
        lines = f.readlines()
        users = {}
        for line in lines:
            username, password = line.strip().split(',')
            users[username] = password
        return users

users = read_users_file()


@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('shazam'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    users = read_users_file()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username].encode('utf-8')):
            session['username'] = username
            return redirect(url_for('shazam'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/export', methods=['GET'])
def export():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Read the data from the TXT file
    with open('history/'+session['username']+'.txt', 'r') as file:
        txt_content = file.read()

    # Render the HTML template with the data
    return render_template('export.html', txt_content=txt_content)


def is_username_taken(username):
    with open('users.txt', 'r') as f:
        for line in f:
            existing_username, _ = line.strip().split(',')
            if existing_username == username:
                return True
    return False

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    error_username = None
    error_password = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if is_username_taken(username):
            error_username = 'Username already taken'

        if password != confirm_password:
            error_password = 'Passwords do not match'

        if error_username or error_password:
            return render_template('create_user.html', error_username=error_username, error_password=error_password)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        with open('users.txt', 'a') as f:
            f.write(f"{username},{hashed_password.decode('utf-8')}\n")

        return redirect(url_for('login'))

    return render_template('create_user.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/shazam')
def shazam():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('shazam.html')



@app.route('/static/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file found'}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected audio file'}), 400

    random_number = random.randint(1, 1000000)
    filename = 'uploads/file'+str(random_number)+'.mp3'
    audio_file.save(filename)
    out = loop.run_until_complete(recognize(filename))

    if ('track' in out):
        # with open('history/' + session['username'] + '.txt', 'a') as f:
        #    f.write(f"{out['track']}\n")
        # return out, 200
        track = out['track']
        result = {
            'title': track['title'],
            'subtitle': track['subtitle'],
            'image': track['images']['coverarthq']
        }
        with open('history/' + session['username'] + '.txt', 'a') as f:
            f.write(f"{track['title']},{track['subtitle']},{track['images']['coverarthq']}\n")
        # Redirect to the results page with the result parameter in the URL
        return jsonify(result), 200

    else:
         return jsonify({'error': 'No track found'}), 400


async def recognize(filename):
  shazam = Shazam()
  out = await shazam.recognize_song(filename)
  return out




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    context = ('cert.pem', 'key.pem')
   # app.run(host='0.0.0.0', port=443, ssl_context=context)
    app.run(host='0.0.0.0', port=80)


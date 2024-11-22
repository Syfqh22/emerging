from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  
WEBEX_API_BASE = 'https://webexapis.com/v1'  

def get_user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{WEBEX_API_BASE}/people/me', headers=headers)
    return response.json() if response.status_code == 200 else None

def get_rooms(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{WEBEX_API_BASE}/rooms', headers=headers)
    return response.json().get('items', []) if response.status_code == 200 else None

def send_message(access_token, room_id, text):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {'roomId': room_id, 'text': text}
    response = requests.post(f'{WEBEX_API_BASE}/messages', headers=headers, json=data)
    return response.status_code == 200

def create_webex_room(access_token, title):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {'title': title}
    response = requests.post(f'{WEBEX_API_BASE}/rooms', headers=headers, json=data)
    return response.status_code == 200

def delete_webex_room(access_token, room_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(f'{WEBEX_API_BASE}/rooms/{room_id}', headers=headers)
    return response.status_code == 204

def test_webex_connection(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{WEBEX_API_BASE}/people/me', headers=headers)
    return response.status_code == 200

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        access_token = request.form.get('access_token')
        user_info = get_user_info(access_token)
        if user_info:
            return redirect(url_for('menu', access_token=access_token))
        else:
            flash("Invalid access token. Please try again.", "error")
            return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/menu/<access_token>', methods=['GET'])
def menu(access_token):
    user_info = get_user_info(access_token)  
    return render_template('menu.html', access_token=access_token, user_info=user_info)

@app.route('/rooms/<access_token>', methods=['GET'])
def rooms(access_token):
    rooms = get_rooms(access_token)
    if rooms is not None:
        return render_template('rooms.html', rooms=rooms[:5], access_token=access_token)
    return "Failed to retrieve rooms.", 400

@app.route('/create_room/<access_token>', methods=['POST'])
def create_room(access_token):
    title = request.form.get('title')
    success = create_webex_room(access_token, title)
    if success:
        return redirect(url_for('rooms', access_token=access_token))
    return "Failed to create room.", 400

@app.route('/send_message/<access_token>', methods=['POST'])
def send_message_route(access_token):
    room_id = request.form.get('room_id')
    message = request.form.get('message')
    if send_message(access_token, room_id, message):
        flash('Message sent successfully!', 'success')
    else:
        flash('Failed to send message.', 'error')
    return redirect(url_for('rooms', access_token=access_token))

@app.route('/delete_room/<access_token>/<room_id>', methods=['POST'])
def delete_room(access_token, room_id):
    success = delete_webex_room(access_token, room_id)
    if success:
        return redirect(url_for('rooms', access_token=access_token))
    return "Failed to delete room.", 400

@app.route('/test_connection/<access_token>', methods=['GET'])
def test_connection(access_token):
    success = test_webex_connection(access_token)
    return jsonify({"success": success})

@app.route('/video_call', methods=['GET'])
def video_call():
    room_name = "Conference Room"  
    return render_template('video_call.html', room_name=room_name)

@app.route('/logout', methods=['GET'])
def logout():
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

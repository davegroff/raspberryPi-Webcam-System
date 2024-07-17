import sys
import time
import signal
import threading
import subprocess
import http.server
import socketserver
from flask_cors import CORS
from flask import Flask, request
from flask_socketio import SocketIO, emit


# Flask-SocketIO server setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionary to store usernames/IDs mapped to socket IDs
user_sessions = {}

@socketio.on('message')
def handle_message(message):
    socket_id = request.sid
    client_ip = request.remote_addr
    client_port = request.environ.get('REMOTE_PORT')
    message_with_ip = message.copy()  # Create a copy of the message
    message_with_ip['peerId'] = f"{client_ip}"
    message_with_ip['sid'] = socket_id
    peerToSend = message.get('to')
    
        
    if peerToSend:
        peer_socket_id = user_sessions.get(peerToSend)
        if peer_socket_id:
            emit('message', message_with_ip, to=peer_socket_id)
        else:
            emit('message', {'error': 'User not found or not connected'}, to=socket_id)
    else:
        emit('message', message_with_ip, broadcast=True)
    
    # Check for the "restart": true key-value pair and run program.py if present
    if message.get('restart') is True:
        service_name = "chromium.service"
        try:
            subprocess.call(["sudo", "systemctl", "restart", service_name])
            print(f"Successfully restarted the '{service_name}' service.")
        except subprocess.CalledProcessError as e:
            print(f"Error restarting the '{service_name}' service: {e}")

@socketio.on('connect')
def test_connect():
    socket_id = request.sid
    auth = request.args  # Get the auth data from the request arguments
    emit('message', auth, broadcast=True)
    username = auth.get('username')
    if username:
        user_sessions[username] = socket_id

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
    socket_id = request.sid
    client_ip = request.remote_addr
    client_port = request.environ.get('REMOTE_PORT')
    
	# Remove the disconnected user from the user_sessions
    for username, sid in list(user_sessions.items()):
        if sid == socket_id:
            del user_sessions[username]
            
    message = {
        'sid': socket_id,
        'peerId': f"{client_ip}:{client_port}",
        'type': "disconnected"
    }
    emit('message', message, broadcast=True)
    
    

def run_socketio():
    try:
        print("Flask SocketIO server is running on port", 5001)
        socketio.run(app, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"SocketIO server error: {e}")

# HTTP server setup
PORT = 9000

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'sender.html'
        elif self.path == '/stream':
            self.path = 'receiver.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def run_http_server():
    Handler = MyHttpRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("HTTP Server Serving at port", PORT)
        try:
            httpd.serve_forever()
        except Exception as e:
            print(f"HTTP server error: {e}")

# Graceful shutdown handling
def signal_handler(sig, frame):
    print('Shutting down servers...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Running both servers concurrently using threading
if __name__ == '__main__':
    # Create threads for each server
    socketio_thread = threading.Thread(target=run_socketio)
    http_thread = threading.Thread(target=run_http_server)

    # Start both threads
    socketio_thread.start()
    http_thread.start()
    
    time.sleep(3)
    
    # try:
    #     subprocess.Popen(['python', 'program.py'])
    #     print("program.py started successfully")
    # except Exception as e:
    #     print(f"Failed to start program.py: {e}")

    # Join threads to the main thread
    socketio_thread.join()
    http_thread.join()
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

@socketio.on('message')
def handle_message(message):
    socket_id = request.sid
    client_ip = request.remote_addr
    client_port = request.environ.get('REMOTE_PORT')
    message_with_ip = message.copy()  # Create a copy of the message
    message_with_ip['peerId'] = f"{client_ip}:{client_port}"
    message_with_ip['sid'] = socket_id
    peerToSend = message.get('to')
    emit('message', message_with_ip, to=peerToSend, broadcast=True)
    
    # Check for the "restart": true key-value pair and run program.py if present
    if message.get('restart') is True:
        try:
            subprocess.Popen(['python3', 'program.py'])
            print("program.py started successfully")
        except Exception as e:
            print(f"Failed to start program.py: {e}")

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
    socket_id = request.sid
    client_ip = request.remote_addr
    client_port = request.environ.get('REMOTE_PORT')
    message = {
        'sid': socket_id,
        'peerId': f"{client_ip}:{client_port}",
        'type': "disconnected"
    }
    emit('message', message, broadcast=True)

def run_socketio():
    try:
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
    
    time.sleep(10)
    
    try:
        subprocess.Popen(['python', 'program.py'])
        print("program.py started successfully")
    except Exception as e:
        print(f"Failed to start program.py: {e}")

    # Join threads to the main thread
    socketio_thread.join()
    http_thread.join()
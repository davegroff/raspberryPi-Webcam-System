import sys
import time
import signal
import threading
import subprocess
import http.server
import socketserver
import socket
from flask_cors import CORS
from flask import Flask, request
from flask_socketio import SocketIO, emit
import re


# Flask-SocketIO server setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionary to store usernames/IDs mapped to socket IDs
user_sessions = {}

def get_local_ip():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        # Validate IP address to ensure it's not the loopback address
        if local_ip.startswith("127."):
            raise ValueError("IP address is a loopback address")
    except Exception:
        # Fallback method if hostname resolution returns loopback address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("192.168.254.1", 80))  # This should be the IP address of the LAN router
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = "127.0.0.1"
        finally:
            s.close()
    return local_ip

# Get the local IP address
local_ip = get_local_ip()
print(f"Local IP address is: {local_ip}")

def modify_sdp(sdp, new_ip):
    """
    Modify the SDP to replace all instances of 127.0.0.1 with the new IP.
    """
    return re.sub(r'127\.0\.0\.1', new_ip, sdp)

@socketio.on('message')
def handle_message(message):
    socket_id = request.sid
    client_ip = request.remote_addr
    client_port = request.environ.get('REMOTE_PORT')
    message_with_ip = message.copy()  # Create a copy of the message
    
    # Check if the message contains an offer and the offer contains an SDP
    if 'offer' in message and 'sdp' in message['offer']:
        original_sdp = message['offer']['sdp']
        new_ip = local_ip  # Use the local IP address
        modified_sdp = modify_sdp(original_sdp, new_ip)
        message_with_ip['offer']['sdp'] = modified_sdp
   
    message_with_ip['sid'] = socket_id
    peerToSend = message.get('to')
    username = message.get('username')
    message_with_ip['peerId'] = username
    if client_ip.startswith("127."):
        client_ip = local_ip
    message_with_ip['peerIPAddress'] = f"{client_ip}:{client_port}"
    
    if username:
        user_sessions[username] = socket_id
        
    if peerToSend:
        peer_socket_id = user_sessions.get(peerToSend)
        if peer_socket_id:
            emit('message', message_with_ip, to=peer_socket_id)
        else:
            emit('message', message_with_ip, broadcast=True)
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
	print('client connected')
    

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')
    socket_id = request.sid
    client_ip = request.remote_addr
    client_port = request.environ.get('REMOTE_PORT')
    
    savedUsername = ""
	# Remove the disconnected user from the user_sessions
    for username, sid in list(user_sessions.items()):
        if sid == socket_id:
            savedUsername = username
            del user_sessions[username]
            
    message = {
        'sid': socket_id,
        'peerId': savedUsername,
        'peerIPAddress': f"{client_ip}:{client_port}",
        'type': "disconnected"
    }
    emit('message', message, broadcast=True)
    
    

def run_socketio():
    try:
        print("Flask SocketIO server is running on port", 5001)
        socketio.run(app, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"SocketIO server error: {e}")
        
async def handle_stun_request(reader, writer):
    data = await reader.read(1024)
    addr = writer.get_extra_info('peername')
    print(f"Received {data!r} from {addr!r}")
    
    response = stun.build_response(data, addr[0], addr[1])
    writer.write(response)
    await writer.drain()
    writer.close()

async def run_stun_server():
    server = await asyncio.start_server(handle_stun_request, '0.0.0.0', 3478)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

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
    stun_thread = threading.Thread(target=run_stun_server)
    http_thread = threading.Thread(target=run_http_server)

    # Start all threads
    socketio_thread.start()
    stun_thread.start()
    http_thread.start()
    
    time.sleep(3)
    
    # try:
    #     subprocess.Popen(['python', 'program.py'])
    #     print("program.py started successfully")
    # except Exception as e:
    #     print(f"Failed to start program.py: {e}")

    # Join threads to the main thread
    socketio_thread.join()
    stun_thread.join()
    http_thread.join()
    
	
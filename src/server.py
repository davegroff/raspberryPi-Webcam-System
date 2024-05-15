import cv2
from flask_cors import CORS
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from flask import Flask, render_template, request, jsonify

# Create a Flask app instance
app = Flask(__name__, static_url_path='/static')

CORS(app)

# Set to keep track of RTCPeerConnection instances
pcs = set()

class CameraVideoTrack(MediaStreamTrack):
    """
    A video stream track that captures video frames from a webcam.
    """
    kind = "video"

    def __init__(self, camera):
        super().__init__()
        self.camera = camera

    async def recv(self):
        frame = self._get_next_frame()
        return frame

    def _get_next_frame(self):
        success, frame = self.camera.read()
        if success:
            # Convert the image format for transmission
            return cv2.imencode('.jpg', frame)[1].tobytes()
        else:
            raise Exception("Failed to capture camera frame")

# Route to render the HTML template
@app.route('/')
def index():
    return render_template('index.html')

# Asynchronous function to handle offer exchange
async def offer_async():
    params = request.json
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    # Create an RTCPeerConnection instance
    pc = RTCPeerConnection()

    # Open the first video device
    camera = cv2.VideoCapture(0)

    # Add camera video track to the peer connection
    video_track = CameraVideoTrack(camera)
    pc.addTrack(video_track)

    # Add the peer connection to the set
    pcs.add(pc)

    await pc.setRemoteDescription(offer)

    # Create and set the local description
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Prepare the response data with local SDP and type
    response_data = {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

    return jsonify(response_data)

# Route to handle the offer request
@app.route('/offer', methods=['POST'])
async def offer_route():
    return await offer_async()

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

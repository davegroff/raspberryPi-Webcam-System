# LiveStream-WebRTC-Flask-OpenCV

#### Prerequisistes
* Webcam/ IP camera
* A server machine and a client machine (smartphone, pc, etc.) connected to the same network.
  `python3 -m venv .venv`

  `source .venv/bin/activate`

  `pip install Flask`

  `pip install opencv-python-headless`

  `pip install aiortc`

* Client Side<br>
To view the live stream from a Server's webcam/IP camera in a client machine, simply open a web browser and type `http://127.0.0.1:<port>/` (client on same machine) OR `http://<server_IP_address>:<port>/` (client on different machine). 

#### Note
* Camera access should be enabled on Server
* Client machine should be connected to the same network as the server machine.
* Set host and port according to your needs. Port should not be running any other processes (details to fix conflicting ports in story)



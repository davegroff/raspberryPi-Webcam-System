## RaspberryPi Webcam System Setup Instructions

### Clone Repository
Clone the repository inside the `/home/pi/Downloads` folder using the following command:
```bash
git clone https://github.com/davegroff/raspberryPi-Webcam-System.git
```

### Startup Script and Systemd Service Configuration

1. **Set Executable Permissions:**
   Run the command below to set executable permissions for the startup script:
   ```bash
   sudo chmod +x /home/pi/Downloads/raspberryPi-Webcam-System/startup.sh
   ```

2. **Create/Update the Systemd Service:**

   Open and edit the systemd service file by running:
   ```bash
   sudo nano /etc/systemd/system/webcam.service
   ```

   Paste the following content into the file:
   ```ini
   [Unit]
   Description=RaspberryPi5 Webcam System
   After=network-online.target

   [Service]
   WorkingDirectory=/home/pi/Downloads/raspberryPi-Webcam-System
   ExecStart=/home/pi/Downloads/raspberryPi-Webcam-System/startup.sh
   Restart=always
   StandardOutput=syslog
   StandardError=syslog
   SyslogIdentifier=main_service
   
   [Service]
   WorkingDirectory=/home/pi/Downloads/raspberryPi-Webcam-System
   ExecStart=/usr/bin/python3 /home/pi/Downloads/raspberryPi-Webcam-System/program.py
   Restart=always
   StandardOutput=syslog
   StandardError=syslog
   SyslogIdentifier=chromium_service
   After=main_service.service
   Requires=main_service.service

   [Install]
   WantedBy=multi-user.target
   ```

3. **Reload Systemd Daemon and Manage the Service:**
   Run the following commands to reload the systemd daemon, enable, start, and check the status of the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable webcam.service
   sudo systemctl start webcam.service
   sudo systemctl status webcam.service
   ```

### Access the System
Open a web browser and go to `localhost:9000` to serve the video stream from Raspberry Pi
To see the stream, launch browser and go to `localhost:9000/stream`

Follow these steps meticulously to ensure a seamless setup and management of the RaspberryPi Webcam System as a Systemd service on your Raspberry Pi device.  
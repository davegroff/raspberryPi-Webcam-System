### Startup Script and Systemd Service Configuration

1. **Set Executable Permissions:**
   ```bash
   sudo chmod +x /home/pi/Downloads/raspberryPi-Webcam-System/startup.sh
   ```

2. **Create/Update the Systemd Service:**
   ```bash
   sudo nano /etc/systemd/system/startup.service
   ```

   **Systemd Unit File:**
   ```ini
   [Unit]
   Description=RaspberryPi5 Webcam System
   After=network.target

   [Service]
   WorkingDirectory=/home/pi/Downloads/raspberryPi-Webcam-System
   ExecStart=/home/pi/Downloads/raspberryPi-Webcam-System/startup.sh
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Reload Systemd Daemon and Manage the Service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable startup.service
   sudo systemctl start startup.service
   sudo systemctl status startup.service
   ```

By following these steps, you can set up and manage the RaspberryPi5 Webcam System as a Systemd service, ensuring its proper execution and management during system startup and operation.  
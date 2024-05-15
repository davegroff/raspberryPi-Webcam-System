# cam2jitsi

Directly stream a webcam into a jitsi room.

Intended to run headless on a Raspberry Pi

## Requirements

* Hardware: Raspberry Pi
  * Runs fine with a 720p cam on a Pi 2
* OS: Raspberry Pi OS Lite

* Software:
  * chromium
  * chromium-codecs-ffmpeg
  * npm
  * puppeteer

* Script:
  * stream.js (from this repo)


## Installation
Run on Pi:

```
sudo apt-get update
sudo apt-get install chromium-browser chromium-codecs-ffmpeg npm git
npm i puppeteer
git clone https://github.com/yggi/cam2jitsi.git
```

## Configuration

Set the default jitsi link and screen name in stream.js:

```
vi cam2jitsi/stream.js
````

## Execution

### Manual Start

```
node cam2jitsi/stream.js <JITSI-LINK> <NAME>
````

### Autostart

Add to rc.local (before final "exit 0" line):

```
node /home/pi/cam2jitsi/stream.js <JITSI-LINK> <NAME> &
```


## License

Released as Public Domain under CC0-License

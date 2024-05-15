const puppeteer = require('puppeteer');


// Streams the first webcam in the system to the specified Jitsi Meet room. Audio is currently
// not sent, but it can be easily enabled by disabling the corresponding setting in `meetArgs`.
//
// TODO
//   - Detect if we are kicked from the room
//   - Support authenticated deployments
//
// NOTE: only tested on GNU/Linux.
// original script from https://code.saghul.net/2017/09/streaming-a-webcam-to-a-jitsi-meet-room/
// extended by iggy@yggi.de

default_url="https://meet.jit.si/test123";
default_name="streamer";

async function main(base_url,name) {
    console.log(`Starting stream to ${base_url} as ${name}`);
    const chromeArgs = [
        // Disable sandboxing, gives an error on Linux
        '--no-sandbox',
        '--disable-setuid-sandbox',
        // Automatically give permission to use media devices
        '--use-fake-ui-for-media-stream',
        // Silence all output, just in case
        '--alsa-output-device=plug:null'
    ];
    const meetArgs = [
        // Disable receiving of video
        'config.channelLastN=0',
        // Mute our audio
        'config.startWithAudioMuted=true',
        // Don't use simulcast to save resources on the sender (our) side
        'config.disableSimulcast=true',
        // No need to process audio levels
        'config.disableAudioLevels=true',
        // Disable P2P mode due to a bug in Jitsi Meet
        'config.p2p.enabled=false',
	// Set display name
        'userInfo.displayName="'+name+'"',
	// Skip prejoin page
        'config.prejoinPageEnabled=false'
    ];
    const url = `${base_url}#${meetArgs.join('&')}`;
    console.log(`Loading ${url}`);

    const browser = await puppeteer.launch({ args: chromeArgs, executablePath: '/usr/bin/chromium-browser', handleSIGINT: false });
    console.log('browser started');
    const page = await browser.newPage();
    console.log('page loaded');
    // Manual handling on SIGINT to gracefully hangup and exit
    process.on('SIGINT', async () => {
        console.log('Exiting...');
        await page.evaluate('APP.conference.hangup();');
        await page.close();
        browser.close();
        console.log('Done!');
        process.exit();
    });

    await page.goto(url);
    console.log('Running...');
}

const url = process.argv[2] || default_url;
const name = process.argv[3] || default_name;
main(url,name);

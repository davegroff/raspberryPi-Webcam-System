import asyncio
import requests
from time import sleep
from pyppeteer.errors import NetworkError
from pyppeteer import launcher, launch, connect

async def check_open_browser():
    try:
        response = requests.get('http://localhost:9222/json/version')
        if response.status_code == 200:
            ws_endpoint = response.json().get('webSocketDebuggerUrl')
            return ws_endpoint
    except requests.exceptions.RequestException:
        return None

async def scraper():
    ws_endpoint = await check_open_browser()
    
    if ws_endpoint:
        print("Closing existing browser...")
        browser = await connect(browserWSEndpoint=ws_endpoint)


    else:
        print("Launching new browser...")
        launcherX = launcher.Launcher({
        "headless": False,
        "executablePath": '/usr/bin/chromium-browser',
        "args": ['--remote-debugging-port=9222', '--auto-accept-camera-and-microphone-capture']})
        launcherX.port = '9222'
        launcherX.url = f'http://127.0.0.1:{launcherX.port}'
        browser = await launcherX.launch()
        # browser = await launch({"headless": False, "executablePath": '/usr/bin/chromium-browser', "args":['--auto-accept-camera-and-microphone-capture' ]})
    
    sleep(2)
    print("opening Page")
    pages = await browser.pages()

    # Set content security policy to allow media access
    # await pages[0].setExtraHTTPHeaders({
    #   'Content-Security-Policy': "default-src 'self' 'unsafe-inline' blob: data:; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data:;"
    # })

    try:
        await pages[0].goto('http://localhost:9000/',{'waitUntil' : 'domcontentloaded'})
    except Exception as error:
        print(error)

    # await browser.close()

asyncio.run(scraper())
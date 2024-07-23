import asyncio
import subprocess
import requests
from time import sleep
from pyppeteer import launcher, launch, connect


async def close_chrome_instances():
    try:
        subprocess.run(['pkill', '-f', 'chromium-browser'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error closing Chrome instances: {e}")
        
async def check_open_browser():
    try:
        response = requests.get('http://localhost:9222/json/version')
        if response.status_code == 200:
            ws_endpoint = response.json().get('webSocketDebuggerUrl')
            return ws_endpoint
    except requests.exceptions.RequestException:
        return None

async def close_dialog(dialog):
            await dialog.dismiss()
            
async def scraper():
    
     
	ws_endpoint = await check_open_browser()
    
	if ws_endpoint:
		print("Closing existing browser...")
		await close_chrome_instances()
		#browser = await connect(browserWSEndpoint=ws_endpoint)
	
	print("Launching new browser...")
	launcherX = launcher.Launcher({
		"headless": True,
		"executablePath": '/usr/bin/chromium-browser',
		"loop": asyncio.get_running_loop(),
		"autoClose": False,
		"args": ['--remote-debugging-port=9222', '--auto-accept-camera-and-microphone-capture'],
	})
	launcherX.port = '9222'
	launcherX.url = f'http://127.0.0.1:{launcherX.port}'
	browser = await launcherX.launch()
    
	await asyncio.sleep(5)
	pages = await browser.pages()

    # Set content security policy to allow media access
    # await pages[0].setExtraHTTPHeaders({
    #   'Content-Security-Policy': "default-src 'self' 'unsafe-inline' blob: data:; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: data:;"
    # })
	print("Opening Page...")
	try:
		pages[0].on(
            'dialog',
            lambda dialog: asyncio.ensure_future(close_dialog(dialog))
        )
		await pages[0].goto('http://localhost:9000/', {'waitUntil' : 'domcontentloaded'})
		while True: pass
	except Exception as error:
		print(error)

    # await browser.close()

asyncio.run(scraper())
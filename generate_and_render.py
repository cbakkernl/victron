# generate_and_render.py
import datetime
import os
import asyncio
import subprocess
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Laad .env variabelen
load_dotenv()
PUBLISH_TO_GITHUB = os.getenv("PUBLISH_TO_GITHUB", "false").lower() == "true"
REPO_PATH = os.getenv("REPO_PATH", ".")
OUTPUT_HTML = os.path.join(REPO_PATH, "status.html")
OUTPUT_PNG = os.path.join(REPO_PATH, "battery_status.png")

# Dummy/mock data – later te vervangen door echte data
DATA = {
    'battery_percentage': 76.3,
    'power_usage_watt': 1234,
    'solar_input_watt': 543,
    'uptime': '5d 14h',
    'last_updated': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
}

def generate_html():
    env = Environment(loader=FileSystemLoader(os.path.join(REPO_PATH, 'templates')))
    template = env.get_template('template.html')
    rendered = template.render(**DATA)
    with open(OUTPUT_HTML, 'w') as f:
        f.write(rendered)
    print(f"✅ HTML gegenereerd als {OUTPUT_HTML}")

async def render_png():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 800, "height": 480})
        await page.goto(f"file://{OUTPUT_HTML}", wait_until="load")
        await page.screenshot(path=OUTPUT_PNG)
        await browser.close()
        print(f"✅ PNG opgeslagen als {OUTPUT_PNG}")

def commit_and_push():
    os.chdir(REPO_PATH)
    subprocess.run(['git', 'add', 'battery_status.png'])
    subprocess.run(['git', 'commit', '-m', 'auto-update battery image'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    result = subprocess.run(['git', 'push'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Geüpload naar GitHub Pages")
    else:
        print("❌ Git push mislukt:")
        print(result.stderr)

if __name__ == '__main__':
    generate_html()
    asyncio.run(render_png())

    if PUBLISH_TO_GITHUB:
        commit_and_push()
    else:
        print("🖼 Alleen lokaal gegenereerd – geen GitHub push.")

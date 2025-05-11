import requests
from PIL import Image, ImageDraw, ImageFont
import datetime
import subprocess
import os
from dotenv import load_dotenv

# ⬇️ Laad omgevingsvariabelen uit .env
load_dotenv()

MOCK = True

# Variabelen uit .env
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')
REPO_PATH = os.getenv('REPO_PATH')
PUBLISH_TO_GITHUB = os.getenv("PUBLISH_TO_GITHUB", "false").lower() == "true"
IMAGE_PATH = os.path.join(REPO_PATH, 'public', 'battery_status.png')

def get_battery_status():
    if MOCK:
        print("→ Mockdata ingeschakeld.")
        return 76.3
    # Hier zou je echte Victron API call doen

def generate_image(battery_percentage, power_usage_watt, solar_input_watt):
    width, height = 800, 480
    img = Image.new('1', (width, height), 255)
    draw = ImageDraw.Draw(img)

    # Fonts laden
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except IOError:
        font_large = font_medium = font_small = ImageFont.load_default()

    # Batterijpercentage tekst
    percentage_text = f"{battery_percentage:.1f}%"
    bbox = font_large.getbbox(percentage_text)
    text_width = bbox[2] - bbox[0]
    draw.text(
        ((width - text_width) // 2, 30),
        percentage_text,
        font=font_large,
        fill=0
    )

    # Batterijbalk
    bar_x1 = 100
    bar_x2 = width - 100
    bar_y1 = 160
    bar_y2 = 220
    draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], outline=0, width=4)
    fill_width = int((bar_x2 - bar_x1 - 4) * (battery_percentage / 100))
    draw.rectangle([bar_x1 + 2, bar_y1 + 2, bar_x1 + 2 + fill_width, bar_y2 - 2], fill=0)
    draw.rectangle([bar_x2 + 4, bar_y1 + 20, bar_x2 + 12, bar_y2 - 20], fill=0)  # topje

    # Verbruik
    usage_text = f"Verbruik: {power_usage_watt:.0f} W"
    usage_bbox = font_medium.getbbox(usage_text)
    usage_width = usage_bbox[2] - usage_bbox[0]
    draw.text(((width - usage_width) // 2, 260), usage_text, font=font_medium, fill=0)

    # Opbrengst
    solar_text = f"Zonnepanelen: {solar_input_watt:.0f} W"
    solar_bbox = font_medium.getbbox(solar_text)
    solar_width = solar_bbox[2] - solar_bbox[0]
    draw.text(((width - solar_width) // 2, 310), solar_text, font=font_medium, fill=0)

    # Tijdstempel
    timestamp = datetime.datetime.now().strftime("%H:%M")
    ts_text = f"Laatste update: {timestamp}"
    ts_bbox = font_small.getbbox(ts_text)
    ts_width = ts_bbox[2] - ts_bbox[0]
    draw.text(((width - ts_width) // 2, height - 50), ts_text, font=font_small, fill=0)

    # Opslaan
    os.makedirs(os.path.dirname(IMAGE_PATH), exist_ok=True)
    img.save(IMAGE_PATH)
    print(f"✅ Afbeelding opgeslagen als {IMAGE_PATH}")

def commit_and_push():
    os.chdir(REPO_PATH)
    subprocess.run(['git', 'add', 'public/battery_status.png'])
    subprocess.run(['git', 'commit', '-m', 'auto-update battery image'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    result = subprocess.run(['git', 'push'], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Geüpload naar GitHub Pages")
    else:
        print("❌ Git push mislukt:")
        print(result.stderr)

if __name__ == "__main__":
    battery = get_battery_status()
    power_usage = 1234  # Mock: huidig verbruik in watt
    solar_input = 543   # Mock: zonne-opbrengst in watt

    generate_image(battery, power_usage, solar_input)

    if PUBLISH_TO_GITHUB:
        commit_and_push()
    else:
        print("🖼 Alleen lokaal gegenereerd – geen GitHub push.")

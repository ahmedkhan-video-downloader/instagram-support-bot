import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from colorama import Fore, Style, init
from telethon import TelegramClient, events
from webdriver_manager.chrome import ChromeDriverManager
import config

init(autoreset=True)

client = TelegramClient('bot', config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)

SUPPORT_URLS = [
    "https://help.instagram.com/contact/606967319425038",
    "https://help.instagram.com/contact/169486816475808",
    "https://help.instagram.com/contact/1652567838289083",
    "https://help.instagram.com/contact/176481208230029",
    "https://help.instagram.com/contact/182222309230200",
    "https://help.instagram.com/contact/117150254721917",
    "https://help.instagram.com/contact/383679321740945"
]

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def get_descriptions():
    return [
        # عربي
        "حسابي تعرض للحظر عن طريق الخطأ وأرجو مراجعته بشكل يدوي.",
        "أنا أستخدم الحساب بشكل طبيعي، الرجاء إعادة تنشيطه.",
        "لم أقم بأي نشاط مخالف لشروط الخدمة، أرجو إعادة تفعيل الحساب.",
        # إنجليزي
        "My account was disabled by mistake, please review manually.",
        "I didn’t violate any terms, please restore my account.",
        "I am a content creator and need my account urgently."
    ]

def send_support_request(driver, url, username):
    try:
        driver.get(url)
        time.sleep(3)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "form")))

        # إدخال اليوزر
        try:
            field = driver.find_element(By.NAME, "username")
            field.clear()
            field.send_keys(username)
        except:
            pass

        # إدخال البريد
        try:
            email_field = driver.find_element(By.NAME, "email")
            email_field.clear()
            email_field.send_keys(f"{username}@gmail.com")
        except:
            pass

        # إدخال الوصف
        try:
            desc_field = driver.find_element(By.NAME, "description")
            desc_field.clear()
            desc = random.choice(get_descriptions())
            desc_field.send_keys(desc)
        except:
            pass

        # الضغط على إرسال
        buttons = driver.find_elements(By.XPATH, "//button[@type='submit']")
        if buttons:
            buttons[0].click()
            return True
        return False
    except:
        return False

def check_account(username):
    url = f"https://www.instagram.com/{username}/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False

@client.on(events.NewMessage(pattern='/unban'))
async def unban_handler(event):
    if event.sender_id != config.ADMIN_ID:
        await event.reply("❌ فقط الأدمن يقدر يستخدم هذا البوت.")
        return

    username = event.raw_text.split(" ")[1] if len(event.raw_text.split()) > 1 else None
    if not username:
        await event.reply("⚠️ استخدم الأمر هكذا:\n`/unban username`")
        return

    driver = setup_driver()
    total_success = 0

    for attempt in range(1,4):  # 3 محاولات لكل رابط
        await event.reply(f"⚡ إرسال الجولة {attempt}/3 لكل رابط دعم")
        for url in SUPPORT_URLS:
            result = send_support_request(driver, url, username)
            if result:
                total_success += 1
            await event.reply(f"✅ محاولة على: {url}")

    driver.quit()

    if check_account(username):
        await client.send_message(config.ADMIN_ID, f"✅ تم فك الحظر عن الحساب @{username} بنجاح!")
    else:
        await client.send_message(config.ADMIN_ID, f"⚠️ الحساب @{username} مازال محظور.")

print("🚀 البوت شغال الآن ...")
client.run_until_disconnected()

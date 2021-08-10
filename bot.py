import time
from datetime import datetime
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from discord import Webhook, RequestsWebhookAdapter, Embed

import pytz

IST = pytz.timezone('Asia/Kolkata')

week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

days = [
    {"09:00": "A Slot | ONL00234 | STS3005 | Fall sem",
     "14:00": "ONL00171-E+TE-Mobile Application Development"},

    {"09:16": "686_slotB_FallSem_CSE3008: Introduction to Machine Learning",
     "11:00": "A Slot | ONL00234 | STS3005 | Fall sem",
     "12:00": "D SLot SoftComputing Fall 21-22",
     "16:00": "CSE4027-Data Analytics (Slot-F)"},

    {"09:00": "CSE3011 C",
     "11:00": "686_slotB_FallSem_CSE3008: Introduction to Machine Learning",
     "14:00": "A Slot | ONL00234 | STS3005 | Fall sem"},

    {"09:00": "D SLot SoftComputing Fall 21-22",
     "14:00": "ONL00171-E+TE-Mobile Application Development"},

    {"09:00": "ONL00171-E+TE-Mobile Application Development",
     "11:00": "D SLot SoftComputing Fall 21-22",
     "12:00": "686_slotB_FallSem_CSE3008: Introduction to Machine Learning",
     "16:00": "CSE3011 C"},

    {"09:00": "CSE4027-Data Analytics (Slot-F)",
     "14:00": "CSE3011 C"}
]


def discord_notification(title, description=""):
    discord_webhook_url = ""
    webhook = Webhook.from_url(discord_webhook_url, adapter=RequestsWebhookAdapter())

    embed = Embed(title=f"{title}", description=f"{description}", colour=0x0011FF)
    embed.set_footer(text=f"\n{datetime.now(IST):%d/%m/%Y at %H:%M}")

    try:
        webhook.send(embed=embed)
    except:
        print("Failed to send discord notification")


def join(name):
    ## Finding Team
    try:
        element_present = EC.visibility_of_element_located((By.LINK_TEXT, name))
        WebDriverWait(browser, 600).until(element_present)

        browser.find_element_by_link_text(name).click()
    except exceptions.TimeoutException:
        print(f"Timeout waiting for element : {name}")
        discord_notification("Error!", f"{name} not found")
        exit()

    time.sleep(4)

    # Finding Join Button : Meeting
    try:
        element_present = EC.visibility_of_element_located((By.XPATH, "//*[text()='Join']"))
        WebDriverWait(browser, 600).until(element_present)

        browser.find_element_by_xpath("//*[text()='Join']").click()
    except exceptions.TimeoutException:
        print(f"No class today : {name}")
        discord_notification("Class NA", f"{name}")
        return None

    time.sleep(12)

    # Muting Audio and Video
    video_btn = browser.find_element_by_css_selector("toggle-button[data-tid='toggle-video']>div>button")
    video_is_on = video_btn.get_attribute("aria-pressed")
    if video_is_on == "true":
        video_btn.click()
        print("Video disabled")
    time.sleep(3)

    audio_btn = browser.find_element_by_css_selector("toggle-button[data-tid='toggle-mute']>div>button")
    audio_is_on = audio_btn.get_attribute("aria-pressed")
    if audio_is_on == "true":
        audio_btn.click()
        print("Microphone off")
    time.sleep(2)

    # Joining Meeting
    class1 = browser.find_element_by_xpath("//*[text()='Join now']")
    class1.click()
    print(f'Joined {name}')
    discord_notification("Joined meeting", name)

    time.sleep(2800)

    try:
        teams = browser.find_element_by_css_selector("#app-bar-2a84919f-59d8-4441-a975-2a8c2643b741")
        teams.click()
    except exceptions.NoSuchElementException:
        print("teams not found")

    time.sleep(2)

    try:
        hangup_btn = browser.find_element_by_css_selector("#hangup-button > ng-include > svg")
        hangup_btn.click()
    except exceptions.NoSuchElementException:
        print("hanup not found")

    discord_notification("Left meeting ", name)
    print("exited meeting")


def wait_until_found(sel, timeout, print_error=True):
    try:
        element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, sel))
        WebDriverWait(browser, timeout).until(element_present)

        return browser.find_element_by_css_selector(sel)
    except exceptions.TimeoutException:
        if print_error:
            print(f"Timeout waiting for element: {sel}")
            discord_notification("Timeout error", sel)
        return None


def login():
    email = ''
    password = ''
    if email != "" and password != "":
        login_email = wait_until_found("input[type='email']", 30)
        if login_email is not None:
            login_email.send_keys(email)

        # find the element again to avoid StaleElementReferenceException
        login_email = wait_until_found("input[type='email']", 5)
        if login_email is not None:
            login_email.send_keys(Keys.ENTER)

        login_pwd = wait_until_found("input[type='password']", 10)
        if login_pwd is not None:
            login_pwd.send_keys(password)

        # find the element again to avoid StaleElementReferenceException
        login_pwd = wait_until_found("input[type='password']", 5)
        if login_pwd is not None:
            login_pwd.send_keys(Keys.ENTER)

        keep_logged_in = wait_until_found("input[id='idBtn_Back']", 5)
        if keep_logged_in is not None:
            keep_logged_in.click()
            discord_notification("Logged in successfully", "")
        else:
            print("Login Unsuccessful, recheck entries in config.json")
            discord_notification("Login Unsuccessful", " recheck entries in config.json")
    time.sleep(10)


conversation_link = "https://teams.microsoft.com/_#/conversations/a"


def init_browser():
    global browser
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--use-fake-ui-for-media-stream')
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_experimental_option('prefs', {
        'credentials_enable_service': False,
        'profile.default_content_setting_values.media_stream_mic': 1,
        'profile.default_content_setting_values.media_stream_camera': 1,
        'profile.default_content_setting_values.geolocation': 1,
        'profile.default_content_setting_values.notifications': 1,
        'profile': {
            'password_manager_enabled': False
        }
    })
    chrome_options.add_argument('--no-sandbox')

    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)


def main():
    init_browser()
    browser.get("https://teams.microsoft.com")

    login()
    print("\rFound page, do not click anything on the webpage from now on.")
    time.sleep(10)

    while True:
        current = datetime.today().weekday()

        if current == 6:
            now = datetime.now(IST)
            run_at = datetime.strptime("08:56", "%H:%M").replace(year=now.year, month=now.month, day=now.day + 1)
            discord_notification("Sunday, sleeping till", run_at)
            time.sleep((run_at - now).total_seconds())
        wday = week[current]
        current = days[current]
        discord_notification(f"{wday} Time Table", '\n'.join(f"{k} : {v}" for k,v in current.items()))
        print(current)

        for t, c in current.items():
            now = datetime.now(IST)
            run_at = datetime.strptime(t, "%H:%M").replace(year=now.year, month=now.month, day=now.day).astimezone(IST)

            if (run_at - now).total_seconds() < 0:
                discord_notification("Skipped class", c)
                continue

            discord_notification(f"{c} at {t}",
                                 f"Waiting for {int((run_at - now).total_seconds()) // 60}min")
            time.sleep((run_at - now).total_seconds())

            join(c)
            time.sleep(5)

        now = datetime.now(IST)
        run_at = datetime.strptime("08:56", "%H:%M").replace(year=now.year, month=now.month,
                                                             day=now.day + 1).astimezone(IST)
        discord_notification("Done today, sleeping for",
                             f"{int((run_at - now).total_seconds() // 3600)}hr")
        time.sleep((run_at - now).total_seconds())

try:
    main()
except Exception as e:
    discord_notification("Error", f"{e}")
finally:
    if browser is not None:
        browser.quit()
    discord_notification("Browser closed", "Thank you!")

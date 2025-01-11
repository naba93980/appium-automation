import os
import subprocess
import time

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.mobileby import MobileBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

CONTACT_NUMBER = "1234567890"
DEVICE_PASSWORD = "1234"

def setup_driver():
    # Set up Appium options
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.platform_version = '13'
    options.device_name = 'motorola edge 40 neo'
    options.automation_name = 'UiAutomator2'
    options.app_package = 'com.google.android.dialer'
    options.app_activity = 'com.android.dialer.main.impl.MainActivity'
    options.no_reset = True
    
    return webdriver.Remote('http://localhost:4723', options=options)

def check_device():
    devices = os.popen("adb devices").read().strip()
    if "device" not in devices:
        raise Exception("No device connected or device not authorized")
    print("Device connected successfully")

#################################################################
def run_adb_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def unlock_device(driver, wait):
    try:
        # Wake up the device
        power_state = run_adb_command("adb shell dumpsys power | grep 'mHoldingDisplaySuspendBlocker'")
        if "false" in power_state:
            print("Waking device...")
            driver.press_keycode(26)  # Power key
            time.sleep(1)
        
        # Check lock state
        lock_state = run_adb_command("adb shell dumpsys window | grep 'mDreamingLockscreen'")
        if lock_state:
            print("Unlocking device...")
            
            # Swipe to unlock
            screen_size = driver.get_window_size()
            start_x = screen_size['width'] * 0.5
            start_y = screen_size['height'] * 0.8
            end_y = screen_size['height'] * 0.2
            driver.swipe(start_x, start_y, start_x, end_y, 500)
            
            # Enter numeric PIN
            print("Entering PIN...")
            for digit in DEVICE_PASSWORD:
                driver.press_keycode(int(digit) + 7)  # Keycode for digits 0-9 is 7-16
                # time.sleep(0.2)
            driver.press_keycode(66)  # Press Enter key to confirm
            time.sleep(2)
    except Exception as e:
        print(f"Error during unlock: {e}")
        raise
################################################################
def make_call(driver, wait):
    try:
        print("Opening dialer...")
        # Open the dialer
        try:
            phone_button = driver.find_element(MobileBy.ACCESSIBILITY_ID, "Phone")
            phone_button.click()

        except TimeoutException:
            print("Unable to locate or open the phone. Please check the app state.")
            return
        
        time.sleep(1)
        try:
            dialpad_button = driver.find_element(MobileBy.ACCESSIBILITY_ID, "key pad")
            dialpad_button.click()
        except TimeoutException:
            print("Unable to locate or open the dialpad. Please check the app state.")
            return
        
        print("Entering number...")
        # Enter the contact number using the dialpad
        digit_input = wait.until(EC.presence_of_element_located((MobileBy.ID, "com.google.android.dialer:id/digits")))
        digit_input.send_keys(CONTACT_NUMBER)
            
        time.sleep(1)
        
        print("Initiating call...")
        # Locate and click the call button
        try:
            call_button = wait.until(EC.presence_of_element_located(
                (MobileBy.ID, "com.google.android.dialer:id/dialpad_voice_call_button")))
            call_button.click()
        except TimeoutException:
            print("Unable to locate the call button. Please check the app state.")
            return
        
        time.sleep(2)
        print("Enabling speaker...")
        try:
            speaker_button = wait.until(EC.presence_of_element_located((MobileBy.XPATH, "(//android.widget.ImageView[@resource-id=\"com.google.android.dialer:id/entry_icon\"])[3]")))
            speaker_button.click()
            print("Speaker enabled.")
        except TimeoutException:
            print("Could not find the speaker button. Skipping speaker activation.")
        
        print("Call in progress...")
        time.sleep(5)
        
        print("Ending call...")
        try:
            end_call_button = wait.until(EC.presence_of_element_located(
                (MobileBy.ACCESSIBILITY_ID, "End call")))
            end_call_button.click()
        except TimeoutException:
            print("Unable to locate the end call button. Call might not have ended.")
    except Exception as e:
        print(f"Error during call: {e}")
        raise

def lock_device(driver):
    try:
        print("Locking device...")
        # CLick home button
        driver.press_keycode(3)  # Home key
        # Press the power button to lock the device
        driver.press_keycode(26)  # Power key
        time.sleep(1)
    except Exception as e:
        print(f"Error during lock: {e}")
        raise

def main():
    driver = None
    try:
        print("Starting script...")
        # Add device check/setup_driver implementation here
        driver = setup_driver()
        wait = WebDriverWait(driver, 10)
        check_device()
        unlock_device(driver, wait)
        time.sleep(10)
        make_call(driver, wait)
        lock_device(driver)
        print("Script completed successfully.")
    except Exception as e:
        print(f"Script failed: {e}")
    finally:
        if driver:
            driver.quit()
            print("Cleanup completed.")

if __name__ == "__main__":
    main()

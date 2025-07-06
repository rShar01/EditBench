import os
import time
import undetected_chromedriver as uc

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path to the chromedriver
chromedriver_path = os.path.join(script_dir, "chrome-win64", "chrome.exe")

options = uc.ChromeOptions()
# Do not set binary location to the chromedriver executable
# The next line is removed to prevent launching an extra uncontrolled browser window
# options.binary_location = chromedriver_path
# options.add_argument("--headless")  # Example: Run in headless mode

# --- Modified Section ---
with uc.Chrome(options=options, driver_executable_path=chromedriver_path) as driver:
    time.sleep(3)
    print("Starting browser...")
    driver.quit()  # Use quit() to ensure the browser is completely closed
# --- End Modified Section ---

# driver.get("https://lmarena.ai/")
# print("Loaded URL")

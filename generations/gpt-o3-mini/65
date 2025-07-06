import os
import time
import undetected_chromedriver as uc

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the relative path to the chromedriver
chromedriver_path = os.path.join(script_dir, "chromedriver-win64", "chromedriver.exe")

options = uc.ChromeOptions()
# NOTE: Removed setting options.binary_location since that is meant for specifying the Chrome binary,
# not the driver executable. Instead, we pass chromedriver_path via driver_executable_path.
print("wde")
with uc.Chrome(driver_executable_path=chromedriver_path, use_subprocess=True, options=options) as driver:
    print("wde")
    driver.get("https://lmarena.ai/")
    print("wde")
    time.sleep(10)

import time

options = uc.ChromeOptions()
# NOTE: Similarly, remove setting options.binary_location here and pass the driver path as driver_executable_path.
print("wde")
with uc.Chrome(driver_executable_path=r"C:\Programming\Test\IP_Test\chromedriver-win64\chromedriver.exe", use_subprocess=True, options=options) as driver:
    print("wde")
    driver.get("https://lmarena.ai/")
    print("wde")
    time.sleep(10)

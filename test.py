from configparser import ConfigParser
from time import sleep

from scrapia_shell import setup_browser
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

import sw_utils.jsHelpScripts as jshs


cfg = ConfigParser()
cfg.read("config.cfg")

# class="grid grid-cols-1 md:grid-cols-2 w-full"
driver = setup_browser(cfg['DRIVERS']['GECKO_EXE_PATH'], False)
driver.get("https://www.wuxiaworld.com/novel/against-the-gods")
driver.install_addon(f"{cfg['EXTENSIONS']['FOX_EXT_BASE_PATH']}/{cfg['EXTENSIONS']['UBO']}")

sleep(5)

# NOTE: find_elements_by_* commands are deprecated!!!
# NOTE: don't need to open the accordian from now on
# driver.execute_script(jshs.clickElementStartingWithStrS("span", "Volume"))
elList = driver.find_elements(By.XPATH, "//div[contains(@class, 'grid') and contains(@class, 'grid-cols-1') and contains(@class, 'md:grid-cols-2') and contains(@class, 'w-full')]")
el = elList[0]
aList = el.find_elements(By.TAG_NAME, "a")
aList[0].get_attribute("href")

def get_hrefList(divList: list[WebElement]) -> list[str]:
    hrefList = []
    for divElement in divList:
        aList: list[WebElement] = divElement.find_elements(By.TAG_NAME, "a")
        hrefList.extend([a.get_attribute("href") for a in aList])
    return hrefList
# [].sort(reverse=True)
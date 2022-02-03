from configparser import ConfigParser
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from scrapia_shell_helper import ScrapiaShellHelper
from sw_utils import JSHelpScripts


def get_hrefList(divList: list[WebElement]) -> list[str]:
    hrefList = []
    for divElement in divList:
        aList: list[WebElement] = divElement.find_elements(By.TAG_NAME, "a")
        hrefList.extend([a.get_attribute("href") for a in aList])
    return list(reversed(hrefList))


def getXpathStrFrClsNames(tagName: str, *styleClassNames: str) -> str:
    returnStr = f"//{tagName}["
    repeatingStr = lambda s: f"contains(@class, '{s}')"
    numOfClasses = len(styleClassNames)
    c = 0
    while c < numOfClasses - 1:
        returnStr += repeatingStr(styleClassNames[c]) + " and "
        c += 1
    returnStr += f"{repeatingStr(styleClassNames[c])}]"
    return returnStr


cfg = ConfigParser()
cfg.read("config.cfg")

# class="grid grid-cols-1 md:grid-cols-2 w-full"
driver = ScrapiaShellHelper("", "").setup_browser(
    cfg["DRIVERS"]["GECKO_EXE_PATH"], False
)
driver.install_addon(
    f"{cfg['EXTENSIONS']['FOX_EXT_BASE_PATH']}/{cfg['EXTENSIONS']['UBO']}"
)
driver.get("https://www.wuxiaworld.com/novel/against-the-gods")

sleep(3)

# elList = driver.find_elements(By.XPATH, "//div[contains(@class, 'grid') and contains(@class, 'grid-cols-1') and contains(@class, 'md:grid-cols-2') and contains(@class, 'w-full')]")
driver.execute_script(JSHelpScripts().clickElementWithInnerTextS("button", "chapters"))

clsTuple = ("grid", "grid-cols-1", "md:grid-cols-2", "w-full")
divList = driver.find_elements(
    By.XPATH,
    JSHelpScripts().getXpathStrFrClsNames("div", *clsTuple),
)

from configparser import ConfigParser
from time import sleep

from click import echo
from selenium.webdriver import Firefox
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver

from sw_utils import NovelProfiler, colored

initializeMsg = (
    colored("Initialized ScrapiaShellHelper", "green"),
    colored("Initialized NovelProfiler", "green"),
    colored("Initialized File_Directory_JSON_Worker", "green"),
    colored("Initialized DBHelper", "green"),
    colored("Initialized JSHelpScripts", "green"),
)

class ScrapiaShellHelper(NovelProfiler):
    """
    Base class with helper methods.

    To be inherited by `ScrapiaShell`.
    """

    def __init__(self, novelPath: str, novelName: str, accordianText: str) -> None:
        echo(initializeMsg[0])
        NovelProfiler.__init__(self, novelPath, novelName, initializeMsg, accordianText)
        cfg = ConfigParser()
        cfg.read("config.cfg")
        self.cfg = cfg

        self.GECKO_EXE_PATH: str = cfg["DRIVERS"]["GECKO_EXE_PATH"]
        self.TABLE: str = cfg["SQL"]["TABLE"]
        self.DATABASE: str = cfg["SQL"]["DATABASE"]

        self.EMAIL = self.cfg["LOGIN"]["EMAIL"]
        self.PASSWORD = self.cfg["LOGIN"]["PASSWORD"]

    def setup_browser(self, exec_path: str, isHeadless: bool = True):
        firefox_options: Options = Options()
        firefox_options.headless = isHeadless

        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "disk-cache-size": 4096,
            "intl.accept_languages": "en-US",
        }
        args = {
            "--dns-prefetch-disable",
            "--no-sandbox",
        }

        for pref in prefs:
            firefox_options.set_preference(pref, prefs[pref])
        for arg in args:
            firefox_options.add_argument(arg)

        capabilities = DesiredCapabilities.FIREFOX

        # firefox_options.set_headless(True)
        return Firefox(
            executable_path=exec_path,
            desired_capabilities=capabilities,
            options=firefox_options,
        )

    def installAddon_cleanTabs_getLoginWindow(self, driver: WebDriver) -> None:
        """
        1) Install UblockOrigin
        2) If any "welcome" windows open, close them
        3) Click on login button
        """

        driver.install_addon(
            f"{self.cfg['EXTENSIONS']['FOX_EXT_BASE_PATH']}/{self.cfg['EXTENSIONS']['UBO']}"
        )

        driver.get(self.cfg["LOGIN"]["LOGIN_FROM"])
        WebDriverWait(self.driver, 7).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "main"))
        )
        # wait for the page to load

        # Points to ww login-page
        MAIN_HANDLE: str = driver.current_window_handle
        for window_handle in driver.window_handles:
            if window_handle != MAIN_HANDLE:
                driver.switch_to.window(window_handle)
                # after closing all irrelevant tabs driver will focus back to the main one
                driver.close()
        # Puts focus back on ww login-page
        driver.switch_to.window(MAIN_HANDLE)
        # Use this stuff to setup the login window (You don't want any junk in some new tab)
        sleep(2)
        # click the first button on the page, it will make login button visible
        driver.execute_script(
            self.clickFirstElementFromElementList("button")
            + self.clickElementWithInnerTextS("button", "log in")
        )

    def loginToWebsite(self, driver: WebDriver) -> None:
        """
        1) Login using credentials in `config.cfg`
        2) sleep for 3 seconds
        """
        inputElement = driver.find_element_by_id("Username")
        inputElement.send_keys(self.EMAIL)
        inputElement = driver.find_element_by_id("Password")
        inputElement.send_keys(self.PASSWORD)
        inputElement.send_keys(Keys.ENTER)
        sleep(3)

    def chapterNumberFromURL(
        self, url: str, return_as_is: bool = False, *args
    ) -> int | None:
        """Setting `return_as_is` to True will return the number as a string,
        this is used by the `end_cleanly` function."""

        # This returns only the relevant part (the part with the chapter no)
        url = list(
            reversed(
                url.removeprefix("https://www.wuxiaworld.com/novel/")
                .rstrip("/")
                .replace("-", " ")
                .split(" ")
            )
        )
        number_as_str: str = ""
        for element in url:
            if element.isdecimal():
                number_as_str = element
                break
        if not (number_as_str) or not (number_as_str.isdigit()):
            return
        if not return_as_is:
            return int(number_as_str)
        else:
            return number_as_str

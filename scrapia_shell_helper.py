from configparser import ConfigParser

from selenium.webdriver import Firefox
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.firefox.options import Options

from sw_utils import NovelProfiler


class ScrapiaShellHelper(NovelProfiler):
    """
    Base class with helper methods.

    To be inherited by `ScrapiaShell`.
    """

    def __init__(self) -> None:
        NovelProfiler.__init__(self)

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

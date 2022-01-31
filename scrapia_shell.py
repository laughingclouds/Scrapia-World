"""
3) For missing novels, add the functionality for pausing the code while it's running and scrape those missing novels first.
4) Sometimes `panels` in the `novel page` have different names for different novels, for them, create a json file for
    storing what kind of a panel they have. For that save it as "str type" and "int type" or simply hardcode that stuff...
5) Try to get the chapter no. from the current page, if it works, that should be the new value
    of `BH_NO`. Why? We want to be consistent with exactly exceeding chapters being scraped and this will help in that.
7) Add an option to update webdrivers automatically, make a CLI option
    check out this tool https://pypi.org/project/webdriver-manager/
"""
# scrapia_world = Scrape wuxia world...
from pprint import pprint
import threading
from cmd import Cmd
from sys import exit, exc_info
from traceback import print_exc
from json import load
from time import sleep  # for timeouts, cuz' you don't wanna get your IP banned...
from platform import system as returnOSName
from configparser import ConfigParser

from click import clear, echo
from selenium.common import exceptions
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement  # for type hinting
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import sw_utils.jsHelpScripts as jshs
from sw_utils import clrScrn, get_hrefList
from sw_utils.termcolor import colored
from sw_utils.novelProfiler.db import getChapterNumberFrmDB, getConAndCur


def setup_browser(exec_path: str, isHeadless: bool = True):
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


# So that termcolor can work on windows
if returnOSName() == "Windows":
    from sw_utils import colorama

    colorama.init()


class ScrapiaShell(Cmd):
    """
    Shell for scraping

    TODO create a helper class that has methods of current class 
    that won't be shown in the interactive shell
    TODO Create a NovelProfiler class or something as well
    """

    # ctx will be used in the class that overrides this one

    def __init__(self, isHeadless: int, novel_name: str, ctx):
        Cmd.__init__(self)

        cfg = ConfigParser()
        cfg.read("config.cfg")
        self.cfg = cfg
        self.ctx = ctx
        # self.FIRST_KEY: str = ''
        self.SCRAPER_THREAD = threading.Thread(target=self.startScraping)
        # using sys.exit will now kill this thread.
        self.SCRAPER_THREAD.daemon = True
        self.__NOVEL = novel_name
        # To make sure certain functions run only after `setup` is invoked
        self.is_ready: bool = False
        self._save_src: bool = True  # If set, we'll save as html instead.

        # Reading from the json file
        with open("novel_page_info.json", "r") as novel_page_fobj:
            # Refer to the above json files to understand this mess

            novel_page_dict: dict = load(novel_page_fobj)            
            self.NOVEL_PAGE_INFO: dict[str, str] = novel_page_dict["novel_page_info"][
                novel_name
            ]
        self.__EXECUTABLE_PATH_GECKO: str = cfg["DRIVERS"]["GECKO_EXE_PATH"]
        self.__TABLE: str = cfg["SQL"]["TABLE"]
        self.__DATABASE: str = cfg["SQL"]["DATABASE"]

        #  These will be used later on
        self.CH_NO: int = 0
        self.__LATEST_CH_NO = int(self.NOVEL_PAGE_INFO["LATEST_CH_NO"])
        self.__NOVEL_PATH = self.NOVEL_PAGE_INFO["NOVEL_PATH"]
        self.EMAIL = self.cfg["LOGIN"]["EMAIL"]
        self.PASSWORD = self.cfg["LOGIN"]["PASSWORD"]

        self.__mydb, self.__cursor = getConAndCur(self.__DATABASE)
        self.CH_NO = getChapterNumberFrmDB(
            self.__mydb, self.__cursor, self.__TABLE, self.__NOVEL
        )

        self.driver = setup_browser(self.__EXECUTABLE_PATH_GECKO, isHeadless)

        self.prompt = colored(f"({self.__NOVEL}) ", "red")

    intro = colored("Hi! Enter `help` for...well...help...", "green")

    def do_nextPage(self) -> None:
        """Finds and clicks the `Next` button"""
        self.driver.execute_script(jshs.clickElementStartingWithStrS("span", "Next"))

    def increment_ch_no(self, commitOnly: bool = False) -> None:
        """
        - Default behaviour: Increment `CH_NO` by 1
        - On setting `commit` to `True`: Don't increment, commit to database
        
        NOTE set `commit` to `True` only when program is about to/ made to end
        """

        if commitOnly:
            with self.__mydb:
                self.__cursor.execute(
                    f"UPDATE {self.__TABLE} SET {self.__NOVEL}={self.CH_NO};"
                )
            return
        self.CH_NO += 1

    def installAddon_cleanTabs_getLoginWindow(self) -> None:
        """
        1) Install UblockOrigin
        2) If any "welcome" windows open, close them
        3) Click on login button
        """

        self.driver.install_addon(
            f"{self.cfg['EXTENSIONS']['FOX_EXT_BASE_PATH']}/{self.cfg['EXTENSIONS']['UBO']}"
        )

        self.driver.get(self.cfg["LOGIN"]["LOGIN_FROM"])
        WebDriverWait(self.driver, 7).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "main"))
        )
        # wait for the page to load

        # Points to ww login-page
        MAIN_HANDLE: str = self.driver.current_window_handle
        for window_handle in self.driver.window_handles:
            if window_handle != MAIN_HANDLE:
                self.driver.switch_to.window(window_handle)
                # after closing all irrelevant tabs driver will focus back to the main one
                self.driver.close()
        # Puts focus back on ww login-page
        self.driver.switch_to.window(MAIN_HANDLE)
        # Use this stuff to setup the login window (You don't want any junk in some new tab)
        sleep(2)
        # click the first button on the page, it will make login button visible
        js = jshs.clickFirstElementFromElementList(
            "button"
        ) + jshs.clickElementWithInnerTextS("button", "log in")
        self.driver.execute_script(js)

    def scrape_sleep_gotoNextPage(self) -> None:
        self.do_scrape()
        sleep(100)
        self.do_nextPage()

    # For god's sake, don't push the json to github...
    # For god's sake, don't push the json to github...
    def loginThenGetNovelPage(self) -> None:
        """
        1) Login using credentials in `config.cfg`
        2) get novel page
        """
        inputElement = self.driver.find_element_by_id("Username")
        inputElement.send_keys(self.EMAIL)
        inputElement = self.driver.find_element_by_id("Password")
        inputElement.send_keys(self.PASSWORD)
        inputElement.send_keys(Keys.ENTER)
        sleep(3)
        # goto novel-page of whatever novel has been choosen
        self.driver.get(self.NOVEL_PAGE_INFO["NOVEL_PAGE"])

    def startScraping(self) -> None:
        """
        - `target` of `self.SCRAPER_THREAD` object.
        - invoked by `self.do_start_scraping` in a thread.
        """
        try:
            if not self.is_ready:
                self.do_setup()

            if self.chapterNumberFromURL(self.__INITIAL_SCRAPE) == self.CH_NO:
                print(f"FOUND----------CHAPTER----------{self.CH_NO}")
                self.driver.get(self.__INITIAL_SCRAPE)
                sleep(5)
                self.scrape_sleep_gotoNextPage()

            while self.CH_NO <= self.__LATEST_CH_NO:
                print("WHILE----------LOOP----------Initialized")
                self.scrape_sleep_gotoNextPage()
                if self.CH_NO % 5 == 0:
                    self.increment_ch_no(commitOnly=True)
                # optional, you could add a line to stop execution
                # when a certain `CH_NO` has been scraped.
            print("All present chapters scraped...\nEnding...")
            self.do_end_cleanly()

        except KeyboardInterrupt:
            self.do_end_cleanly()
            print("KEYBOARD----------INTERRUPT----------INVOKED")
            return
        except Exception:
            print("----------ERROR----------")
            print_exc()
            self.do_end_cleanly()
            return

    def do_ch_no(self, *args) -> None:
        """Perform operations on `self.CH_NO`."""
        option = str(input("(show/change)? ")).strip()
        if option == "show":
            print(self.CH_NO)
        elif option == "change":
            try:
                self.CH_NO = int(input("New value: ").strip())
            except Exception as e:
                print(e, "Retry with a the correct value next time.", sep="\n")
                return None
        else:
            print("Aborting!")

    def do_change_values(self, *args):
        """
        menu to change values of certain variables        
        """
        # For now work with `self._save_src` only
        new_value = input("change to true?\n(y/n) ")
        if new_value == "y":
            self._save_src = True
        elif new_value := input("change to false?\n(y/n) ") == "y":
            self._save_src = False
        else:
            print("Aborted!")

    def do_cls(self, *args) -> None:
        """Clear screen"""
        clrScrn(clear)

    def do_commit(self, *args) -> None:
        """
        - Commit current value of `self.CH_NO` to database.

        NOTE you can change the value using `ch_no`"""
        self.increment_ch_no(commitOnly=True)

    def do_current_url(self, *args) -> None:
        try:
            echo(f"We are in\n{self.driver.current_url}")
        except Exception as e:
            echo(e + "\n\n" + "Try invoking `setup` first")
            return None

    def chapterNumberFromURL(
        self, url: str, return_as_is: bool = False, *args
    ) -> int | None:
        """Setting `return_as_is` to True will return the number as a string, 
        this is used by the `end_cleanly` function."""
        if not self.is_ready:
            echo("Can run only after `setup` is invoked!")
            return

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
        if not number_as_str:
            return
        if return_as_is:
            return number_as_str
        else:
            return int(number_as_str)

    def do_get(self, *args):
        """Prompts for a url and invokes `self.__driver.get(<url>)`"""
        url: str = input("Enter url: ").strip()
        self.driver.get(url)

    def do_end_cleanly(self, onlyDriverQuit: bool = False, *args):
        """Invoke two functions:

        1) `increment_ch_no(commit=True)`
        2) `driver.quit()`
        
        Simply quits the driver if `onlyDriverQuit` is set to `True`.

        NOTE 
        - `end_cleanly` does 'NOT' end the program execution
        - just closes the browser and commits to db
        """

        if onlyDriverQuit:
            self.driver.quit()
            return
        # TODO Change code later
        # don't take current_ch_no, take current index number
        # which will be found using the profiler
        current_ch_no: str = self.chapterNumberFromURL(
            self.driver.current_url, return_as_is=True
        )
        if (
            current_ch_no
        ):  # we want to save the ch_no of the chapter we are presently in
            self.CH_NO = int(current_ch_no)

        self.increment_ch_no(commitOnly=True)
        self.driver.quit()

    def do_exit(self, *args) -> bool:
        """Exit the interactive shell"""
        try:
            if self.is_ready:
                self.CH_NO = int(
                    self.chapterNumberFromURL(
                        self.driver.current_url, return_as_is=True
                    )
                )
        except ValueError:
            pass
        finally:
            self.do_end_cleanly(onlyDriverQuit=not (self.is_ready))
            exit()  # This kills the daemon

    def do_is_ready(self, show: bool = False, *args) -> None:
        """This is for manually telling the shell that we have now completed `setup`."""
        if show:
            print("This is the value of `self.is_ready`:", self.is_ready)
        elif self.is_ready:
            echo("It is already set to True!")
        else:
            self.is_ready = True
            echo("Value has been set to True!")

    # TODO Rename this son
    # This will go into profiler class
    def do_openAccordians(self, *args) -> None:
        """The name makes it quite obvious...I'll come up with a better description at some later date."""

        if not self.is_ready:
            echo("Can run only after `setup` is invoked!")
            return None
        # The structure is quite simple, Dictionary{ tuple(lowerLimit, upperLimit): VolumeNumber }
        # starts from '2' because in the initial setup the first panel is open by default, clicking on it, will close
        # and hence, hide the chapters withing that panel.

        self.driver.execute_script(
            jshs.clickElementWithInnerTextS("button", "chapters")
        )

        clsTuple = ("grid", "grid-cols-1", "md:grid-cols-2", "w-full")
        divList = self.driver.find_elements(
            By.XPATH,
            jshs.getXpathStrFrClsNames("div", *clsTuple),
        )

        hrefList = get_hrefList(divList)
        # TODO ADD CODE HERE!!        

    def do_pr_pgsrc(self, *args):
        """Prints the page source to stdout"""
        print(self.driver.page_source)

    def do_reinitiate(self, *args) -> None:
        """Re-initiates the driver object for smoothly re-running from the terminal itself"""
        option = input(
            "THIS WILL CLOSE ANY RUNNING INSTANCES OF SELENIUM IN THIS THREAD\nCONTINUE? (y/n): "
        )
        if option == "y":
            self.do_end_cleanly()
            self.driver = Firefox(executable_path=self.__EXECUTABLE_PATH_GECKO)
        else:
            return None

    def do_reinitiate_everything(self, *args) -> None:
        """This will re-initiate everything, including the shell class."""
        option = input(
            "THIS WILL CLOSE ANY RUNNING INSTANCES OF SELENIUM IN THIS THREAD\nCONTINUE? (y/n): "
        )
        if option == "y":
            novel_name: str = input(f"{self.prompt}Enter novel name: ").strip()
            self.do_end_cleanly()
            self.__init__(novel_name)
        else:
            return None

    def do_scrape(self, *args) -> None:
        """`scrape` does the following:\n
        Get relevant content from the website and then save it in a file `NOVEL_SAVE_PATH`.\n
        Increment the value of global variable `CH_NO` by one and output the title of the webpage scraped."""

        if not self.is_ready:
            echo("Can run only after `setup` is invoked!")
            return None
        # the filename including the chapters from now on should be saved as `<last_part_of_url>.txt`

        URL_LAST_PART: str = self.driver.current_url.rstrip("/").split("/")[-1]

        file_ext: str = ".txt"  # default value
        if self._save_src:
            file_ext = ".html"
            story_content = self.driver.page_source
        else:
            # we don't need this if we're saving pg source by default
            # but this won't work either
            story_content = self.driver.find_element_by_id("chapter-content").text
        with open(self.__NOVEL_PATH + URL_LAST_PART + file_ext, "w") as f:
            f.write(story_content)
        self.increment_ch_no()

        print(f"{URL_LAST_PART} scraped successfully...\n")

    # Setting up everything
    def do_setup(self, *args) -> None:
        """This has something to do with the way the site is designed, go to any random chapter and inspect the page source
        in the source a `div` has the `back button, the link to the novel page, the next button` (in this order)
        what this code does is simply returns a list of the WebElement objects that refer to these elements respectively.
        and since I know that I'm supposed to go to the next chapter, I simply choose the last element and click it."""
        # TODO Change!!!
        # You no longer need to open accordians and search for chapter names and shit
        # Now simply fetch the latest link using novel profiler
        # driver.get that link and start_scraping from there
        try:
            self.is_ready = True
            self.installAddon_cleanTabs_getLoginWindow()
            sleep(5)

            self.loginThenGetNovelPage()
            sleep(2)

            # TODO put code to directly goto chapter, using indexed link

            self.driver.implicitly_wait(5)
            # This is all it does.
            # It's basically creating (or `setting up`) a scenario that makes scraping through the click method possible
        except exceptions.NoSuchElementException as e:
            print("EXCEPTION-----from self.do_setup")
            print(e, "Try to invoke `start_scraping`", sep="\n\n")
        except Exception as e:
            self.is_ready = False
            print(e, "FROM self.do_setup", sep="\n\n")
        finally:
            print(
                "The start_scraping function should be working no matter what.",
                "If you're having trouble with this function, consider manually going to the required chapter.",
                "And invoking `start_scraping`, it should start scraping then.\n\n",
            )
            return

    # –
    # -

    def do_start_scraping(self, *args):
        """This will run the `self.__start_scraping` helper function in a thread. This particular function also
        deals with any function calls that might try to `start` the same thread again."""
        try:
            self.SCRAPER_THREAD.start()
        except RuntimeError as e:
            print(e, "The function is probably already running!", sep="\n")
            return None

"""
3) For missing novels, add the functionality for pausing the code while it's running and scrape those missing novels first.
4) Sometimes `panels` in the `novel page` have different names for different novels, for them, create a json file for
    storing what kind of a panel they have. For that save it as "str type" and "int type" or simply hardcode that stuff...
5) Try to get the chapter no. from the current page, if it works, that should be the new value
    of `BH_NO`. Why? We want to be consistent with exactly exceeding chapters being scraped and this will help in that.
"""
# scrapia_world = Scrape wuxia world...
import cmd
import threading
from json import load
from os import environ
from sys import exit
from time import \
    sleep  # for timeouts, cuz' you don't wanna get your IP banned...

import click
import colorama
import mysql.connector
from mysql.connector.cursor import MySQLCursor
from selenium.common import exceptions
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement  # for type hinting
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from termcolor import colored

colorama.init()


class ScrapiaShell(cmd.Cmd):
    """Shell for scraping...duh..."""
    # ctx will be used in the class that overrides this one
    def __init__(self, novel_name: str, ctx):
        cmd.Cmd.__init__(self)
        # self.FIRST_KEY: str = ''
        self.SCRAPER_THREAD = threading.Thread(target=self.__start_scraping)
        self.SCRAPER_THREAD.daemon = True  # using sys.exit will now kill this thread.
        self.ctx = ctx
        self.__NOVEL = novel_name
        self.is_ready: bool = False     # To make sure certain functions run only after `setup` is invoked

        with open("novel_page_info.json", 'r') as novel_page_fobj, open("panel_struct_info.json", 'r') as panel_struct_fobj:       # Reading from the json file
            # Refer to the above json files to understand this mess

            novel_page_dict: dict = load(novel_page_fobj)

            self.__PANEL_STRUCT_DICT: dict = load(panel_struct_fobj)[novel_name]
            self.__EXECUTABLE_PATH_GECKO: str = novel_page_dict['drivers_and_extensions']['EXECUTABLE_PATH_GECKO']
            self.__LOGIN_INFO: dict[str, str] = novel_page_dict['login_info']
            self.__NOVEL_PAGE_INFO: dict[str, str] = novel_page_dict['novel_page_info'][novel_name]
            self.__TABLE: str = novel_page_dict['sql_info']['TABLE']
            self.__DATABASE: str = novel_page_dict['sql_info']['DATABASE']

        #  These will be used later on
        self.CH_NO: int = 0
        self.__CHAPTER_NO_SUF = self.__NOVEL_PAGE_INFO['CHAPTER_NO_SUF']
        self.__CHAPTER_NO_PRE = self.__NOVEL_PAGE_INFO['CHAPTER_NO_PRE']
        self.__EMAIL = self.__LOGIN_INFO['EMAIL']
        self.__INITIAL_SCRAPE = self.__NOVEL_PAGE_INFO['INITIAL_SCRAPE']
        self.__LATEST_CH_NO = int(self.__NOVEL_PAGE_INFO['LATEST_CH_NO'])
        self.__NOVEL_SAVE_PATH_BASE = self.__NOVEL_PAGE_INFO['NOVEL_SAVE_PATH_BASE']
        self.__PASSWORD = self.__LOGIN_INFO['PASSWORD']

        self.__mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            database=self.__DATABASE,
            password=environ['PASSWORD']
        )
        self.__cursor: MySQLCursor = self.__mydb.cursor(dictionary=True)
        self.__cursor.execute(f"SELECT {self.__NOVEL} FROM {self.__TABLE};")
        for row in self.__cursor:
            self.CH_NO = row[self.__NOVEL]

        self.__driver = Firefox(executable_path=self.__EXECUTABLE_PATH_GECKO)

        self.prompt = colored(f"({self.__NOVEL}) ", 'red')
    intro = colored("Hi! Enter `help` for...well...help...", 'green')

    def __goto_next_page(self) -> None:
        """Does one simple task, and that is, it clicks on the button, that will take us to
        the next page or to the next chapter."""

        element: WebElement = self.__driver.find_element_by_class_name("top-bar-area")
        elements = element.find_elements_by_xpath(".//a")       # Returns a list of elements

        elements[2].click()     # This clicks the `next button`

    def __increment_ch_no(self, commit: bool = False) -> None:
        """This function `by default`, will only increment `CH_NO` by 1.\n
        But, setting `commit` to `True` will make it 'NOT INCREMENT' `CH_NO` and rather
        just commit to database.
        
        `commit` is to be set to `True` only when the script is about to close selenium."""

        if commit:
            self.__cursor.execute(f"UPDATE {self.__TABLE} SET {self.__NOVEL} = {self.CH_NO};")
            self.__mydb.commit()
            return None
        self.CH_NO += 1

    def __install_addon_clean_tabs_get_login_window(self) -> None:
        """Big name...ikr, this will first install an addon (`ghostery ad blocker`), then also go to the login window
        of wuxiaworld. After sleeping for 7 seconds the code will then begin to close any unwanted tabs (closes any tabs that are not `MAIN_HANDLE`)
        and also return focus to the login window.

        Extra import requirements:\n
        `from selenium.webdriver.common.by import By`\n
        `from selenium.webdriver.support.ui import WebDriverWait`\n
        `from selenium.webdriver.support import expected_conditions as EC`
        """
        
        # driver.install_addon('/opt/WebDriver/fox_ext/touch_vpn_secure_vpn_proxy_for_unlimited_access-4.2.1-fx.xpi')
        # Don't need the vpn if we're gonna go with the click implementation
        self.__driver.install_addon('/opt/WebDriver/fox_ext/ghostery_privacy_ad_blocker-8.5.5-an+fx.xpi')
        self.__driver.install_addon('/opt/WebDriver/fox_ext/privacy_badger-2021.2.2-an+fx.xpi')
        self.__driver.get("https://www.wuxiaworld.com/account/login")
        WebDriverWait(self.__driver, 7).until(EC.presence_of_all_elements_located((By.TAG_NAME, "form")))
        # wait for the page to load

        MAIN_HANDLE: str = self.__driver.current_window_handle     # Points to ww /account/login
        for window_handle in self.__driver.window_handles:
            if window_handle != MAIN_HANDLE:
                self.__driver.switch_to.window(window_handle)
                self.__driver.close()      # after closing all irrelevant tabs driver will focus back to the main one
        self.__driver.switch_to.window(MAIN_HANDLE)    # Puts focus back on ww /account/login
            # Use this stuff to setup the login window (You don't want any junk in some new tab)

    def __invoke_scrape_sleep_goto_next_page(self) -> None:
        """This function invokes all these three functions"""
        self.do_scrape()
        sleep(115)       # DO NOT DELETE!!! Unless...you want to be seen as a bot and blocked?
        self.__goto_next_page()

    # For god's sake, don't push the json to github...
    # For god's sake, don't push the json to github...
    def __login_key_strokes_goto_chapterpage(self) -> None:
        """This will login through your credentials. And then send you to the chapter page.
        
        Extra import requirements:\n
        `from selenium.webdriver.common.keys import Keys`"""

        inputElement = self.__driver.find_element_by_id('Email')
        inputElement.send_keys(self.__EMAIL)
        inputElement = self.__driver.find_element_by_id('Password')
        inputElement.send_keys(self.__PASSWORD)
        inputElement.send_keys(Keys.ENTER)
        sleep(3)
        self.__driver.get(self.__NOVEL_PAGE_INFO['NOVEL_PAGE']) # goto whatever novel whas entered

    def __start_scraping(self) -> None:
        """Helper function that will be invoked by `self.do_start_scraping` in a thread.
        This is the target function of `self.SCRAPER_THREAD` object."""
        try:
            if not self.is_ready:
                self.do_setup()

            if self.do_get_chapter_number_from_url(self.__INITIAL_SCRAPE) == self.CH_NO:
                print(f"FOUND----------CHAPTER----------{self.CH_NO}")
                self.__driver.get(self.__INITIAL_SCRAPE)
                sleep(5)
                self.__invoke_scrape_sleep_goto_next_page()

            while self.CH_NO <= self.__LATEST_CH_NO:
                print("WHILE----------LOOP----------Initialized")
                self.__invoke_scrape_sleep_goto_next_page()
                if self.CH_NO % 5 == 0:
                    self.__increment_ch_no(commit=True)
                # optional, you could add a line to stop execution when a certain `CH_NO` has been scraped.
            print("All present chapters scraped...\nEnding...")
            self.do_end_cleanly()
            
        except KeyboardInterrupt:
            self.do_end_cleanly()
            print("KEYBOARD----------INTERRUPT----------INVOKED")
            return None
        except Exception as e:
            print("----------ERROR----------")
            print(e)
            self.do_end_cleanly()
            return None

    def do_ch_no(self, *args) -> None:
        """Perform operations on `self.CH_NO`"""
        option = str(input("(show/change)? ")).strip()
        if option == "show":
            print(self.CH_NO)
        elif option == "change":
            try:
                self.CH_NO = int(input("New value: ").strip())
            except Exception as e:
                print(e, "Retry with a the correct value next time.", sep='\n')
                return None
        else:
            print("Aborting!")

    def do_cls(self, *args) -> None:
        """Clear screen using `click`"""
        click.clear()

    def do_commit(self, *args) -> None:
        """Commits the current value of `self.CH_NO` to db. You can change the value before calling this
        using `ch_no` function"""
        self.__increment_ch_no(commit=True)

    def do_curent_url(self, *args) -> None:
        try:
            click.echo(f"We are in\n{self.__driver.current_url}")
        except Exception as e:
            click.echo(e + '\n\n' + "Try invoking `setup` first")
            return None

    def do_get_chapter_number_from_url(self, url: str, return_as_is: bool=False, *args) -> int:
        """"Setting `return_as_is` to True will return the number as a string, this is used by the `end_cleanly` function."""
        if not self.is_ready:
            click.echo("Can run only after `setup` is invoked!")
            return None

        url = url.rstrip('/').split('/')[-1]        # This returns only the relevant part (the part with the chapter no)
        number_as_str: str = ''
        was_prev_element_digit: bool = False
        for element in url:
            if element.isdigit():
                number_as_str += element
                was_prev_element_digit = True
            elif not(element.isdigit()) and was_prev_element_digit:
                break
            else:
                continue
        if return_as_is:
            return number_as_str
        else:
            return int(number_as_str)

    def do_end_cleanly(self, *args) -> None:
        """Invokes two functions:

        `increment_ch_no(commit=True)` and
        `driver.quit()`
        \n
        Note that `end_cleanly` does 'NOT' end the program execution, it just ends the browser and commits
        to db."""
        
        current_ch_no: str = self.do_get_chapter_number_from_url(self.__driver.current_url, return_as_is=True)
        if current_ch_no:  # we want to save the ch_no of the chapter we are presently in
            self.CH_NO = int(current_ch_no)
            
        self.__increment_ch_no(commit=True)
        self.__driver.quit()

    def do_exit(self, *args) -> bool:
        """Exits the interactive shell"""
        try:
            self.CH_NO = int(self.do_get_chapter_number_from_url(self.__driver.current_url, return_as_is=True))
        except ValueError:
            pass
        finally:
            self.do_end_cleanly()
            exit()      # This kills the daemon

    def do_is_ready(self, show: bool=False, *args) -> None:
        """This is for manually telling the shell that we have now completed `setup`."""
        if show:
            print("This is the value of `self.is_ready`:", self.is_ready)
        elif self.is_ready:
            click.echo("It is already set to True!")
        else:
            self.is_ready = True
            click.echo("Value has been set to True!")

    def do_open_chapterhead_then_panel(self, *args) -> None:
        """The name makes it quite obvious...I'll come up with a better description at some later date."""

        if not self.is_ready:
            click.echo("Can run only after `setup` is invoked!")
            return None
        # The structure is quite simple, Dictionary{ tuple(lowerLimit, upperLimit): VolumeNumber }
        # starts from '2' because in the initial setup the first panel is open by default, clicking on it, will close
        # and hence, hide the chapters withing that panel.

        self.__driver.find_element_by_partial_link_text("Chapters").click()
        # This will open only the required panel in the chapters section of ww /atg
        try:
            is_first_iteration: int = 0  # cuz' the first panel is open by default
            for chapter_tuple in self.__PANEL_STRUCT_DICT:
                chapter_tuple: list[int, int] = eval(chapter_tuple)  # Yes, this is actually a list
                if chapter_tuple[0] <= self.CH_NO <= chapter_tuple[1]:
                    if is_first_iteration == 0:
                        is_first_iteration += 1
                    else:
                        self.__driver.find_element_by_partial_link_text(self.__PANEL_STRUCT_DICT[str(chapter_tuple)]).click()
                        return None
                        # Since chapter_tuple is also a key we use it to access the value in panel_struct_dict
        except exceptions.NoSuchElementException as e:
            print(e, "From function: self.do_open_chapterhead_then_panel", sep='\n\n')
        except Exception as e:
            print(e, "From function: self.do_open_chapterhead_then_panel", sep='\n\n')

    def do_reinitiate(self, *args) -> None:
        """Re-initiates the driver object for smoothly re-running from the terminal itself"""
        option = input("THIS WILL CLOSE ANY RUNNING INSTANCES OF SELENIUM IN THIS THREAD\nCONTINUE? (y/n): ")
        if option == 'y':
            self.do_end_cleanly()
            self.__driver = Firefox(executable_path=self.__EXECUTABLE_PATH_GECKO)
        else:
            return None

    def do_reinitiate_everything(self, *args) -> None:
        """This will re-initiate everything, including the shell class."""
        option = input("THIS WILL CLOSE ANY RUNNING INSTANCES OF SELENIUM IN THIS THREAD\nCONTINUE? (y/n): ")
        if option == 'y':
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
            click.echo("Can run only after `setup` is invoked!")
            return None
        # the filename including the chapters from now on should be saved as `<last_part_of_url>.txt`

        URL_LAST_PART: str = self.__driver.current_url.rstrip('/').split('/')[-1]
        # Since the code is self-explanatory, I'll describe what the variable stands for
        # The last part of the url usually contains information on the chapter being scraped
        # We will, from now on save the chapter text file with this part of the url as it's name
        story_content = self.__driver.find_element_by_id('chapter-content').text

        with open(self.__NOVEL_SAVE_PATH_BASE + URL_LAST_PART, 'w') as f:
            f.write(story_content)
        self.__increment_ch_no()

        print(f"{URL_LAST_PART} scraped successfully...\n")

    # Setting up everything
    def do_setup(self, *args) -> None:
        """This has something to do with the way the site is designed, go to any random chapter and inspect the page source
        in the source a `div` has the `back button, the link to the novel page, the next button` (in this order)
        what this code does is simply returns a list of the WebElement objects that refer to these elements respectively.
        and since I know that I'm supposed to go to the next chapter, I simply choose the last element and click it."""
        try:
            self.is_ready = True            
            self.__install_addon_clean_tabs_get_login_window()

            sleep(5)
            self.__login_key_strokes_goto_chapterpage()

            self.do_open_chapterhead_then_panel()
            sleep(3)    # just wait...it's extra safe

            element_to_click: str = self.__CHAPTER_NO_PRE + str(self.CH_NO) + self.__CHAPTER_NO_SUF
            self.__driver.find_element_by_partial_link_text(element_to_click).click()  # For going to the required chapter

            self.__driver.implicitly_wait(5)
            # This is all it does.
            # It's basically creating (or `setting up`) a scenario that makes scraping through the click method possible
        except exceptions.NoSuchElementException as e:
            print("EXCEPTION-----from self.do_setup")
            print(e, "Try to invoke `start_scraping`", sep='\n\n')
        except Exception as e:
            print(e, "FROM self.do_setup", sep='\n\n')
            self.is_ready = False
        finally:
            print("The start_scraping function should be working no matter what.",
            "If you're having trouble with this function, consider manually going to the required chapte.",
            "And invoking `start_scraping`, it should start scraping then.\n\n")
            return None
    # –
    # -
    def do_start_scraping(self, *args):
        """This will run the `self.__start_scraping` helper function in a thread. This particular function also
        deals with any function calls that might try to `start` the same thread again."""
        try:            
            self.SCRAPER_THREAD.start()
        except RuntimeError as e:
            print(e, "The function is probably already running!", sep='\n')
            return None

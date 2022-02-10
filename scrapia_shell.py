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
import threading
from cmd import Cmd
from sys import exit
from traceback import print_exc
from json import dump, load
from time import sleep  # for timeouts, cuz' you don't wanna get your IP banned...
from platform import system as returnOSName

from click import clear, echo, Context
from selenium.common import exceptions

from sw_utils import clrScrn, colored
from scrapia_shell_helper import ScrapiaShellHelper


if returnOSName() == "Windows":
    from sw_utils import colorama

    colorama.init()


class ScrapiaShell(Cmd, ScrapiaShellHelper):
    """
    Shell for scraping

    TODO create a helper class that has methods of current class
    that won't be shown in the interactive shell
    TODO Create a NovelProfiler class or something as well
    """

    # ctx will be used in the class that overrides this one

    def __init__(self, isHeadless: int, novelName: str, ctx: Context):
        msg = colored("Initialized ScrapiaShell", "green")
        echo(msg)
        Cmd.__init__(self)
        self.ctx = ctx
        self.isHeadless = isHeadless

        self.SCRAPER_THREAD = threading.Thread(target=self.startScraping)
        # using sys.exit will now kill this thread.
        self.SCRAPER_THREAD.daemon = True
        self.NOVEL = novelName
        # To make sure certain functions run only after `setup` is invoked
        self.is_ready: bool = False
        self.saveSrc: bool = True  # If set, we'll save as html instead.

        # Reading from the json file
        with open("novel_page_info.json", "r") as novel_page_fobj:
            # Refer to the above json files to understand this mess

            novel_page_dict: dict = load(novel_page_fobj)
            self.NOVEL_PAGE_INFO: dict[str, str] = novel_page_dict["novel_page_info"][
                novelName
            ]

        #  These will be used later on
        self.CH_NO: int = 0
        self.NOVEL_PATH = self.NOVEL_PAGE_INFO["NOVEL_PATH"].rstrip("/")
        self.ACCORDIAN_TXT = self.NOVEL_PAGE_INFO["ACCORDIAN_TXT"]
        # initialize here to avoid errors, as self.DATABASE is used after it
        ScrapiaShellHelper.__init__(
            self, self.NOVEL_PATH, novelName, self.ACCORDIAN_TXT
        )
        # create a DBHelper class and make NovelProfiler inherit it
        self.mydb, self.cursor = self.getConAndCur(self.DATABASE)
        self.CH_NO = self.getChapterNumberFrmDB(
            self.mydb, self.cursor, self.TABLE, self.NOVEL
        )

        self.driver = self.setup_browser(self.GECKO_EXE_PATH, isHeadless)

        self.prompt = colored(f"({self.NOVEL}) ", "red")

    intro = colored("Hi! Enter `help` for...well...help...", "green")

    def do_make_profile(self, *args) -> None:
        greenColorNovelName = colored(self.NOVEL, "green")
        echo(f"Starting profile creation for {greenColorNovelName}")

        self.makeNovelProfile(self.driver, self.NOVEL_PAGE_INFO["NOVEL_PAGE"])

    def do_nextPage(self, *args) -> None:
        """Finds and clicks the `Next` button"""
        self.driver.execute_script(self.clickElementStartingWithStrS("span", "Next"))

    def increment_ch_no(self, commitOnly: bool = False) -> None:
        """
        - Default behaviour: Increment `CH_NO` by 1
        - On setting `commit` to `True`: Don't increment, commit to database

        NOTE set `commit` to `True` only when program is about to/ made to end
        """

        if commitOnly:
            con, cur = self.getConAndCur(self.DATABASE)
            with con:
                cur.execute(f"UPDATE {self.TABLE} SET {self.NOVEL}={self.CH_NO};")
            return
        self.CH_NO += 1

    def scrape_gotoNextPage_sleep(self) -> None:
        """
        (NOTE) Order matters here. After successfully scraping a page, it will go
        to the next page and then sleep.
        
        Giving enough time to the content to load.
        """
        self.do_scrape()
        self.do_nextPage()
        sleep(int(self.cfg["PROJECT"]["SLEEP_TIME_AFTER_SCRAPE"]))

    def startScraping(self) -> None:
        """
        - `target` of `self.SCRAPER_THREAD` object.
        - invoked by `self.do_start_scraping` in a thread.
        """
        try:
            if not self.is_ready:
                self.do_setup()

            read_dict, toRead_dict = self.readJsonsReturnDict()
            indexList = list(toRead_dict.keys())

            scrapeCount = 0
            print("WHILE----------LOOP----------Initialized")
            while toRead_dict:
                self.scrape_gotoNextPage_sleep()
                # updating the values
                indexList, toRead_dict, read_dict = popFirstElementUpdateOtherDict(
                    indexList, toRead_dict, read_dict
                )

                scrapeCount += 1
                if scrapeCount % 5 == 0:
                    self.increment_ch_no(commitOnly=True)
                    saveNovelProfile(self, toRead_dict, read_dict)
                    scrapeCount = 0
            print("All present chapters scraped...\nEnding...")
            self.do_end_cleanly()
            saveNovelProfile(self, toRead_dict, read_dict)
            
        except KeyboardInterrupt:
            # save before ending
            saveNovelProfile(self, toRead_dict, read_dict)
            self.do_end_cleanly()
            print("KEYBOARD----------INTERRUPT----------INVOKED")
            return
        except Exception:
            saveNovelProfile(self, toRead_dict, read_dict)
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
            echo(f"We are in: \t{self.driver.current_url}")
        except Exception as e:
            echo(e + "\n\n" + "Try invoking `setup` first")
            return None

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
            self.driver = self.setup_browser(self.GECKO_EXE_PATH, self.isHeadless)
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
            self.__init__(self.isHeadless, novel_name, self.ctx)

    def do_scrape(self, *args) -> None:
        """`scrape` does the following:\n
        Get relevant content from the website and then save it in a file `NOVEL_SAVE_PATH`.\n
        Increment the value of global variable `CH_NO` by one and output the title of the webpage scraped."""

        if not self.is_ready:
            echo("Can run only after `setup` is invoked!")
            return None
        # the filename including the chapters from now on should be saved as `<last_part_of_url>.txt`

        URL_LAST_PART: str = self.driver.current_url.rstrip("/").split("/")[-1]

        # file_ext: str = "txt"  # default value
        file_ext = "html"
        story_content = self.driver.page_source

        # TODO save as f"Chapter-{customIndex}"
        with open(f"{self.NOVEL_PATH}/{URL_LAST_PART}.{file_ext}", "w") as f:
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
            echo("Installing addon...")
            self.installAddon_cleanTabs_getLoginWindow(self.driver)
            echo("Done. Sleeping for 2 seconds.")
            sleep(2)

            echo("logging in to website...")
            self.loginToWebsite(self.driver)
            echo("Done. Sleeping for 2 seconds.")
            sleep(2)

            # TODO put code to directly goto chapter, using indexed link
            toRead_dict = self.readJsonsReturnDict()[1]
            self.driver.get(toRead_dict[tuple(toRead_dict.keys())[0]][0])
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

    def do_start_scraping(self, *args):
        """This will run the `self.__start_scraping` helper function in a thread. This particular function also
        deals with any function calls that might try to `start` the same thread again."""
        try:
            self.SCRAPER_THREAD.start()
        except RuntimeError as e:
            print(e, "The function is probably already running!", sep="\n")
            return None


def saveNovelProfile(shellObj: ScrapiaShell, toRead_dict, read_dict):
    """
    1) Open json files corresponding to the inputted dict objects
    2) dump data in them
    """
    with open(shellObj.retFilePath("toRead"), "w") as save_toReadFobj, open(
        shellObj.retFilePath("read"), "w"
    ) as save_readFobj:
        dump(toRead_dict, save_toReadFobj, indent=2)
        dump(read_dict, save_readFobj, indent=2)


def popFirstElementUpdateOtherDict(keyList: list, *ds: dict | None):
    """
    1) pop first element from d1
    2) update d2 with popped element
    3) pop first element from keyList
    4) return elements in the order they were inputted
    """
    d1, d2 = ds
    if not d2:
        d1.pop(keyList.pop(0))
    else:
        d2.update({keyList[0]: d1.pop(keyList.pop(0))})
    return keyList, d1, d2

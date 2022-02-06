from time import sleep
from itertools import islice

from click import echo
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.firefox.webdriver import WebDriver

from .db import DBHelper
from .file_directory_worker import File_Directory_JSON_Worker


def get_hrefList(divList: list[WebElement]) -> list[str]:
    """
    1) Get the links to the chapters
    2) Return in ascending order
    """
    hrefList = []
    for divElement in divList:
        aList: list[WebElement] = divElement.find_elements(By.TAG_NAME, "a")
        hrefList.extend([a.get_attribute("href") for a in aList])
    return list(reversed(hrefList))


def convert_hrefList2Dict(hrefList: list[str]):
    """
    Convert inputted list to mapping of {custom_index: (link, custom_index)}

    NOTE: We assume `hrefList` starts from chapter-0
    """
    hrefDict: dict[int, tuple[str, int]] = {}
    for i, link in enumerate(hrefList):
        hrefDict[i] = (link, i)

    return hrefDict


class NovelProfiler(File_Directory_JSON_Worker, DBHelper):
    """
    Helper class to deal with "novel profiling" and more.
    """

    def __init__(
        self, novelPath: str, novelName: str, msg: tuple[str], accordianText: str
    ) -> None:
        echo(msg[1])
        File_Directory_JSON_Worker.__init__(self, novelPath, novelName, msg)
        DBHelper.__init__(self, msg)

        self.accordianText = accordianText

    def makeNovelProfile(self, driver: WebDriver, novelPageUrl: str):
        """
        1) create directory and subdirectories where <>_toRead.json and <>_read.json will exist.
        2) if they don't exist
        """
        ifExists = self.createDirectoriesReturnTrueIfExists()
        f_r, f_tR = self.readFiles(self.checkIfFilesExist())

        keys_f_r = tuple(f_r[1])
        keys_f_tR = tuple(f_tR[1])

        hrefDict = convert_hrefList2Dict(self.harvestChapterLinks(driver, novelPageUrl))
        print(keys_f_r, keys_f_tR, sep="\n")
        f_tRDict = {}

        keys_hrefDict = tuple(hrefDict)
        # if <>_toRead.json didn't or nothing existed initially
        if not (f_tR[0]) or not (ifExists) or (f_tR[1]):
            echo(f"Overwriting <>_toRead.json")
            f_tRDict = hrefDict

        # if <>_read.json didn't exist initially or is empty
        elif ((not f_r[1][0]) or f_r[0]) and keys_f_tR[-1] < keys_hrefDict[-1]:
            # slice hrefDict from the point where <>_toRead.json ends
            # to where hrefDict ends, and update the dict
            f_tR[1].update(dict(islice(hrefDict.items(), keys_f_tR[-1], None)))
            f_tRDict = f_tR[1]
            echo("<>_read.json is incompetent, slicing and updating")

        # now it's assured that <>_read.json is not empty
        else:
            f_tR[1].update(dict(islice(hrefDict.items(), keys_f_r[-1], None)))
            f_tRDict = f_tR[1]
            echo("<>_read.json is competent, slicing and updating")

        self.closeFileObjs((f_tR[-1], f_tRDict), (f_r[-1], f_r[1]))

    def harvestChapterLinks(self, driver: WebDriver, novelPageUrl: str):
        """
        1) Assuming in novel page -> open "Chapters" section
        2) Find div elements with chapter links
        3) Get the returned list of chapter links

        NOTE: You NEED to be in the novel_page for this to work
        """
        driver.get(novelPageUrl)
        sleep(5)

        driver.execute_script(self.clickElementWithInnerTextS("button", "chapters"))

        driver.execute_script(self.openAccordian(self.accordianText))
        sleep(2)

        clsTuple = ("grid", "grid-cols-1", "md:grid-cols-2", "w-full")
        divList = driver.find_elements(
            By.XPATH,
            self.getXpathStrFrClsNames("div", *clsTuple),
        )

        return get_hrefList(divList)

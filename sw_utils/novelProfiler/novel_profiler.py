from click import echo

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.firefox.webdriver import WebDriver

from .db import DBHelper
import jsHelpScripts as jshs


class NovelProfiler(DBHelper):
    """
    Helper class to deal with "novel profiling" and more.
    """

    def __init__(self) -> None:
        DBHelper.__init__(self)

    # TODO Rename this son
    # This will go into profiler class
    def openAccordians(self, driver: WebDriver) -> None:
        """
        1) Assuming in novel page -> open "Chapters" section
        2) Find div elements with chapter links
        3) Get the returned list of chapter links
        """

        if not self.is_ready:
            echo("Can run only after `setup` is invoked!")
            return None
        # The structure is quite simple, Dictionary{ tuple(lowerLimit, upperLimit): VolumeNumber }
        # starts from '2' because in the initial setup the first panel is open by default, clicking on it, will close
        # and hence, hide the chapters withing that panel.

        driver.execute_script(jshs.clickElementWithInnerTextS("button", "chapters"))

        clsTuple = ("grid", "grid-cols-1", "md:grid-cols-2", "w-full")
        divList = driver.find_elements(
            By.XPATH,
            jshs.getXpathStrFrClsNames("div", *clsTuple),
        )

        hrefList = self.get_hrefList(divList)
        # TODO ADD CODE HERE!!

    def get_hrefList(divList: list[WebElement]) -> list[str]:
        hrefList = []
        for divElement in divList:
            aList: list[WebElement] = divElement.find_elements(By.TAG_NAME, "a")
            hrefList.extend([a.get_attribute("href") for a in aList])
        return list(reversed(hrefList))

# scrapia_world = Scrape wuxia world...
from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.chrome.options import Options
from time import sleep      # for timeouts, cuz' you don't wanna get your IP banned...
from random import choice
from env_db import *
# hardcoding geckodrivers location programmatically is much easier...shrugs...they should've written this at the top...

def return_driver(name: str='FOX'):
    """This will return us a Firefox WebDriver object by default.\nUse for re-instantiating the `driver` object
    If `name` is given and not equal to `FOX`, a Chrome webdriver object will be returned."""
    if name != 'FOX':
        options = Options()
        options.add_argument("start-maximized")
        options.binary_location = "/opt/vivaldi/vivaldi"
        return Chrome(executable_path=EXECUTABLE_PATH_CHROME, options=options)
    return Firefox(executable_path=EXECUTABLE_PATH_GECKO)

driver = return_driver()

def end_cleanly() -> None:
    """Implements two functions:

    `increment_ch_no(commit=True)` and
    `driver.close()`
    \n
    Note that `end_cleanly` does 'NOT' end the program execution, it just ends the browser and commits
    to db."""
    increment_ch_no(commit=True)        # Test: use without cleaning all cookies first
    driver.quit()


try:
    # Problem detected...guest readers can only read 10 chapters...after that a pop interrupts and prompts you
    # to login/register, selenium `can` handle pop-ups, but I would rather do this and save some time for now.
    count = 0
    while CH_NO < LATEST_CH_NO:
        scrape(driver)
        sleep(28)       # DO NOT DELETE!!! Unless...you want to be seen as a bot and blocked?
        if count == 9:
            count = 0       # Count resets...obv...
            end_cleanly()   # if we're nearing the 10 chapter limit, we can call this
            driver = return_driver(name=choice(BROWSER_NAME_LIST))
        # optional, you could add a line to stop execution when a certain `CH_NO` has been scraped.
        count += 1

    print("All present chapters scraped...\nEnding...")
    end_cleanly()
except KeyboardInterrupt:
    end_cleanly()
except Exception as e:
    print("-------ERROR--------")
    print(e)
    end_cleanly()
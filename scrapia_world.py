# scrapia_world = Scrape wuxia world...
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Firefox
from time import sleep      # for timeouts, cuz' you don't wanna get your IP banned...
from env_db import *
# hardcoding geckodrivers location programmatically is much easier...shrugs...they should've written this at the top...

def return_driver():
    """This will return us a Firefox WebDriver object by default.\nUse for re-instantiating the `driver` object"""
    return Firefox(executable_path=EXECUTABLE_PATH_GECKO)

def install_addon_clean_tabs_get_login_window(driver) -> None:
    """Big name...ikr, this will first install an addon (`ghostery ad blocker`), then also go to the login window
    of wuxiaworld. After sleeping for 3 seconds the code will then begin to close any unwanted tabs (closes any tabs that are not `MAIN_HANDLE`)
    and also return focus to the login window.
    """

    # driver.install_addon('/opt/WebDriver/fox_ext/touch_vpn_secure_vpn_proxy_for_unlimited_access-4.2.1-fx.xpi')
    # Don't need the vpn if we're gonna with the click implementation
    driver.install_addon('/opt/WebDriver/fox_ext/ghostery_privacy_ad_blocker-8.5.5-an+fx.xpi')
    driver.install_addon('/opt/WebDriver/fox_ext/privacy_badger-2021.2.2-an+fx.xpi')
    driver.get("https://www.wuxiaworld.com/account/login")
    WebDriverWait(driver, 7).until(EC.presence_of_all_elements_located((By.TAG_NAME, "form")))

    driver.implicitly_wait(20)      # please setup touch vpn within this time...hopefully it works...


    MAIN_HANDLE: str = driver.current_window_handle     # Points to ww /account/login/
    for window_handle in driver.window_handles:
        if window_handle != MAIN_HANDLE:
            driver.switch_to.window(window_handle)
            driver.close()      # after closing all irrelevant tabs driver will focus back to the main one
    driver.switch_to.window(MAIN_HANDLE)    # Puts focus back on ww /account/login/
        # Use this stuff to setup the login window (You don't want any junk in some new tab)

# For god's sake, don't push this to github...
def login_key_strokes(driver) -> None:
    inputElement = driver.find_element_by_id('Email')
    inputElement.send_keys('<ENTER Email>')
    inputElement = driver.find_element_by_id('Password')
    inputElement.send_keys('<ENTER PASSWORD>')
    inputElement.send_keys(Keys.ENTER)
    sleep(5)

def end_cleanly() -> None:
    """Implements two functions:

    `increment_ch_no(commit=True)` and
    `driver.quit()`
    \n
    Note that `end_cleanly` does 'NOT' end the program execution, it just ends the browser and commits
    to db."""
    increment_ch_no(commit=True)        # Test: use without cleaning all cookies first
    driver.quit()


driver = return_driver()

install_addon_clean_tabs_get_login_window(driver)

login_key_strokes(driver)
# This makes us a "regular reader" (a reader that is registered) (made up term) (since unregistered users are called
# "guest readers")
# Until here, all we do is login, now we're going to the novel page

# New stuff below
driver.get("https://www.wuxiaworld.com/novel/against-the-gods/")

driver.find_element_by_partial_link_text("Chapters").click()

# This will open all the panels in the chapters section of ww /atg
# starts from '2' because in the initial setup the first panel is open by default, clicking on it, will close
# and hence, hide the chapters withing that panel.
try:
    for volume_no in range(2, 19):
        driver.find_element_by_partial_link_text(f"Volume {volume_no} ").click()
except Exception as e:
    print(e)
finally:    # To do, add this stuff in a function or make it work as a method
    pass

# Now we go to the relevant chapter or `CH_NO`
driver.find_element_by_partial_link_text("Chapter " + str(CH_NO) + " ").click()
# BASE_URL[26: ] = /novel/against-...
# New stuff above

try:
    while CH_NO < LATEST_CH_NO:
        scrape(driver)
        sleep(28)       # DO NOT DELETE!!! Unless...you want to be seen as a bot and blocked?
        # optional, you could add a line to stop execution when a certain `CH_NO` has been scraped.

    print("All present chapters scraped...\nEnding...")
except KeyboardInterrupt:
    # end_cleanly()
    pass
except Exception as e:
    print("-------ERROR--------")
    print(e)
    # end_cleanly()
    pass
finally:
    end_cleanly()

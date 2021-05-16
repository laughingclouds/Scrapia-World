"""This has both the environment variables that are to be used by our code
and also the different functions for working with the database."""
from os import environ      # for loading all the env vars in the global namespace
import mysql.connector      # for working with the database


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    database="wuxiaworld",
    password=environ['PASSWORD']
)
cursor = mydb.cursor(dictionary=True)


# initialising all the required global variables
EXECUTABLE_PATH_GECKO: str = environ['EXECUTABLE_PATH_GECKO']
EXECUTABLE_PATH_CHROME: str = environ['EXECUTABLE_PATH_CHROME']
FOX_EXT_BASE_PATH: str = environ['FOX_EXT_BASE_PATH']
BASE_URL: str = environ['BASE_URL']
NOVEL_BASE_PATH: str = environ['NOVEL_BASE_PATH']
LATEST_CH_NO: int = int(environ['LATEST_CH_NO'])
CH_NO: int = 0


cursor.execute("SELECT * FROM last_chapter;")
for row in cursor:
    CH_NO = row['LAST_CH_NO']


def increment_ch_no(commit: bool = False) -> None:
    """This function `by default`, will only increment `CH_NO` by 1.\n
    But, setting `commit` to `True` will make it 'NOT INCREMENT' `CH_NO` and rather
    just commit to database.
    
    `commit` is to be set to `True` only when the script is about to close selenium."""

    global CH_NO, mydb, cursor
    if commit:
        cursor.execute(f"UPDATE last_chapter SET LAST_CH_NO = {CH_NO};")
        mydb.commit()
        return
    CH_NO += 1


def scrape(driver) -> None:
    """`scrape` does the following:\n
    Get relevant content from the website and then save it in a file `NOVEL_BASE_PATH`.\n
    Increment the value of global variable `CH_NO` by one and output the title of the webpage scraped."""

    driver.get(BASE_URL + str(CH_NO))       # CH_NO's value is queried from the db everytime the code is executed.
    story_content, title = driver.find_element_by_id('chapter-content').text, driver.title

    with open(NOVEL_BASE_PATH + title, 'w') as f:
        f.write(story_content)
    increment_ch_no()

    print(f"{title} scraped successfully...\n")

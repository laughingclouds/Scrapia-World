# Scrapia-World

A web scraper for scraping wuxiaworld, written in python, using selenium and both gecko and chrome drivers.

**Note:**

1. I don't have any releases setup in pypi, and I probably don't want to use that space for this project (I just prefer that). So you will have to do with either the _latest-release_ or the latest _pre-release_. (I will do my best to keep even the pre-release; only the latest one: as functional as I can keem them).
2. This readme might not always be upto date so I'd rather you just go to the latest release (or pre-release)

**Setting up:**

1. Latest releases of scrapia-world use only firefox as the earlier requirement of using vivaldi as well has been made void due to a few improvements. Open `novel_page_info.json` and make changes to the different paths in accordance to your wishes. I assure you the latest release won't break because of any hotch potch in the paths.
2. The `.env` file is required for storing the password to the database. You can eazily make changes in the code (remove the `load_dotenv` function call) to use any other method to use virtual environments. The `email` and `password` for logging in should not be moved though. If they are, please make necessary changes in the source code (in the class `InteractiveShell` in `scrapia_shell.py`).
3. You need a database!!: Significant changes have been made in later releases in the way the database is used (or structured). For now here's how things should be:

* Set the value of **DATABASE** in **novel_page_info.json** and create a database with that name.
* Set the value of **TABLE** in **novel_page_info.json** and create a table with that name.
* This is how the table structure should be:

abreviated_novel_name1 | abreviated_novel_name2 | abreviated_novel_name3 | ...
------------------------ | ------------------------ | ------------------------ | ---
chapter no. | chapter no. | chapter no. | ...

Something like this:
![database table structure](https://user-images.githubusercontent.com/57110219/120084992-46f4d080-c0f2-11eb-8ad1-56d0c33c0c23.png)

It is recommended to set the default value of every column to the integer value of the first chapter number of a novel.

4. For the other stuff, I'll add in a requirements.txt which you can `pip install -r requirements.txt` within a virtual environment.


```sql
CREATE TABLE "novel" (
 "ATG" INTEGER DEFAULT 0,
 "OG" INTEGER DEFAULT 0
);
```

SQL code for creating the table.

**Webdrivers:**
Browser | Recommended Driver | ...
------- | ------------------ | ---
Vivaldi | [chromedriver](https://chromedriver.chromium.org/downloads)
Chromium | [chromedriver](https://chromedriver.chromium.org/downloads)
Firefox | [geckodriver](https://github.com/mozilla/geckodriver/releases)

1. You will need to link to vivaldi's binary file instead of chromes' to use it. This [stackoverflow question](https://stackoverflow.com/questions/59644818/how-to-initiate-a-chromium-based-vivaldi-browser-session-using-selenium-and-pyth) might help you out. For me binary's path was `/opt/vivaldi/vivaldi` (I use linux btw)
2. Chromedriver version for vivaldi: 
  - In the url area, enter ``vivaldi://about/``.
  - The version of chromium your vivaldi is based on should be visible in the "user agent" field.
  - Install chromedriver for this specific version.
3. If you use linux and want to work with vivaldi, you can just copy the code from the [v0.1.0-alpha](https://github.com/r3a10god/Scrapia-World/blob/v0.1.0-alpha/scrapia_world.py) release.
4. Using the drivers for chromium and firefox should be easy.

**Things to add:**

1. I have taken to adding a docstring at the top of the source files, might not be a good practise...but meh...I'll see what I can do later on.

**Issues:**

1. You can track any known issues from the [issues tab] (<https://github.com/r3a10god/Scrapia-World/issues>).
2. If you find any issues then feel free to raise them.

**Current capability and a few thoughts:**

1. I wanted to read the novel, that's it. And that's what this script helps me with. Therefore, I made it to scrape only two things from a page. The page title, and the relevant text. The title of the page is what will become the name of the text file associated with that page, and the relevant text will be stored in that text file. Hence, it scrapes the raw text of a chapter.
2. I plan to make new stuff that would deal with that raw text. I could've downloaded the whole page source and made a script to edit that, but I didn't feel the need to do so.

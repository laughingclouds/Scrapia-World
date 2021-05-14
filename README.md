# Scrapia-World
A web scraper for scraping wuxiaworld, written in python, using selenium and both gecko and chrome drivers.

Current capability and a few thoughts:
1. I wanted to read the novel, that's it. And that's what this script helps me with. Therefore, I made it to scrape only two things from a page. The page title, and the relevant text. The title of the page is what will become the name of the text file associated with that page, and the relevant text will be stored in that text file. Hence, it scrapes the raw text of a chapter.
2. I plan to make new stuff that would deal with that raw text. I could've downloaded the whole page source and made a script to edit that, but I didn't feel the need to do so.

DON'T BE AN IDIOT:
1. If this is your first time webscraping (like me), then please, don't be an idiot (read as some other word that fits this context) when you scrape. What this simply means is don't mess with the `sleep()` function and the time limit I've set in it. You could at most make it 24-28 seconds. But any less and you're going to a danger zone. Those guys will ban your IP if you're acting too rowdy.
2. Although many suggest 10-15 seconds as an appropiate gap between requests, I don't want to take any risks and be IP banned by one of my most favorite sites.

Note: 
1. It uses the vivaldi browser instead of chrome/chromium.
2. The system where this code was developed is a linux system, hence all file links are like what you will find in most linux systems.
3. The code can be tweaked to scrape any novel but this implementation scrapes specifically ATG (you know it if you know it)
4. Why are two web browsers being used? Wuxiaworld has a chapter limit of 10 for anonymous 'guest readers'. That would mean after you navigate 10 chapters in that site, you're getting a pop-up, so my implementation; after a certain iteration count has been reached, resets the count and just simply randomly chooses a webdriver. This might not have been required as you can also simply restart the browser, but I felt like implementing it...so I did... ;).

Setting up:
1. Make sure you have geckodriver and chromedriver installed, put both of them in a file called `/opt/webdriver/bin/`. Hence, if you install these drivers, the path to these executables will look like `/opt/webdriver/bin/geckodriver` and `/opt/webdriver/bin/chromedriver`.
2. Version of chrome driver for `Vivaldi 3.8.2259.40` to be used is `Chrome 90`. How do I know this? I installed the chromedriver of the latest chrome version and I got an error message saying that my chrome version was Chrome 90.x.y.z (But I don't have chrome! So that was actually the chrome version associated to vivaldi 3.8...hopefully I'm correct...the code works though.)
3. Because of the way I've written my code, the '.env' file is required. The variable names in it are quite self-explanatory, but I might add some small info on them later on.
4. You need a database!!: I used mysql(unfortunately that's all I know) to keep track of a variable called `LAST_CH_NO`, this is what will help the scraper to automatically start scraping from where it left off(if you decide to stop execution).
5. For the other stuff, I'll add in a requirements.txt which you can `pip install -r requirements.txt` within a virtual environment.

Webdriver:
1. For using Vivaldi, use chromedriver
2. For using Firefox, use geckodriver...reason? Go check the selenium documentation, I can't explain each and every thing in this repo.


Things to add:
1. (A thing you could add yourself too:) Make the code stop after a certain number of chapter count has been reached. For this repos' implementation, you can simply check what the value of `CH_NO` is after every iteration of our infinite loop.
2. Maybe an addblocker? But then I would have to download and install it every time my browser runs (I think), so I need a method to keep my 
3. Maybe make the presentation in this readme better? (I don't quite know how to beautify .md's...I'm lazy...this is a cry for help...please raise an issue or whatever is required if you'd like to help me format this readme in a better way. Thanks in advance!)
4. Add a way to work with the output (the chapter text files).


Issues:
1. None...so far, please raise them if you find any.

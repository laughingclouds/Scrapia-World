# Scrapia-World
A web scraper for scraping wuxiaworld, written in python, using selenium and both gecko and chrome drivers.

Note: 
1. It uses the vivaldi browser instead of chrome/chromium.
2. The system where this code was developed is a linux system, hence all file links are like what you will find in most linux systems.

Setting up:
1. Make sure you have geckodriver and chromedriver installed, put both of them in a file called `/opt/webdriver/bin/`. Hence, if you install these drivers, the path to these executables will look like `/opt/webdriver/bin/geckodriver` and `/opt/webdriver/bin/chromedriver`.
2. Version of chrome driver for `Vivaldi 3.8.2259.40` to be used is `Chrome 90`. How do I know this? I installed the chromedriver of the latest chrome version and I got an error message saying that my chrome version was Chrome 90.x.y.z (But I don't have chrome! So that was actually the chrome version associated to vivaldi 3.8...hopefully I'm correct...the code works though.)

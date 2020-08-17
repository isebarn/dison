from shutil import which

SELENIUM_DRIVER_NAME = 'firefox'
SELENIUM_DRIVER_EXECUTABLE_PATH = which('geckodriver')
SELENIUM_DRIVER_ARGUMENTS=['-headless']

DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800
}
DEFAULT_REQUEST_HEADERS = {
    'Referer': 'http://www.google.com' 
}
# Scrapy settings for dison project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'dison'

SPIDER_MODULES = ['dison.spiders']
NEWSPIDER_MODULE = 'dison.spiders'
USER_AGENT = 'Mozilla/5.0'
LOG_LEVEL = 'ERROR'  # to only display errors
LOG_FORMAT = '%(levelname)s: %(message)s'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'dison (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32
DOWNLOAD_DELAY = 1

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'dison.middlewares.RotateUserAgentMiddleware.RotateUserAgentMiddleware': 543,
}
# Scrapy settings for dison project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from shutil import which

SELENIUM_DRIVER_NAME = 'firefox'
SELENIUM_COMMAND_EXECUTOR = which('geckodriver')
#SELENIUM_DRIVER_ARGUMENTS=['-headless']

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
CONCURRENT_REQUESTS_PER_DOMAIN = 16
DOWNLOAD_DELAY = 0
DOWNLOADER_MIDDLEWARES = {
  'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
  'scrapy_selenium.SeleniumMiddleware': 800
}
#DOWNLOADER_MIDDLEWARES = {
  #'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
  #'dison.middlewares.RotateUserAgentMiddleware.RotateUserAgentMiddleware': 543,
 # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
  #'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
#}


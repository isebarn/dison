from selenium import webdriver
import selenium as se
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import urllib3
import time
from urllib.parse import urlparse, parse_qs
import os
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random
urls = ['https://www.amazon.com/s?i=digital-text&bbn=154790011&rh=n%3A133140011%2Cn%3A154606011%2Cn%3A154754011%2Cn%3A154786011%2Cn%3A154790011%2Cn%3A10332441011%2Cp_n_feature_nine_browse-bin%3A3291437011&dc&qid=1597051787&rnid=154790011&ref=sr_nr_n_1']
driver = webdriver.Remote(os.environ.get('BROWSER'), DesiredCapabilities.FIREFOX)

def fetch_page(page):
  http = urllib3.PoolManager()
  r = http.request("GET", page)
  soup = BeautifulSoup(r.data, features="lxml")

  return soup

if __name__ == '__main__':
  for url in urls:
    soup = fetch_page(url)
    print(soup)
from time import time
from pprint import pprint
from urllib.parse import urlparse
import re
import os
from random import choice

if __name__ == '__main__':
  from ORM import Operations, Book
  from Email import Email

else:
  from dison.spiders.ORM import Operations, Book
  from dison.spiders.Email import Email

from selenium import webdriver
import selenium as se
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType
import threading
from time import sleep
from multiprocessing import Queue
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_isbn(paperback_url):
  paperback_isbn_string = re.search(r'dp/(\d+)/ref', paperback_url)

  if paperback_isbn_string != None:
    return paperback_isbn_string.group(1)

  paperback_isbn_string = re.search(r'dp/(\d+)X/ref', paperback_url)

  if paperback_isbn_string != None:
    return paperback_isbn_string.group(1)

  paperback_isbn_string = re.search(r'dp/(.*?)/ref', paperback_url)
  if paperback_isbn_string != None:
    return paperback_isbn_string.group(1)

def handle_block(proxy_queue, proxy, driver):
  proxy_queue.put(proxy)
  driver.delete_all_cookies()
  driver.close()

def parse_page(proxy_queue, url_queue, proxy):
  proxy_config = {'httpProxy': proxy['proxy'], 'sslProxy': proxy['proxy']}
  proxy_object = Proxy(raw=proxy_config)
  capabilities = DesiredCapabilities.FIREFOX
  options = Options()
  options.headless = True
  proxy_object.add_to_capabilities(capabilities)

  try:
    driver = webdriver.Remote(os.environ.get("BROWSER"), options=options, desired_capabilities=capabilities)
    driver.set_page_load_timeout(10)
  
  except Exception as e:
    proxy_queue.put(proxy)
    sleep(5)
    return

  while url_queue.qsize() > 0:
    try:
      url = url_queue.get()

      book_url = url['url']
      if '://' not in book_url:
        book_url = 'https://' + book_url

      try:

        driver.get(book_url)
      except TimeoutException as e:
        continue

      except Exception as e:
        handle_block(proxy_queue, proxy, driver)

      try:
        driver.find_element_by_id("captchacharacters")
        handle_block(proxy_queue, proxy, driver)
        return

      except NoSuchElementException as e:
        pass

      # MAIN LOGIC
      try:

        book = {'id': url['id']}

        # Book title
        try:
          element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "productTitle")))
          book['Title'] = driver.find_element_by_id("productTitle").text

        except NoSuchElementException as e:
          handle_block(proxy_queue, proxy, driver)
          return

        # Author
        try:
          book['Author'] = driver.find_element_by_xpath("//a[@data-asin]").text

        except NoSuchElementException as e:
          try:
            book['Author'] = driver.find_element_by_xpath("//span[@class='author notFaded']/a").text

          except NoSuchElementException as e:
            pass

        # language
        book['Language'] = None
        try:
          book['Language'] = driver.find_element_by_xpath("//b[contains(text(), 'Language:')]/..").text

        except NoSuchElementException as e:
          pass
        except Exception as e:
          pass

        if book['Language'] == None:
          try:
            book['Language'] =  driver.find_element_by_xpath("//span[contains(text(), 'Language:')]/..").text.split(":")[-1]

          except NoSuchElementException as e:
            pass
          except Exception as e:
            pass

        if book['Language'] == None:
          book['Language'] = ''

        book['LanguageID'] = Operations.GetOrCreateLanguage(book['Language'].strip()).Id

        # kindle categories
        try:
          categories = driver.find_element_by_id('detailBullets_feature_div').find_elements_by_xpath(".//following-sibling::ul/li/span/span/span/a")
          kindle_category_names = [x.text for x in categories[1:]]
          kindle_category_urls = [x.get_attribute('href') for x in categories[1:]]

          if len(kindle_category_names) > 0:
            book['eBookCategory_1'] = Operations.GetOrCreateEBookCategory(kindle_category_names[0], kindle_category_urls[0]).Id
          else:
            book['eBookCategory_1'] = None

          if len(kindle_category_names) > 1:
            book['eBookCategory_2'] = Operations.GetOrCreateEBookCategory(kindle_category_names[1], kindle_category_urls[1]).Id

          else:
            book['eBookCategory_2'] = None

          if len(kindle_category_names) > 2:
            book['eBookCategory_3'] = Operations.GetOrCreateEBookCategory(kindle_category_names[2], kindle_category_urls[2]).Id

          else:
            book['eBookCategory_3'] = None

        except NoSuchElementException as e:
          pass
        except Exception as e:
          pass

        book['PaperbackURL'] = None
        book['PaperbackISBN'] = None
        try:
          book['PaperbackURL'] = driver.find_element_by_xpath("//a/span[contains(text(), 'Paperback')]/..").get_attribute('href')
          try:
            book['PaperbackISBN'] = parse_isbn(book['PaperbackURL'])
          except Exception as e:
            book['PaperbackISBN'] = ''

        except NoSuchElementException as e:
          pass
        except Exception as e:
          pass

        Operations.UpdateBook(book)

      except Exception as e:
        handle_block(proxy_queue, proxy, driver)
        print(e)
        return

    except Exception as e:
      handle_block(proxy_queue, proxy, driver)

    sleep(1)

  handle_block(proxy_queue, proxy, driver)

if __name__ == '__main__':
  count = 1

  while count > 0:
    urls = list(Operations.QueryUnfetchedBooks(2000))
    count = len(urls)
    url_queue = Queue()
    for url in urls:
      url_queue.put({"url": url.URL, "id": url.Id})

    ROTATING_PROXY_LIST = ['p.webshare.io:20000','p.webshare.io:20001','p.webshare.io:20002','p.webshare.io:20003','p.webshare.io:20004','p.webshare.io:20005','p.webshare.io:20006','p.webshare.io:20007','p.webshare.io:20008','p.webshare.io:20009']
    proxy_queue = Queue()
    for proxy in ROTATING_PROXY_LIST:
      proxy_queue.put({"proxy": proxy, "enabled": True, "block_time": None})

    threads = []
    start_time = time()
    timer = 0
    print('restart')
    while url_queue.qsize() > 0 and timer < 500:
      timer = time() - start_time
      print("Queue: {} - Proxies: {} - Time: {}".format(url_queue.qsize(), proxy_queue.qsize(), timer))
      if proxy_queue.qsize() > 0:
        thread = threading.Thread(target=parse_page,
          args=(proxy_queue, url_queue, proxy_queue.get()))
        thread.start()
        threads.append(thread)

      else:
        sleep(10)

    for thread in threads:
      thread.join()
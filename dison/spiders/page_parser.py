import scrapy
from scrapy import signals
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

from scrapy_selenium import SeleniumRequest
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

def handle_block(next_page, url_queue, url, proxy_queue, proxy, driver):
  next_page = None
  proxy['enabled'] = False
  url_queue.put(url)
  proxy_queue.put(proxy)
  driver.close()

def parse_page(proxy_queue, url_queue, book_queue):
  url = url_queue.get()
  proxy = proxy_queue.get()

  if proxy['enabled'] == False:
    print("Proxy blocked: {}".format(proxy['proxy']))
    sleep(100)

  proxy['enabled'] = True
  next_page = True
  sleep(choice([4, 5, 6, 7]))

  proxy_config = {'httpProxy': proxy['proxy'], 'sslProxy': proxy['proxy']}
  proxy_object = Proxy(raw=proxy_config)
  capabilities = DesiredCapabilities.FIREFOX
  proxy_object.add_to_capabilities(capabilities)

  driver = webdriver.Remote(os.environ.get("BROWSER"), desired_capabilities=capabilities)
  driver.get(url['url'])

  try:
    driver.find_element_by_id("captchacharacters")
    handle_block(next_page, url_queue, url, proxy_queue, proxy, driver)
    return

  except Exception as e:
    pass


  try:
    parsed_uri = urlparse(url['url'])
    marketplace = '{uri.netloc}'.format(uri=parsed_uri)
    marketplace = Operations.GetOrCreateMarketplace(marketplace)

  except Exception as e:
    handle_block(next_page, url_queue, url, proxy_queue, proxy, driver)
    return

  try:
    departments = driver.find_elements_by_xpath("//div[@id='departments']/ul/li")

    department = departments[1].text if len(departments) > 1 else ''
    department = Operations.GetOrCreateDepartment(department)

    category = departments[2].text if len(departments) > 2 else ''
    category = Operations.GetOrCreateCategory(category)

    if len(departments) > 3:
      subcategory = departments[3].text
      subcategory = Operations.GetOrCreateCategory(subcategory)

    else:
      raise Exception()

    subsubcategory = departments[4].text if len(departments) > 4 else ''
    subsubcategory = Operations.GetOrCreateCategory(subsubcategory)

    subsubsubcategory = departments[5].text if len(departments) > 5 else ''
    subsubsubcategory = Operations.GetOrCreateCategory(subsubsubcategory)



  except Exception as e:
    handle_block(next_page, url_queue, url, proxy_queue, proxy, driver)
    return


  book_list = []
  while next_page != None:
    sleep(choice([4, 5, 6, 7]))
    next_page = None

    try:
      current_page = driver.find_element_by_xpath("//ul/li[@class='a-selected']").text
      last_page = driver.find_elements_by_xpath("//ul/li[@class='a-disabled']")[-1].text
      print("{}/{}: {}".format(current_page, last_page, proxy['proxy']))
    except Exception as e:
      pass

    try:

      books = driver.find_elements_by_xpath("//img[@class='s-image']/../..")
      book_urls = [book.get_attribute('href') for book in books]

      if len(book_urls) == 0:
        books = driver.find_elements_by_xpath("//a[@class='a-link-normal a-text-normal']")
        book_urls = [book.get_attribute('href') for book in books]

      if len(book_urls) == 0: break

      for book_url in book_urls:
        book = Book()
        book.ASIN = re.search(r'dp/(.*?)/ref', book_url).group(1)
        book.URL = book_url
        book.SearchURLID = url['id']
        book.MarketplaceID = marketplace.Id
        book.DepartmentID = department.Id
        book.CategoryID = category.Id
        book.SubCategoryID = subcategory.Id
        book.SubSubCategoryID = subsubcategory.Id
        book.SubSubSubCategoryID = subsubsubcategory.Id

        book_queue.put(book)



    except Exception as e:
      handle_block(next_page, url_queue, url, proxy_queue, proxy, driver)
      return

    try:
      if driver.find_element_by_xpath("//ul/li[@class='a-last']/a") != None:
        next_page = driver.find_element_by_xpath("//ul/li[@class='a-last']/a")

      elif driver.find_element_by_xpath("//ul/li[@class='a-selected']/following-sibling::li") != None:
        next_page = driver.find_element_by_xpath("//ul/li[@class='a-selected']/following-sibling::li")

      elif driver.find_elements_by_xpath("//ul/li[@class='a-normal']") != None:
        next_page = driver.find_elements_by_xpath("//ul/li[@class='a-normal']")[-1]


      if next_page != None:
        try:
          url['url'] = next_page.get_attribute('href')
          next_page.click()

        except Exception as e:
          pass

    except Exception as e:
      handle_block(next_page, url_queue, url, proxy_queue, proxy, driver)


  proxy_queue.put(proxy)
  driver.close()

def save_book_thread(book_queue):
  while book_queue != None:
    print("Book queue: {}".format(book_queue.qsize()))
    while book_queue.qsize() > 0:
      Operations.SaveBook(book_queue.get())

    sleep(10)


if __name__ == '__main__':
  book_queue = Queue()
  book_thread = threading.Thread(target=save_book_thread, args=(book_queue,))
  book_thread.start()

  urls = list(Operations.GetSites())
  url_queue = Queue()
  for url in urls:
    url_queue.put({"url": url.Value, "id": url.Id})

  ROTATING_PROXY_LIST = ['p.webshare.io:19999','p.webshare.io:20000','p.webshare.io:20001','p.webshare.io:20002','p.webshare.io:20003']
  proxy_queue = Queue()
  for proxy in ROTATING_PROXY_LIST:
    proxy_queue.put({"proxy": proxy, "enabled": True, "block_time": None})


  while url_queue.qsize() > 0:
    print("Queue: {}".format(url_queue.qsize()))
    if proxy_queue.qsize() > 0:
      print("Proxies: {}".format(proxy_queue.qsize()))
      thread = threading.Thread(target=parse_page, args=(proxy_queue, url_queue, book_queue))
      thread.start()
      sleep(1)

    else:
      sleep(10)

  book_queue = None
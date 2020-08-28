import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from time import time
from pprint import pprint
import os
import re
import logging

import urllib3
import time
from datetime import datetime, timedelta
import urllib.parse as urlparse
from urllib.parse import parse_qs
import threading
from multiprocessing import Queue
from time import sleep
from urllib3 import ProxyManager, make_headers
from random import choice

if __name__ == '__main__':
  from ORM import Operations, Book
  from Email import Email

else:
  from dison.spiders.ORM import Operations, Book
  from dison.spiders.Email import Email

def output(text):
  with open("output.txt", "a") as text_file:
      text_file.write("\n{}".format(text))

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

class MyException(Exception):
  pass


class BookSpider(scrapy.Spider):
  name = "book"
  ready = []
  ROTATING_PROXY_LIST = ['p.webshare.io:19999','p.webshare.io:20000','p.webshare.io:20001','p.webshare.io:20002','p.webshare.io:20003']
  success = 0
  fail = 0
  def start_requests(self):
    self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2840.71 Safari/539.36'}

    for book in Operations.QueryUnfetchedBooks()[0:500]:
      yield scrapy.Request(url=book.URL,
        callback=self.parser,
        errback=self.errbacktest,
        headers=self.headers,
        meta={'id': book.Id, 'proxy': choice(self.ROTATING_PROXY_LIST)})

  def exception_is_ban(self, request, exception):
      # override method completely: don't take exceptions in account
      return False

  def response_is_ban(self, request, response):
    if b'Type the characters you see in this image' in response.body \
      or b'Sorry, we just need to make sure you' in response.body \
      or b'productTitle' not in response.body \
      or b'To discuss automated access to Amazon data please contact' in response.body:

      #output("BANNED: {}".format(response.meta.get('proxy')))
      return True

    return False

  def parser(self, response):
    book = {'id': response.meta.get('id')}
    book['Title'] = response.xpath("//span[@id='productTitle']/text()").extract_first()
    if book['Title'] == None:
      self.fail += 1
      return

    book['Title'] = book['Title'].replace('\n', '')
    output("{}: {}".format(response.meta.get('proxy'), book['Title']))

    # author
    book['Author'] = response.xpath("//a[@data-asin]/text()").extract_first()
    if book['Author'] == None:
      book['Author'] = response.xpath("//span[@class='author notFaded']/a/text()").extract_first()

    # language
    try:
      language = response.xpath("//b[contains(text(), 'Language:')]").xpath("../text()").extract_first(None)
      if language == None:
        language = response.xpath("//span[contains(text(), 'Language:')]").xpath("../text()").extract_first(None)

      book['LanguageID'] = Operations.GetOrCreateLanguage(language.strip()).Id

    except Exception as e:
      output('language: {}'.format(response.url))

    # kindle categories
    try:
      kindle_category_names = response.xpath("//li[@id='SalesRank']/ul/li/..//a/text()").extract()
      kindle_category_urls = response.xpath("//li[@id='SalesRank']/ul/li/..//a/@href").extract()

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

    except Exception as e:
      output('Kindle categories: {}'.format(response.url))

    # paperback URL
    try:
      book['PaperbackURL'] = response.xpath("//a/span[contains(text(), 'Paperback')]").xpath("../@href").extract_first()
      try:
        book['PaperbackISBN'] = parse_isbn(book['PaperbackURL'])
      except Exception as e:
        book['PaperbackISBN'] = ''

    except Exception as e:
      output('paperback URL: {}'.format(response.url))

    self.success += 1

    Operations.UpdateBook(book)


  def errbacktest(self, failiure):
    pass

  @classmethod
  def from_crawler(cls, crawler, *args, **kwargs):
    spider = super().from_crawler(crawler, *args, **kwargs)
    crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
    return spider

  def spider_closed(self, spider):
    print("Saved: {}".format(self.c))
    pass

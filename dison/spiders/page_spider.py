import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from time import time
from pprint import pprint
import os
import re
from random import choice
from urllib.parse import urlparse

if __name__ == '__main__':
  from ORM import Operations, Book

else:
  from dison.spiders.ORM import Operations, Book

class RootSpider(scrapy.Spider):
  name = "page"
  department = "//div[@id='departments']/ul/li[2]/span/a/span/text()"
  category = "//div[@id='departments']/ul/li[3]/span/a/span/text()"
  subcategory = "//div[@id='departments']/ul/li[4]/span/a/span/text()"
  subcategory_backup = "//div[@id='departments']/ul/li[4]/span/span/text()"
  subsubcategory = "//div[@id='departments']/ul/li[5]/span/a/span/text()"
  subsubcategory_backup = "//div[@id='departments']/ul/li[5]/span/span/text()"
  subsubsubcategory = "//div[@id='departments']/ul/li[6]/span/span/text()"
  ROTATING_PROXY_LIST = ['p.webshare.io:19999','p.webshare.io:20000','p.webshare.io:20001','p.webshare.io:20002','p.webshare.io:20003']

  def start_requests(self):
    start_urls = Operations.QueryPageSearch()

    if len(start_urls) == 0:
      sites = Operations.GetSites()
      for site in sites:
        Operations.UpdatePageSearch({'id': site.Id, 'value': site.Value})

    start_urls = Operations.QueryPageSearch()

    for url in start_urls:
      if url.Value is not None:
        search_url = url.Value
        if '://' not in search_url:
          search_url = 'https://' + search_url

        yield scrapy.Request(url=search_url,
          callback=self.parser,
          errback=self.errbacktest,
          meta={'root': url.Id, 'proxy': choice(self.ROTATING_PROXY_LIST)})

  def parser(self, response):
    # If blocked, we return
    if 'productTitle' not in response.text:
      return

    # Get marketplace from the URL
    parsed_uri = urlparse(response.url)
    marketplace = '{uri.netloc}'.format(uri=parsed_uri)
    marketplace = Operations.GetOrCreateMarketplace(marketplace)

    # get department
    department = response.xpath(self.department).extract_first('')
    department = Operations.GetOrCreateDepartment(department)

    # get category
    category = response.xpath(self.category).extract_first('')
    category = Operations.GetOrCreateCategory(category)

    # get subcategory
    subcategory = response.xpath(self.subcategory).get()
    subcategory = subcategory if subcategory != None else response.xpath(self.subcategory_backup).extract_first('')
    subcategory = Operations.GetOrCreateCategory(subcategory)

    # get subsubcategory
    subsubcategory = response.xpath(self.subsubcategory).get()
    subsubcategory = subsubcategory if subsubcategory != None else response.xpath(self.subsubcategory_backup).extract_first('')
    subsubcategory = Operations.GetOrCreateCategory(subsubcategory)

    # get subsubsubcategory
    subsubsubcategory = response.xpath(self.subsubsubcategory).extract_first('')
    subsubsubcategory = Operations.GetOrCreateCategory(subsubsubcategory)

    images = response.xpath("//div[@data-asin]/..//a/div/img")
    book_urls = [marketplace.Value + x.xpath("../../@href").extract_first() for x in images]

    if len(book_urls) == 0:
      title_urls = response.xpath("//a[@class='a-link-normal a-text-normal']/@href").extract()
      book_urls = [marketplace.Value + x.xpath("../../@href").extract_first() for x in images]

    if len(book_urls) == 0: return

    for book_url in book_urls:
      book = Book()
      book.ASIN = re.search(r'dp/(.*?)/ref', book_url).group(1)
      book.URL = book_url
      book.SearchURLID = response.meta.get('root')
      book.MarketplaceID = marketplace.Id
      book.DepartmentID = department.Id
      book.CategoryID = category.Id
      book.SubCategoryID = subcategory.Id
      book.SubSubCategoryID = subsubcategory.Id
      book.SubSubSubCategoryID = subsubsubcategory.Id

      Operations.SaveBook(book)

    next_page = None
    if response.xpath("//ul/li[@class='a-last']/a").extract_first(None) != None:
      next_page = marketplace.Value + response.xpath("//ul/li[@class='a-last']/a/@href").extract_first(None)

    elif response.xpath("//ul/li[@class='a-selected']/following-sibling::li/@href").extract_first(None) != None:
      next_page = marketplace.Value + response.xpath("//ul/li[@class='a-selected']/following-sibling::li/@href").extract_first(None)

    elif len(response.xpath("//ul/li[@class='a-normal']/@href").extract()) > 0:
      next_page = marketplace.Value + response.xpath("//ul/li[@class='a-normal']/@href").extract()[-1]

    Operations.UpdatePageSearch({'id': response.meta.get('root'), 'value': next_page})


  def errbacktest(self, failiure):
    pass

  @classmethod
  def from_crawler(cls, crawler, *args, **kwargs):
    spider = super().from_crawler(crawler, *args, **kwargs)
    crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
    return spider

  def spider_closed(self, spider):
    pass

if __name__ == "__main__":
  process = CrawlerProcess({
      'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
  })

  process.crawl(RootSpider)
  process.start()
import scrapy
from scrapy import signals
from time import time
from pprint import pprint
from urllib.parse import urlparse
import re
import os

try:
  from dison.spiders.ORM import Operations, Book

except Exception as e:
  from ORM import Operations, Book


class ListSpider(scrapy.Spider):
  name = "root"
  counter = 0
  books = []
  sql_insert_time = 0
  sql_query_kindle_and_language = 0


  def start_requests(self):
    self.pages = int(getattr(self, 'pages', 5))
    start_urls = Operations.GetSites()

    for url in start_urls:
      yield scrapy.Request(url=url.Value,
        callback=self.parseList, errback=self.errorParseList,
        meta={'searchURLID': url.Id})

  def parseList(self, response):
    self.counter += 1
    parsed_uri = urlparse(response.url)
    self.URL = response.url
    marketplace = '{uri.netloc}'.format(uri=parsed_uri)

    department = response.xpath("//div[@id='departments']/ul/li[2]/span/a/span/text()").get()
    category = response.xpath("//div[@id='departments']/ul/li[3]/span/a/span/text()").get()
    subcategory = response.xpath("//div[@id='departments']/ul/li[4]/span/a/span/text()").get()
    if subcategory == None:
      subcategory = response.xpath("//div[@id='departments']/ul/li[4]/span/span/text()").get()

    subsubcategory = response.xpath("//div[@id='departments']/ul/li[5]/span/a/span/text()").get()
    if subsubcategory == None:
      subsubcategory = response.xpath("//div[@id='departments']/ul/li[5]/span/span/text()").get()

    subsubsubcategory = response.xpath("//div[@id='departments']/ul/li[6]/span/a/span/text()").get()

    subsubsubcategory = subsubsubcategory if subsubsubcategory != None else ''


    marketplace = Operations.GetOrCreateMarketplace(marketplace)
    department = Operations.GetOrCreateDepartment(department)
    category = Operations.GetOrCreateCategory(subcategory)
    subcategory = Operations.GetOrCreateCategory(subcategory)
    subsubcategory = Operations.GetOrCreateCategory(subsubcategory)
    subsubsubcategory = Operations.GetOrCreateCategory(subsubsubcategory)

    images = response.xpath("//div[@data-asin]/..//a/div/img")
    start_urls = [x.xpath("../../@href").extract_first() for x in images]

    for url in start_urls[0:self.pages]:

      yield response.follow(url=url,
        callback=self.parseBook, errback=self.errorParseBook,
        meta={'searchURLID': response.meta.get('searchURLID'),
        'marketplace': marketplace.Id, 'department': department.Id,
        'category': category.Id, 'subcategory': subcategory.Id,
        'subsubcategory': subsubcategory.Id,
        'subsubsubcategory': subsubsubcategory.Id })

    if self.counter < 10:
      next_page = response.xpath("//ul/li/a[contains(text(), 'Next')]/@href").extract_first()
      yield response.follow(next_page,
        callback=self.parseList, errback=self.errorParseList,
        meta={'searchURLID': response.meta.get('searchURLID')})

  def parseBook(self, response):
    title = response.xpath("//span[@id='productTitle']/text()"
      ).extract_first(
      ).replace('\n', '')
    URL = response.request.url
    author = response.xpath("//a[@data-asin]/text()").extract_first()
    asin = response.xpath("//b[contains(text(), 'ASIN:')]"
      ).xpath("../text()").extract_first().strip()
    language = response.xpath("//b[contains(text(), 'Language:')]"
      ).xpath("../text()").extract_first().strip()

    kindle_category_names = response.xpath("//li[@id='SalesRank']/ul/li/..//a/text()").extract()
    kindle_category_urls = response.xpath("//li[@id='SalesRank']/ul/li/..//a/@href").extract()

    paperback_url = response.xpath("//a/span[contains(text(), 'Paperback')]").xpath("../@href").extract_first()
    try:
      paperback_isbn_string = re.search(r'dp/(\d+)/ref', paperback_url).group(1)
      paperback_isbn = re.search(r'\d+', paperback_isbn_string).group()
    except Exception as e:
      paperback_isbn = ''

    book = Book()

    # Basic scraped features
    book.ASIN = asin
    book.Title = title
    book.URL = URL
    book.Author = author
    book.PaperbackURL = paperback_url
    book.PaperbackISBN = paperback_isbn

    # Inherited book features
    start = time()
    if len(kindle_category_names) > 0:
      book.eBookCategory_1 = Operations.GetOrCreateEBookCategory(kindle_category_names[0]).Id
    else:
      book.eBookCategory_1 = None

    if len(kindle_category_names) > 1:
      book.eBookCategory_2 = Operations.GetOrCreateEBookCategory(kindle_category_names[1]).Id

    else:
      book.eBookCategory_2 = None

    if len(kindle_category_names) > 2:
      book.eBookCategory_3 = Operations.GetOrCreateEBookCategory(kindle_category_names[2]).Id

    else:
      book.eBookCategory_3 = None

    book.LanguageID = Operations.GetOrCreateLanguage(language).Id
    self.sql_query_kindle_and_language += time() - start

    book.SearchURLID = response.meta.get('searchURLID')
    book.MarketplaceID = response.meta.get('marketplace')
    book.DepartmentID = response.meta.get('department')
    book.CategoryID = response.meta.get('category')
    book.SubCategoryID = response.meta.get('subcategory')
    book.SubSubCategoryID = response.meta.get('subsubcategory')
    book.SubSubSubCategoryID = response.meta.get('subsubsubcategory')

    start = time()
    Operations.SaveBook(book)
    self.sql_insert_time += time() - start


  def errorParseList(self, failiure):
    print('fail')

  def errorParseBook(self, failiure):
    print('fail')


  @classmethod
  def from_crawler(cls, crawler, *args, **kwargs):
    spider = super().from_crawler(crawler, *args, **kwargs)
    crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
    return spider

  def spider_closed(self, spider):
    print("SQL Insert book time: {}".format(self.sql_insert_time))
    print("SQL Kindle and Language query: {}".format(self.sql_query_kindle_and_language))

if __name__ == "__main__":
  pass
import os
import json
from pprint import pprint
from datetime import datetime

from sqlalchemy import ForeignKey, desc, create_engine, func, Column, BigInteger, Integer, Float, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from time import time

connectionString = "postgresql://dison:dison123@192.168.1.35:5433/dison"

engine = create_engine(connectionString, echo=False)

Base = declarative_base()

def read_file(filename):
  file = open(filename, "r")
  return file.readlines()

class SearchURL(Base):
  __tablename__ = 'search_url'

  Id = Column('id', Integer, primary_key=True)
  Value = Column('value', String)
  Advert = Column('advert', String)

  def __init__(self, value, advert):
    self.Value = value
    self.Advert = advert

class PageSearch(Base):
  __tablename__ = 'page_search'

  Id = Column('id', Integer, primary_key=True)
  Value = Column('value', String)

  def __init__(self, data):
    self.Id = data['id']
    self.Value = data['value']

class Marketplace(Base):
  __tablename__ = 'marketplace'

  Id = Column('id', Integer, primary_key=True)
  Value = Column('value', String)

class Department(Base):
  __tablename__ = 'department'

  Id = Column('id', Integer, primary_key=True)
  Value = Column('value', String)

class Category(Base):
  __tablename__ = 'category'

  Id = Column('id', Integer, primary_key=True)
  Value = Column('value', String)

class eBookCategory(Base):
  __tablename__ = 'ebookcategory'

  Id = Column('id', Integer, primary_key=True)
  Value = Column('value', String)
  URL = Column('url', String)

class Language(Base):
  __tablename__ = 'language'

  Id = Column('id', Integer, primary_key=True)
  Value = Column('value', String)


class Book(Base):
  __tablename__ = 'book'

  Id = Column('id', Integer, primary_key=True, autoincrement=True)
  ASIN = Column('isbn', String, primary_key=True)
  Title = Column('title', String)
  URL = Column('url', String)
  Author = Column('author', String)
  PaperbackURL = Column('paperback_url', String)
  PaperbackISBN = Column('paperback_isbn', String)

  # Foreign keys

  # This is inside book page
  eBookCategory_1 = Column('ebookcategory_1', Integer, ForeignKey('ebookcategory.id'))
  eBookCategory_2 = Column('ebookcategory_2', Integer, ForeignKey('ebookcategory.id'))
  eBookCategory_3 = Column('ebookcategory_3', Integer, ForeignKey('ebookcategory.id'))
  LanguageID = Column('language', Integer, ForeignKey('language.id'))

  # This is manually put into db
  SearchURLID = Column('search_url', Integer, ForeignKey('search_url.id'))

  # This is on list page
  MarketplaceID = Column('marketplace', Integer, ForeignKey('marketplace.id'), primary_key=True)
  DepartmentID = Column('department', Integer, ForeignKey('department.id'))
  CategoryID = Column('category', Integer, ForeignKey('category.id'))
  SubCategoryID = Column('subcategory', Integer, ForeignKey('category.id'), primary_key=True)
  SubSubCategoryID = Column('subsubcategory', Integer, ForeignKey('category.id'))
  SubSubSubCategoryID = Column('subsubsubcategory', Integer, ForeignKey('category.id'))


Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

class Operations:

  def UpdatePageSearch(data):
    page_search = session.query(PageSearch).filter_by(Id=data['id']).first()
    if page_search == None:
      session.add(PageSearch(data))

    else:
      page_search.Value = data['value']

    session.commit()

  def GetSites():
    return session.query(SearchURL).all()

  def QueryPageSearch():
    return session.query(PageSearch).all()

  def SaveURLSave(url):
    session.add(URLSave(url))
    session.commit()

  def GetSiteUpdatePageSearchs():
    return session.query(SearchURL).all()

  def GetOrCreateMarketplace(marketplace_name):

    marketplace = session.query(Marketplace
      ).filter_by(Value=marketplace_name).scalar()
    if marketplace != None:
      return marketplace

    else:
      marketplace = Marketplace()
      marketplace.Value = marketplace_name
      session.add(marketplace)
      session.commit()

    return marketplace

  def GetOrCreateDepartment(department_name):

    department = session.query(Department
      ).filter_by(Value=department_name).scalar()
    if department != None:
      return department

    else:
      department = Department()
      department.Value = department_name
      session.add(department)
      session.commit()

    return department

  def GetOrCreateCategory(category_name):

    category = session.query(Category
      ).filter_by(Value=category_name).scalar()
    if category != None:
      return category

    else:
      category = Category()
      category.Value = category_name
      session.add(category)
      session.commit()

    return category

  def GetOrCreateEBookCategory(category_name, category_url):

    category = session.query(eBookCategory
      ).filter_by(Value=category_name).scalar()
    if category != None:
      return category

    else:
      category = eBookCategory()
      category.Value = category_name
      category.URL = category_url
      session.add(category)
      session.commit()

    return category

  def GetOrCreateLanguage(language_name):

    language = session.query(Language
      ).filter_by(Value=language_name).scalar()
    if language != None:
      return language

    else:
      language = Language()
      language.Value = language_name
      session.add(language)
      session.commit()

    return language

  def SaveBasicBooks(books):
    for book in books:
      db_book = session.query(Book
      ).filter_by(ASIN=book.ASIN, MarketplaceID=book.MarketplaceID, SubCategoryID=book.SubCategoryID
      ).delete()

    session.bulk_save_objects(books)
    session.commit()

  def SaveBook(book):
    db_book = session.query(Book
    ).filter_by(ASIN=book.ASIN, MarketplaceID=book.MarketplaceID, SubCategoryID=book.SubCategoryID
    ).delete()
    session.commit()

    session.add(book)
    session.commit()

  def SaveSearchURL(data):
    if session.query(SearchURL.Id).filter_by(Id=data.Id).scalar() == None:
      session.add(SearchURL(data))
      session.commit()

  def init_database():
    searches = [x.rstrip() for x in read_file('searches.txt')]
    adverts = [x.rstrip() for x in read_file('adverts.txt')]

    search_urls = [SearchURL(search, advert) for search, advert in zip(searches, adverts)]
    session.bulk_save_objects(search_urls)
    session.commit()

  def generate_data_for_email():
    conn = psycopg2.connect(os.environ.get('DISON_DATABASE'))
    cursor = conn.cursor()
    sql_file = open('queries.sql', 'r')
    t_path_n_file = "data.csv"
    with open('data.csv', 'w') as f_output:
        cursor.copy_expert("""COPY (select * from excel) TO STDOUT WITH (FORMAT CSV)""", f_output)

  def QueryUnfetchedBooks(volume=500):
    return session.query(Book).filter_by(Title=None).limit(volume).all()

  def Commit():
    session.commit()

  def UpdateBook(save):
    book = session.query(Book).filter_by(Id=save['id']).first()
    book.Title = save['Title']
    book.Author = save['Author']
    book.LanguageID = save['LanguageID']
    book.eBookCategory_1 = save['eBookCategory_1']
    book.eBookCategory_2 = save['eBookCategory_2']
    book.eBookCategory_3 = save['eBookCategory_3']
    book.PaperbackURL = save['PaperbackURL']
    book.PaperbackISBN = save['PaperbackISBN']

    session.commit()

if __name__ == "__main__":
  print(session.query(Book).filter_by(Title=None).count())
import os
import json
from pprint import pprint
from datetime import datetime

from sqlalchemy import ForeignKey, desc, create_engine, func, Column, BigInteger, Integer, Float, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

if os.environ.get('DATABASE') is not None:
  connectionString = os.environ.get('DATABASE')

engine = create_engine(connectionString, echo=False)

Base = declarative_base()

class SearchURL(Base):
  __tablename__ = 'searchURL'

  Id = Column('id', Integer, primary_key=True)
  Value = Column('value', String)

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

class Language(Base):
  __tablename__ = 'language'

  Id = Column('id', Integer, primary_key=True)
  Value = Column('value', String)


class Book(Base):
  __tablename__ = 'book'

  ASIN = Column('isbn', String, primary_key=True)
  Title = Column('title', String)
  URL = Column('url', String)
  Author = Column('author', String)
  PaperbackURL = Column('paperbackURL', String)
  PaperbackISBN = Column('paperbackISBN', String)

  # Foreign keys

  # This is inside book page
  eBookCategory_1 = Column('ebookcategory_1', Integer, ForeignKey('ebookcategory.id'))
  eBookCategory_2 = Column('ebookcategory_2', Integer, ForeignKey('ebookcategory.id'))
  eBookCategory_3 = Column('ebookcategory_3', Integer, ForeignKey('ebookcategory.id'))
  LanguageID = Column('language', Integer, ForeignKey('language.id'))

  # This is manually put into db
  SearchURLID = Column('searchURL', Integer, ForeignKey('searchURL.id'))

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
  def GetSites():
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

  def GetOrCreateEBookCategory(category_name):

    category = session.query(eBookCategory
      ).filter_by(Value=category_name).scalar()
    if category != None:
      return category

    else:
      category = eBookCategory()
      category.Value = category_name
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

    session.add(book)
    session.commit()


if __name__ == "__main__":
  print(os.environ.get('DATABASE'))
  print(Operations.GetSites()[0].Value)

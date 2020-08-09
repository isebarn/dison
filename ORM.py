import os
import json

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
  __tablename__ = 'eBookCategory'

  Id = Column('id', Integer, primary_key=True)
  Value = Column('value', String)

class Language(Base):
  __tablename__ = 'language'

  Id = Column('id', Integer, primary_key=True)
  Value = Column('value', String)


class Book(Base):
  __tablename__ = 'ads'

  ASIN = Column('isbn', String, primary_key=True)
  Title = Column('title', String)
  URL = Column('url', String)
  Author = Column('author', String)
  PaperbackURL = Column('paperbackURL', String)
  PaperbackISBN = Column('paperbackISBN', BigInteger)

  SearchURLID = Column('searchURL', Integer, ForeignKey('searchURL.id'))
  MarketplaceID = Column('marketplace', Integer, ForeignKey('marketplace.id'))
  DepartmentID = Column('department', Integer, ForeignKey('department.id'))
  CategoryID = Column('category', Integer, ForeignKey('category.id'))
  SubCategoryID = Column('subcategory', Integer, ForeignKey('category.id'))
  SubSubCategoryID = Column('subsubcategory', Integer, ForeignKey('category.id'))
  SubSubSubCategoryID = Column('subsubsubcategory', Integer, ForeignKey('category.id'))
  LanguageID = Column('language', Integer, ForeignKey('language.id'))
  eBookCategory_1 = Column('ebookcategory_1', Integer, ForeignKey('eBookCategory.id'))
  eBookCategory_2 = Column('ebookcategory_2', Integer, ForeignKey('eBookCategory.id'))
  eBookCategory_3 = Column('ebookcategory_3', Integer, ForeignKey('eBookCategory.id'))


Base.metadata.create_all(engine)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


if __name__ == "__main__":
  print(os.environ.get('DATABASE'))

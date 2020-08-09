# Amazon book scraper

## Get the code from git
```
git clone https://github.com/isebarn/dison.git
or
git clone git@github.com:isebarn/dison.git
```

## Preparing the environment (Linux)
Make sure you have python3 and pip3 installed

I recommend using a virtual environment, but it is not necessary
```
virtualenv venv
source /venv/bin/activate
```
Install the packages
```
pip3 install -r requirements.txt
```

Set the environment variable that points to your database

```
export DATABASE=postgresql://USERNAME:PASSWORD@HOST:5432/DATABASE
# example
export DATABASE=postgresql://dison:dison123@localhost:5432/books
```

## Initializing the database

### Create tables
run
```
python ORM.py
```

That will create all tables

You must also run the following command

### Create a search page 
The crawler crawls all search pages in the table `searchURL`

To view this table run
```
psql -d DATABASE -U USER -h HOST -W 
```
and enter your password

You can view all tables by running
```
\dt
```

To view all search urls, run

```
select * from "searchURL";
>>> result
 id |  value                                                                                          
----+-------
```
To insert a search url like `https://www.amazon.com/s?i=digital-text&bbn=156431011&rh=n%3A133140011%2Cn%3A154606011%2Cn%3A156430011%2Cn%3A156431011%2Cn%3A11717359011%2Cp_n_feature_nine_browse-bin%3A3291437011&dc` run

```
insert into "searchURL"(value) values('https://www.amazon.com/s?i=digital-text&bbn=156431011&rh=n%3A133140011%2Cn%3A154606011%2Cn%3A156430011%2Cn%3A156431011%2Cn%3A11717359011%2Cp_n_feature_nine_browse-bin%3A3291437011&dc');
```

Now you can again run

```
select * from "searchURL";
>>> result
 id |                                                                                         value                                                                                          
----+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  1 | https://www.amazon.com/s?i=digital-text&bbn=156431011&rh=n%3A133140011%2Cn%3A154606011%2Cn%3A156430011%2Cn%3A156431011%2Cn%3A11717359011%2Cp_n_feature_nine_browse-bin%3A3291437011&dc
```
## Run the crawler
The crawler will iterate over every entry inside `searchURL`

You start the crawler by running
```
scrapy crawl root -a pages=N
fx
scrapy crawl root -a pages=1
```
Where `N` is the number of pages you want to crawl. If `N=1` it will crawl only the first page, which usually contains 16 books, so 16 books will be scraped and saved into the database. You can put any number you want. If you put 1000 and there are 252 pages, it wont fail.

You can also run
```
scrapy crawl root
```
Then the number of pages will revert to default = `5`

## View the data 
The most basic way of generating an excel file from the data is by:

 1. Edit the file `queries.sql`.
 2. The last line of the file reads `\copy (select * from excel) to '/home/david/data.csv' With CSV HEADER`
 3. Change `/home/david/data.csv` to `/some/path/data.csv` that is on your system
 4. run `psql -d DATABASE -f queries.sql` or `psql -d books -f queries.sql`

This will generate a excel file with all necessary fields!

drop view excel;
create view excel as (SELECT
  search_url.value as "search url",
  search_url.advert as "advert",
  category1.value as "category",
  category2.value as "subcategory",
  category3.value as "subsubcategory",
  category4.value as "subsubsubcategory",
  department.value as "department",
  ebookcategory1.value as "ebookcategory_1",
  concat(marketplace.value, ebookcategory1.url) as "ebookcategory_1_url",
  ebookcategory2.value as "ebookcategory_2",
  concat(marketplace.value, ebookcategory2.url) as "ebookcategory_2_url",
  ebookcategory3.value as "ebookcategory_3",
  concat(marketplace.value, ebookcategory3.url) as "ebookcategory_3_url",
  marketplace.value as "marketplace",
  language.value as "language",
  book.isbn,
  book.title,
  book.url,
  book.author,
  concat(marketplace.value, book.paperback_url) as "paperback_url",
  concat('"', book.paperback_isbn, '"')
from book
join category as category1 on category1.id = book.category
join category as category2 on category2.id = book.subcategory
join category as category3 on category3.id = book.subsubcategory
join category as category4 on category4.id = book.subsubsubcategory
join department on department.id = book.department
join ebookcategory as ebookcategory1 on ebookcategory1.id = book.ebookcategory_1
join ebookcategory as ebookcategory2 on ebookcategory2.id = book.ebookcategory_2
join ebookcategory as ebookcategory3 on ebookcategory3.id = book.ebookcategory_3
join marketplace on marketplace.id = book.marketplace
join language on language.id = book.language
join search_url on search_url.id = book.search_url);

\copy (select * from excel) to '/home/david/data.csv' With CSV HEADER
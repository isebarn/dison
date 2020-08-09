drop view excel;
create view excel as (SELECT
  searchurl.value as "search url",
  category1.value as "category",
  category2.value as "subcategory",
  category3.value as "subsubcategory",
  category4.value as "subsubsubcategory",
  department.value as "department",
  ebookcategory1.value as "ebookcategory_1",
  ebookcategory2.value as "ebookcategory_2",
  marketplace.value as "marketplace",
  language.value as "language",
  book.isbn,
  book.title,
  book.url,
  book.author,
  book."paperbackURL" as "paperback url",
  book."paperbackISBN" as "paperback isbn"
from book
join category as category1 on category1.id = book.category
join category as category2 on category2.id = book.subcategory
join category as category3 on category3.id = book.subsubcategory
join category as category4 on category4.id = book.subsubsubcategory
join department on department.id = book.department
join ebookcategory as ebookcategory1 on ebookcategory1.id = book.ebookcategory_1
join ebookcategory as ebookcategory2 on ebookcategory2.id = book.ebookcategory_2
join marketplace on marketplace.id = book.marketplace
join language on language.id = book.language
join "searchURL" as searchurl on searchurl.id = book."searchURL");

\copy (select * from excel) to '/home/david/data.csv' With CSV HEADER
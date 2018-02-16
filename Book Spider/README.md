# Book Spiders

## Step to use this scrapy structures:

- Open Terminal and run

```bash
​```
pip install scrapy
​```
```

- Clone this repo
- go to **example** folder
- go to **spiders** folder

```bash
​```
scrapy crawl books -o books.csv 
​```
```

- *scrapy crawl* means to begin crawl using scrapy
- *books* is a very important parameter for it is defined in **book_spider.py**

```python
​```
name = 'books' 
​```
```

- *-o* means to export the result in a file called **books.csv**
- Use the following commands to see the content in the csv file and it will skip the first line of the csv file

```bash
​```
sed -n '2,$p' books.csv | cat -n
​```
```

## The code in the *book_spider.py*

- *name* is the unique identifier of every spiders in one project, which is very important in a scrapy project. In

```bash
​```
scrapy crawl books -o books.csv
​```
```

command, *books* is the same as the name in the code.

- *start_url* is the begining url for a spider
- *parse* is the function to run for a spider
  - *css* or *xpath* interpreter
  - *yield* will commit the request to scrapy server.
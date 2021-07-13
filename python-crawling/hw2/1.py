from urllib.parse import urljoin

import requests
import bs4
import pymongo as pm
import dateparser
import locale
from dateutil.relativedelta import relativedelta


class MagnitParser:

    def __init__(self, start_url):
        self.start_url = start_url

    def _get(self, url: str) -> bs4.BeautifulSoup:
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        self.db = pm.MongoClient('mongodb://localhost:27017')['python-crawling']
        return soup

    def run(self):
        soup = self._get(self.start_url)
        for product in self.parse(soup):
            self.save(product)

    def parse(self, soup: bs4.BeautifulSoup):
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})
        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        for product in catalog.findChildren('a'):
            try:
                old_price_element = product.find("div", attrs={"class": "label__price label__price_old"})
                old_price = int(old_price_element.find('span', attrs={"class": "label__price-integer"}).text)
                old_price += float(old_price_element.find('span', attrs={"class": "label__price-decimal"}).text) / 100

                new_price_element = product.find("div", attrs={"class": "label__price label__price_new"})
                new_price = int(new_price_element.find('span', attrs={"class": "label__price-integer"}).text)
                new_price += float(new_price_element.find('span', attrs={"class": "label__price-decimal"}).text) / 100

                date = list(product.find("div", attrs={"class": "card-sale__date"}).find_all('p'))
                date_from = date[0].text
                date_to = date[1].text

                date_from_date = dateparser.parse(date_from[2:])
                date_to_date = dateparser.parse(date_to[3:])

                if date_to_date < date_from_date:
                    date_to_date = date_from_date + relativedelta(years=1)

                data = {
                    "url": urljoin(self.start_url, product.attrs.get('href')),
                    "image_url": urljoin(self.start_url, product.find("img").attrs.get('data-src')),
                    "promo_name": product.find('div', attrs={'class': 'card-sale__header'}).text,
                    "old_price": old_price,
                    "new_price": new_price,
                    "product_name": product.find("div", attrs={'class': 'card-sale__title'}).text,
                    "date_from": date_from_date,
                    "date_to": date_to_date
                }
                yield data
            except AttributeError:
                continue

    def save(self, data: dict):
        collection = self.db['magnit']
        collection.insert_one(data)
        pass


MagnitParser("https://magnit.ru/promo/?geo=moskva").run()

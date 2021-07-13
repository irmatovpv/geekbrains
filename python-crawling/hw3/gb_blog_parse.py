import requests
import bs4
from urllib.parse import urljoin
import dateparser
from data_base import Storage


class GbBlogParse:

    def __init__(self, start_url, storage):
        self.start_url = start_url
        self.page_done = set()
        self._storage = storage

    def __get(self, url: str) -> bs4.BeautifulSoup:
        response = requests.get(url)
        self.page_done.add(url)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        return soup

    def run(self, url=None):
        if not url:
            url = self.start_url
        if not url in self.page_done:
            soup = self.__get(url)
            posts, pagination = self.parse(soup)
            for post_url in posts:
                page_data = self.page_parse(self.__get(post_url), post_url)
                self.save(page_data)
            for url in pagination:
                self.run(url)

    def parse(self, soup: bs4.BeautifulSoup):
        posts = set(
            [urljoin(self.start_url, url.get('href')) for url in soup.find_all('a', attrs={'class': 'post-item__title'})
             if url.get('href')])

        ul_pag = soup.find('ul', attrs={'class': 'gb__pagination'})
        return posts, \
               set([urljoin(self.start_url, url.get('href')) for url in ul_pag.find_all('a') if url.get('href')])

    def save(self, data: dict):
        self._storage.store(data)

    def page_parse(self, soup, url) -> dict:
        data = {
            'url': url,
            'first_img': soup.find("div", attrs={'class': 'blogpost'}).find('img').get('src'),
            'date_published': dateparser.parse(soup.find("time", attrs={'itemprop': 'datePublished'}).get('datetime')),
            'author': {
                'name': soup.find("div", attrs={'itemprop': 'author'}).text,
                'url': urljoin(self.start_url, soup.find("div", attrs={'itemprop': 'author'}).parent.get('href'))
            },
            'title': soup.find('h1').text,
            'comments': self.load_comments(soup.find('comments').get('commentable-id')),
            'tags': []
        }

        for tag in soup.find_all('a', attrs={'class': 'small'}):
            t_url = urljoin(self.start_url, tag.get('href'))
            tag_name = tag.text
            comment_data = {
                'url': t_url,
                'name': tag_name
            }
            data['tags'].append(comment_data)
        return data

    def load_comments(self, id):
        response = requests.get(
            "https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id={}&order=desc".format(id)
        )
        return self.parse_comments(response.json())

    def parse_comments(self, comments):
        result = []
        for comment in comments:
            result.append(
                {
                    'author': {
                        'url': comment['comment']['user']['url'],
                        'name': comment['comment']['user']['full_name']
                    },
                    'body': comment['comment']['body'],
                    'id': comment['comment']['id'],
                    'parent_id': comment['comment']['parent_id'],
                }
            )
            result += self.parse_comments(comment['comment']['children'])
        return result


parser = GbBlogParse('https://geekbrains.ru/posts/', Storage())
parser.run()

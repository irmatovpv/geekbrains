import scrapy
import json
import datetime as dt

from gb_parse.items import InstagramTag, InstagramPost


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    api_url = '/graphql/query/'
    start_urls = ['https://www.instagram.com/']
    query_hash = {
        'posts': '56a7068fea504063273cc2120ffd54f3',
        'tag_posts': '9b498c08113f1e09617a1703c22b2f32'
    }

    def __init__(self, start_hash_tags: list, login, password,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_hash_tags = start_hash_tags
        self.login = login
        self.password = password
        self.start_hash_tags = [f"/explore/tags/{tag}/" for tag in start_hash_tags]

    def get_js_data(self, response):
        json_text = response.xpath('//script[contains(text(),"window._shared" )]/text()').get()
        return json.loads(json_text.replace('window._sharedData = ', '')[:-1])

    def parse(self, response):
        try:
            js_data = self.get_js_data(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password':self.password
                },
                headers={
                    'X-CSRFToken': js_data['config']['csrf_token']
                }
            )
        except Exception as e:
            data = response.json()
            if data['authenticated']:
                for tag in self.start_hash_tags:
                    yield response.follow(tag, callback=self.tag_page_parse)

    def tag_page_parse(self, response):
        js_data = self.get_js_data(response)
        tag = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']

        yield InstagramTag(
            date_parse=dt.datetime.utcnow(),
            data = {
                'id': tag['id'],
                'name': tag['name'],
                'profile_pic_url': tag['profile_pic_url']
            }
        )
        yield from self.get_tag_posts(tag, response)

    def tag_api_parse(self, response):
        yield from self.get_tag_posts(response.json()['data']['hashtag'], response)

    def get_tag_posts(self, tag, response):
        if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {
                'tag_name': tag['name'],
                'first': 100,
                'after': tag['edge_hashtag_to_media']['page_info']['end_cursor']
            }
            url = f'{self.api_url}?query_hash={self.query_hash["tag_posts"]}&variables={json.dumps(variables)}'
            yield response.follow(
                url,
                callback=self.tag_api_parse,
            )
        yield from self.get_post_item(tag['edge_hashtag_to_media']['edges'])

    @staticmethod
    def get_post_item(edges):
        for node in edges:
            yield InstagramPost(
                date_parse=dt.datetime.utcnow(),
                data=node['node']
            )


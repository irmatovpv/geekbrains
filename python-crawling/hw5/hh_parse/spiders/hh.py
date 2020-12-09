import scrapy

from hh_parse.loaders import VacancyLoader, AuthorLoader


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']
    xpath_query ={
        'vacancy': '//div[contains(@class, "vacancy-serp-item")]//a[contains(@class, "HH-VacancySidebarTrigger-Link")]/@href',
        'list_pagination': '//div[contains(@class, "bloko-gap")]//a[contains(@class, "HH-Pager-Control")]/@href',
        'company_link': '//a[contains(@data-qa, "vacancy-company-name")]/@href',
        'author_vacancy_page': '//div[contains(@class, "employer-sidebar-content")]//a[contains(@data-qa, "employer-vacancies-link")]/@href'
    }

    vacancy_template = {
        'title': '//div[contains(@class, "vacancy-title")]//h1/text()',
        'salary': '//template[contains(@id, "HH-Lux-InitialState")]/text()',
        'description': '//template[contains(@id, "HH-Lux-InitialState")]/text()',
        'key_skill': '//template[contains(@id, "HH-Lux-InitialState")]/text()',
        'author_url': '//a[contains(@data-qa, "vacancy-company-name")]/@href',
    }

    author_template = {
        'name': '//div[contains(@class, "employer-sidebar-header")]//span[contains(@class, "company-header-title-name")]/text()',
        'site_url': '//div[contains(@class, "employer-sidebar-content")]//a[contains(@data-qa, "sidebar-company-site")]/@href',
        'field_of_activity': '//div[contains(@class, "employer-sidebar-content")]//div[contains(@class, "employer-sidebar-block")]//div[contains(@class, "employer-sidebar-block__header") and contains(text(), "Сферы деятельности")]/../p/text()',
        'author_description': '//div[contains(@class, "company-description")]',
    }

    def vacancy_page_parse(self, response, **kwargs):
        for link in response.xpath(self.xpath_query['company_link']):
            yield response.follow(link, callback=self.parse_author)

        loader = VacancyLoader(response=response)
        loader.add_value('url', response.url)
        for name, selector in self.vacancy_template.items():
            loader.add_xpath(name, selector)
        yield loader.load_item()

    def parse_author(self, response, **kwargs):
        for link in response.xpath(self.xpath_query['author_vacancy_page']):
            yield response.follow(link, callback=self.parse)

        loader = AuthorLoader(response=response)
        loader.add_value('url', response.url)
        for name, selector in self.author_template.items():
            loader.add_xpath(name, selector)

        yield loader.load_item()

    def parse(self, response, **kwargs):
        for link in response.xpath(self.xpath_query['vacancy']):
            yield response.follow(link, callback=self.vacancy_page_parse)

        for page in response.xpath(self.xpath_query['list_pagination']):
            yield response.follow(page, callback=self.parse)

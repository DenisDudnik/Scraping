import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
import json

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['www.superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&geo[t][0]=4']

    def parse(self, response: HtmlResponse):
        links_json = response.xpath("//script[@type='application/ld+json']/text()").getall()
        links_dict = json.loads(links_json[0])
        links_source = links_dict.get('itemListElement')
        links = [item.get('url') for item in links_source]
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in links:
            yield response.follow(link, callback=self.parse_vacancy)

    def parse_vacancy(self, response: HtmlResponse):
        vac_name = response.xpath("//h1/text()").get()
        vac_salary = response.xpath("//h1/../span/span[1]/span/text()").getall()
        vac_url = response.url
        yield JobparserItem(name=vac_name, salary=vac_salary, url=vac_url)

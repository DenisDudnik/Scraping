import scrapy
from scrapy.http import HtmlResponse
from leroy.items import LeroyItem
from scrapy.loader import ItemLoader


class LeroyruSpider(scrapy.Spider):
    name = 'leroyru'
    allowed_domains = ['leroymerlin.ru']

    # start_urls = ['http://leroymerlin.ru/']

    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']

    def parse(self, response: HtmlResponse):
        '''Получаем ссылки на объекты и ссылку на след. страницу'''
        page_links = response.xpath("//a[@data-qa-pagination-item='right']")  # next page
        for page in page_links:
            yield response.follow(page, callback=self.parse)

        ads_links = response.xpath("//div[@data-qa-product]/a")  # путь до блока в котором есть нужный href
        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyItem(), response=response)  # Создаем отдельный объект для работы с item
        # (здесь инициализируются все поля item'a и их обработчики)
        loader.add_xpath('name', "//h1/text()")  # Наполняем item данными (также сразу запускаются предобработчики)
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('currency', "//span[@slot='currency']/text()")
        loader.add_xpath('unit', "//span[@slot='unit']/text()")
        loader.add_xpath('specification_term', "//dt[@class='def-list__term']/text()")
        loader.add_xpath('specification_definition', "//dd[@class='def-list__definition']/text()")
        loader.add_xpath('photos', "//source[@media=' only screen and (min-width: 1024px)']/@srcset")
        loader.add_value('url', response.url)
        yield loader.load_item()  # Отправляем в пайплайн (также здесь запускаются постобработчики)

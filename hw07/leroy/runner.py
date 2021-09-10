from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroy.spiders.leroyru import LeroyruSpider
from leroy import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroyruSpider, query='газонокосилка')
    process.start()

import scrapy

class FranceCultureSpider(scrapy.Spider):
    name = 'france_culture'
    start_urls = ['https://www.franceculture.fr/emissions']

    def parse(self, response):
        for link in response.css('div.link-podcast').xpath('a[@class="podcast" and contains(text(),"RSS")]'):
            rss = link.xpath('@href').extract_first()
            if rss:
                yield {'rss': rss}

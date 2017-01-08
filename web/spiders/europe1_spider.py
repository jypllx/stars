import scrapy

class FranceInterSpider(scrapy.Spider):
    name = 'europe1'
    start_urls = ['https://www.europe1.fr/podcasts']

    def parse(self, response):
        for art in response.css('div.myPodcast'):
            rss = art.css('span.link._NOL::text').extract_first()
            if rss:
                yield {'rss': rss}

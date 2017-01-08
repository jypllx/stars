import scrapy

class FranceInterSpider(scrapy.Spider):
  name = 'franceinter'
  start_urls = ['https://www.franceinter.fr/emissions']

  def parse(self, response):
    for art in response.css('article'):
        rss = art.css('div.podcast-container.rss > a::attr(href)').extract_first()
        if rss:
            yield {'rss': rss}

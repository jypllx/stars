import scrapy

class FranceInterSpider(scrapy.Spider):
  name = 'franceinter'
  BASE_URL='https://www.franceinter.fr'
  start_urls = [BASE_URL+'/emissions']

  def parse(self, response):
    for art in response.css('article a'):
        itemprop=art.css('a::attr(itemprop)').extract_first()
        if itemprop=='name':
            link=self.BASE_URL+art.css('a::attr(href)').extract_first()
            yield scrapy.Request(link, callback=self.parse_page)

  def parse_page(self, response):
        rss = response.css('a.rss::attr(href)').extract_first()
        if rss:
            yield {'rss': rss}

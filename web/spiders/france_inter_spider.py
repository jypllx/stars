import scrapy

class FranceInterSpider(scrapy.Spider):
  name = 'France Inter'
  start_urls = ['https://www.franceinter.fr/emissions']

  def parse(self, response):
    for art in response.css('article'):
      yield {'title': art.css('div header > a::text').extract_first().strip(),
             'rss': art.css('div.podcast-container.rss > a::attr(href)').extract_first()}

      #next_page = response.css('div.prev-post > a ::attr(href)').extract_first()
      #if next_page:
      #  yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

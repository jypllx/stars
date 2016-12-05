import scrapy

class RmcSpider(scrapy.Spider):
  name = 'rmc'
  start_urls = ['http://rmc.bfmtv.com/mediaplayer/podcast/']

  def parse(self, response):
    for page in response.css('li.bloc div.art-body a.color-txt-0::attr(href)').extract():
        print(page)
        yield scrapy.Request(page, callback=self.parse_page)


      #next_page = response.css('div.prev-post > a ::attr(href)').extract_first()
      #if next_page:
      #  yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

  def parse_page(self, response):
    yield {'title': response.css('h1.title-medium::text').extract_first(),
           'rss'  : response.xpath('//div[@id="emissionLink"]/a').xpath('@href').extract_first()}
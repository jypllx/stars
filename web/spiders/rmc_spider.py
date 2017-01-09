import scrapy

class RmcSpider(scrapy.Spider):
  name = 'rmc'
  start_urls = ['http://rmc.bfmtv.com/mediaplayer/podcast/']

  def parse(self, response):
    for page in response.css('li.bloc div.art-body a.color-txt-0::attr(href)').extract():
        yield scrapy.Request(page, callback=self.parse_page)

  def parse_page(self, response):
    rss = response.xpath('//div[@id="emissionLink"]/a').xpath('@href').extract_first()
    if rss:
      yield {'rss' : rss}
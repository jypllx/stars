import scrapy

class BfmSpider(scrapy.Spider):
  name = 'bfm'
  start_urls = ['http://bfmbusiness.bfmtv.com/mediaplayer/podcast/']

  def parse(self, response):
    for page in response.css('figure.figure > a::attr(href)').extract():
        yield scrapy.Request(page, callback=self.parse_page)

  def parse_page(self, response):
    rss = response.xpath('//div[@id="emissionLink"]/a[contains(text(), "RSS")]/@href').extract_first()
    if rss:
        yield {'rss' : rss}
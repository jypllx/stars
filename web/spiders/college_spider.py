import scrapy

class CollegeSpider(scrapy.Spider):
  name = 'college-de-france'
  start_urls = ['https://www.college-de-france.fr/components/search-audiovideo.jsp?type=all&lang=FR&siteid=1156951719600']
  BASE_URL = 'https://www.college-de-france.fr'

  def parse(self, response):
    result = []
    first=True
    for link in response.css('li > a'):
        text = link.css('a::text').extract_first().strip()
        link = self.BASE_URL+link.css('a::attr(href)').extract_first()
        
        if text.strip() == 'continuer':
            yield scrapy.Request(link, callback=self.parse)
        else:
            yield scrapy.Request(link, callback=self.parse_link)


  def parse_link(self, response):
    title = response.css("#title::text").extract_first().strip()
    audio = response.css("ul.picto > li.audio > a::attr(href)").extract_first()
    image = response.css("div.img-container > img::attr(src)").extract_first()
    d = response.css("span.date > span.day::text").extract_first()
    h = response.css("span.date > span.from::text").extract_first()

    if audio:
        yield {'title_' : title, 'audio_url_':audio, 'image':image, 'day':d, 'hour':h}
    else:
        yield None
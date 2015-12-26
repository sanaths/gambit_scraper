from meta import *
import scrapy


class GambitSpider(scrapy.Spider):
    name = "event_spider"
    allowed_domains = ["bestofneworleans.com"]
    start_urls = [
        "http://www.bestofneworleans.com/gambit/EventSearch?eventSection=1222876&narrowByDate=Next%207%20Days&neighborhoodGroup=1287922",
    ]

    def parse(self, response):
        
        basic_list =  [ 
                        GambitScraperItem(
                                            link=event_listing.xpath('.//h3/a/@href').extract(),
                                            time=event_listing.xpath('.//div[@class="listing"]/text()').extract(),
                                            location=(
                                                    event_listing.xpath('.//div[@class="listingLocation"]/a/text()').extract(),
                                                    event_listing.xpath('.//div[@class="listingLocation"]/text()').extract()
                                                    ),
                                            description=event_listing.xpath('.//p/text()').extract(),
                                            title=event_listing.xpath('.//h3/a/text()').extract()
                                            )
                        
                        for event_listing in response.css('div.EventListing')
                        ]
       


        filename = response.url.split("/")[-2]
        with open(filename, 'wb') as f:
            f.write(response.body)
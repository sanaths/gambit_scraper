from meta import *
import scrapy
from emailer import *
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor


class GambitSpider(CrawlSpider):

    name = "event_spider"
    allowed_domains = ["bestofneworleans.com"]
    start_urls = [
        "http://www.bestofneworleans.com/gambit/EventSearch?eventSection=1222876&narrowByDate=Next%207%20Days&neighborhoodGroup=1287922",
    ]

    rules = (
            Rule(
                    SgmlLinkExtractor(allow=(), restrict_xpaths=('//a[@class="next"]',)),
                    callback="parse_items", follow=True
                ),
            )

    def parse_items(self, response):
            basic_list = []

            for event_listing in response.css('div.EventListing'):

                basic_item = GambitScraperItem(
                        link=event_listing.xpath('.//h3/a/@href').extract(),
                        time=event_listing.xpath('.//div[@class="listing"]/text()').extract(),
                        location=[
                                    event_listing.xpath('.//div[@class="listingLocation"]/a/text()').extract(),
                                    event_listing.xpath('.//div[@class="listingLocation"]/text()').extract()
                                  ],
                        description=event_listing.xpath('.//p/text()').extract(),
                        title=event_listing.xpath('.//h3/a/text()').extract())

                cleaned_item = self.clean_up_item_lists(basic_item)
                final_item = self.remove_empty_list_values_from_item(cleaned_item)

                basic_list.append(final_item)

            print(basic_list)

            # emailer = Emailer()
            # message = emailer.create_message(sender="sanath001@gmail.com",
            #                                  to="vfanola@gmail.com",
            #                                  subject="This Week in NOLA:",
            #                                  message_text=basic_list)
            #
            # draft = emailer.create_draft("me", message)

            return basic_list

    @classmethod
    def clean_up_item_lists(cls, item):
        item['link'][:] = [link.strip(' \r\n') for link in item['link']]
        item['time'][:] = [link.strip(' \r\n') for link in item['time']]
        item['location'][:] = [link.strip(' \r\n') for link in item['location'][0] if link != 'map']
        item['description'][:] = [link.strip(' \r\n') for link in item['description']]
        item['title'][:] = [link.strip(' \r\n') for link in item['title']]

        return item

    @classmethod
    def remove_empty_list_values_from_item(cls, item):

        link = ' '.join(item['link'])
        time = ' '.join(item['time'])
        location= ' '.join(item['location'])
        description = ' '.join(item['description'])
        title = ' '.join(item['title'])

        item = GambitScraperItem(link=link,
                          time=time,
                          location=location,
                          description=description,
                          title=title)

        return item







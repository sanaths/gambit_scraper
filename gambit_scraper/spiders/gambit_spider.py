from meta import *
import scrapy
from emailer import *
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from datetime import datetime
from scrapy.linkextractors import LinkExtractor, _re_type
from scrapy.selector import HtmlXPathSelector



class GambitSpider(CrawlSpider):

    name = "event_spider"
    allowed_domains = ["bestofneworleans.com"]
    start_urls = [
        "http://www.bestofneworleans.com/gambit/EventSearch?eventSection=1222876&narrowByDate=Next%207%20Days&neighborhoodGroup=1287922",
    ]

    def parse(self, response):
        url= "http://www.bestofneworleans.com/gambit/EventSearch?eventSection=1222876&amp;narrowByDate=Next%207%20Days&amp;neighborhoodGroup=1287922&page="
        page_number = int(response.xpath('.//a[@class="next"]/@title').extract()[0][-1])
        url_list = [url + str(number) for number in range(1, page_number+1)]

        for url in url_list:
            yield Request(url, callback=self.parse_items)

    def parse_items(self, response):
            basic_list = []

            # put everything into a basic list
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

            #break up list into multidimensional array with items ordered by date
            org_list = self.get_list_organized_by_day_of_week(basic_list)               

            self.write_list_to_todays_file(basic_list)

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

    @classmethod
    def write_list_to_todays_file(cls, basic_list):
        with open(datetime.strftime(datetime.now(), '%Y-%m-%d') + 'gambit.txt','a') as f:
            for item in basic_list:
                f.write(
                    "<p>" +\
                        "<a href='" + 
                            item['link'].encode('utf-8') + "'>" +\
                            item['title'].encode('utf-8') +\
                        "</a>" +\
                        " @ " + item['location'].encode('utf-8') + ", " +\
                        item['time'].encode('utf-8') +\
                    "</p>" +\
                    "<p>" +\
                         "\n" + item['description'].encode('utf-8') + "\n\n" +\
                    "</p>" 
                )

    @classmethod
    def get_list_organized_by_day_of_week(cls, list):
        pass






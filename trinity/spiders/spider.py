import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import TrinityItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://www.trinitybank.cz/aktuality/?pc-297-paginator-page={}&do=pc-297-paginator-setPage'

class TrinitySpider(scrapy.Spider):
	name = 'trinity'
	page = 0
	start_urls = [base.format(page)]

	def parse(self, response):
		post_links = response.xpath('//div[@class="o-grid2__column col-md-12 col-lg-8"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if not len(post_links) < 6:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[@class="o-news-detail__date"]/text()').get()
		date = ''.join(date.split())
		title = response.xpath('//h1//text()').get()
		content = response.xpath('//div[@class="a-max-width-md mx-auto mt-2"]//text()[not (ancestor::h1 or ancestor::a)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=TrinityItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()

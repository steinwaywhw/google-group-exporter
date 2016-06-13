import scrapy
from pygments import highlight
from pygments.lexers.html import HtmlLexer
from pygments.formatters import TerminalFormatter

class ThreadItem(scrapy.Item):
	subject = scrapy.Field()
	href = scrapy.Field()

class MessageItem(scrapy.Item):
	subject = scrapy.Field()
	author = scrapy.Field()
	lastPostDate = scrapy.Field()
	snippet = scrapy.Field()
	threadUrl = scrapy.Field()
	threadSubject = scrapy.Field()

class GoogleGroupSpider(scrapy.Spider):
	name = "google-group-spider"
	start_urls = ["https://groups.google.com/forum/#!forum/ats-lang-users"]
	
	def parse(self, response):

		# total = response.xpath("//i[contains(text(),'Showing')]").extract_first()
		# total = total.split()[3]
		# total = int(total)

		# print(highlight(response.body, HtmlLexer(), TerminalFormatter()))
		
		for index, thread in enumerate(response.xpath("//body/table/tr")):
			item = ThreadItem()
			item["href"] = thread.xpath(".//a/@href").extract_first().replace("/d/topic", "/forum/#!topic")
			item["subject"] = thread.xpath(".//a/text()").extract_first()
			# yield item 

			request = scrapy.Request(item["href"], self.parse_thread)
			request.meta['threadUrl'] = item["href"]
			request.meta['threadSubject'] = item["subject"]
			yield request


		load_more = response.xpath("//a[contains(text(),'More topics')]/@href").extract_first()
		if load_more:
			url = load_more.replace("?_escaped_fragment_=", "#!")
			url = url.replace("%5B", "[")
			url = url.replace("%5D", "]")
			yield scrapy.Request(url, self.parse)			
	
	def parse_thread(self, response):

		for index, message in enumerate(response.xpath("//body/table/tr")):
			item = MessageItem()
			item["threadUrl"] = response.meta["threadUrl"]
			item["threadSubject"] = response.meta["threadSubject"]
			item["subject"] = message.xpath("./td[@class='subject']/a/text()").extract_first()
			item["author"] = message.xpath("./td[@class='author']/span/text()").extract_first()
			item["lastPostDate"] = message.xpath("./td[@class='lastPostDate']/text()").extract_first()
			item["snippet"] = message.xpath("./td[@class='snippet']/div/div/div[@dir]").extract_first()

			yield item

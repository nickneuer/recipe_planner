#!/usr/bin/env python

import scrapy
from bs4 import BeautifulSoup


class SmittenKitchenScraper(scrapy.Spider):

	name = "recipes"

	start_urls = [
	    "https://smittenkitchen.com/2009/07/plum-kuchen/"
	]

	def parse(self, response):
		ingredients = response.css('div.jetpack-recipe-ingredients')
		if ingredients:
			ingredient_list = ingredients.css(
				"li.jetpack-recipe-ingredient::text").extract()
		else:
			paragraphs = response.css('div.entry-content p')
			for p in paragraphs:
				br_count = len(p.css('br').extract())
				if br_count > 1:
					ingredient_list = p.css('p::text').extract()
		try:
			yield {
			    'url': response.url,
			    'title': response.css('title::text').extract(),
			    'ingredients': ingredient_list
			}
		except:
			yield None

		next_page = response.css('div.nav-next a::attr(href)').extract_first()
		if next_page is not None:
			yield response.follow(next_page, callback=self.parse)


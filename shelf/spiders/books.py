import re

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    def parse(self, response: Response, **kwargs) -> dict:
        for book_card in response.css("article.product_pod"):
            yield response.follow(
                book_card.css("a::attr(href)").get(),
                callback=self.parse_book_detail
            )

        if next_href := response.css("li.next a::attr(href)").get():
            yield response.follow(next_href, callback=self.parse)

    @staticmethod
    def parse_book_detail(response: Response) -> dict:
        product_detail = dict(
            zip(
                response.css("table tr th::text").getall(),
                response.css("table tr td::text").getall()
            )
        )
        rating = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }
        yield {
            "title": response.css(".product_main h1::text").get(),
            "category": product_detail.get("Product Type"),
            "upc": product_detail.get("UPC"),
            "price": response.css(
                ".product_main p.price_color::text"
            ).get()[1:],
            "rating": rating.get(
                response.css("p.star-rating::attr(class)").get().split()[-1]
            ),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "amount_in_stock": int(re.sub(
                "\D", "",  # NOQA W605
                product_detail.get("Availability")
            )),
        }

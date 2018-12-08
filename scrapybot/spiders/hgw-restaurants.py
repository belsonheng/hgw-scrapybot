import geocoder, json, scrapy, pandas
from scrapybot.items import Restaurant

def get_start_urls():
    df = pandas.read_csv('data/town.csv')
    return [f"https://www.hungrygowhere.com/search-results/?search_location={town}" for town in df.pln_area_n.tolist()]

class HungryGoWhereRestaurants(scrapy.Spider):
    name = "hgw-restaurants"
    allowed_domains = ['www.hungrygowhere.com']
    start_urls = get_start_urls()

    def parse(self, response):
        if not '&p=' in response.url:
            result = response.css('#page_result')[0]
            next_urls = [
                response.urljoin(restaurant.css('.title-wrap a::attr(href)').extract_first())
                for _, restaurant in enumerate(result.css('.restaurant_item'))
            ]
            yield scrapy.Request(
                response.url + '&p=2',
                meta={
                    'town': response.css('input.term-search-location::attr(value)').extract_first(),
                    'next_urls': next_urls
                },
                callback=self.parse
            )
        else:
            # subsequent response type should be in json format
            try:
                json_response = json.loads(response.body_as_unicode())
                more = not json_response['endPage']

                from scrapy import Selector
                selector = Selector(text=json_response['resultHtml'], type='html')

                for _, restaurant in enumerate(selector.css('article.restaurant_item')):
                    response.meta['next_urls'].append(
                        response.urljoin(restaurant.css('.title-wrap a::attr(href)').extract_first())
                    )
            except:
                more = False

            if (more):
                next_url = '='.join(response.url.split('=')[:-1]) + '=' + str(int(response.url.split('=')[-1])+1)
                yield scrapy.Request(
                    next_url,
                    meta=response.meta,
                    callback=self.parse
                )
                
            for url in response.meta['next_urls']:
                yield scrapy.Request(
                    url,
                    meta={'town': response.meta['town']},
                    callback=self.parse_restaurant_detail
                )

    def parse_restaurant_detail(self, response):
        summary = response.css('.module-ibl-summary')
        postal = summary.css('span[itemprop="postalCode"]::text').extract_first(default='')
        coordinates = geocoder.arcgis(f"singapore {postal}")
        for cuisine in summary.css('.cuisine a::text').extract():
            yield Restaurant(
                town=response.meta['town'],
                url=response.url,
                business_id=response.css('.review_item::attr(data-ibl-id)').extract_first(default=''),
                name=summary.css('h1.hneue-bold-ll::text').extract_first(default=''),
                address=''.join(summary.css('.address *::text').extract()),
                postal=postal,
                latitude=coordinates.lat,
                longitude=coordinates.lng,
                type=summary.css('.category-name::text').extract_first(default=''),
                price_range=summary.css('.price-range::text').extract_first(default=''),
                cuisine=cuisine
            )

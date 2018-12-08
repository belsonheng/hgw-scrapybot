import scrapy, pandas
from scrapybot.items import Review
from datetime import datetime
from dateutil import relativedelta

def get_start_urls():
    df = pandas.read_csv('data/hgw-restaurants.csv')
    return [f"{restaurant_url}review/" for restaurant_url in df[df.business_id.notnull()].url.drop_duplicates().tolist()]

def get_date(s):
    if 'months ago' in s.lower():
        return (datetime.now() - relativedelta.relativedelta(months=int(s.split()[0]))).date().strftime("%d %b %Y")
    elif 'last month' in s.lower():
        return (datetime.now() - relativedelta.relativedelta(months=1)).date().strftime("%d %b %Y")
    elif 'this month' in s.lower():
        return (datetime.now() - relativedelta.relativedelta(weeks=2)).date().strftime("%d %b %Y")
    elif 'last week' in s.lower():
        return (datetime.now() - relativedelta.relativedelta(weeks=1)).date().strftime("%d %b %Y")
    elif 'this week' in s.lower():
        return (datetime.now() - relativedelta.relativedelta(days=2)).date().strftime("%d %b %Y")
    elif 'yesterday' in s.lower():
        return (datetime.now() - relativedelta.relativedelta(days=1)).date().strftime("%d %b %Y")
    elif 'today' in s.lower():
        return datetime.now().date().strftime("%d %b %Y")
    else:
        return s

class HungryGoWhereReviews(scrapy.Spider):
    name = "hgw-reviews"
    allowed_domains = ['www.hungrygowhere.com']
    start_urls = get_start_urls()

    def parse(self, response):
        more = not response.css(".icon-empty-reviews")
        business_id = response.css(".review_item::attr(data-ibl-id)").extract_first()

        if '=singapore' in response.url:
            # if the actual url gets redirected, we have to get url back from referer
            more = True
            next_url = response.urljoin(str(response.request.headers.get('referer_url')))
            print(next_url)
            print(response.url)
            raise Exception('here')
        elif '&page=' in response.url:
            # increment the page counter
            next_url = '='.join(response.url.split('=')[:-1]) + '=' + str(int(response.url.split('=')[-1])+1)
        else:
            next_url = f"{response.url}?start_page=0&sort=helpful_votes&business_id={business_id}&page=1"

        review_urls = [
            response.urljoin(review.css('h4 > a::attr(href)').extract_first())
            for _, review in enumerate(response.css('.review_item'))
        ]

        if (more):
            yield scrapy.Request(
                next_url,
                meta={'business_id': business_id, 'review_urls': review_urls},
                callback=self.parse
            )

        if 'business_id' not in response.meta:
            response.meta['business_id'] = business_id
        if 'review_urls' not in response.meta:
            response.meta['review_urls'] = review_urls
        else:
            review_urls = list(set(review_urls + response.meta['review_urls']))

        for url in review_urls:
            yield scrapy.Request(
                url,
                meta=response.meta,
                callback=self.parse_review_detail
            )

    def parse_review_detail(self, response):
        user_details = response.css('.favourite-review .user-detail::text').extract_first(default='')
        yield Review(
            business_id=response.meta['business_id'],
            review_user=response.css('.favourite-review .user-detail > span::text').extract_first(default=''),
            review_date=get_date([part.strip() for part in user_details.split(u'\u2022')][1]),
            review_title=response.css('.favourite-review h4 > a::text').extract_first(default=''),
            review_text=' '.join(''.join(response.css('.favourite-review .desc *::text').extract()).split()).replace('"', ''),
            review_url=response.url
        )

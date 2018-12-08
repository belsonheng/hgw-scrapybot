# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv

class ScrapybotPipeline(object):
    def open_spider(self, spider):
        if spider.name == 'hgw-restaurants':
            self.restaurant_file = csv.writer(open(f"data/{spider.name}.csv", 'w', newline='', encoding='utf8'))
            self.restaurant_file.writerow([
                'town',
                'url',
                'business_id',
                'name',
                'address',
                'postal',
                'latitude',
                'longitude',
                'type',
                'price_range',
                'cuisine'
            ])
        if spider.name == 'hgw-reviews':
            self.review_file = csv.writer(open(f"data/{spider.name}.csv", 'w', newline='', encoding='utf8'))
            self.review_file.writerow([
                'business_id',
                'review_user',
                'review_date',
                'review_title',
                'review_text',
                'review_url'
            ])

    def process_item(self, item, spider):
        if spider.name == 'hgw-restaurants':
            self.restaurant_file.writerow([
                item['town'],
                item['url'],
                item['business_id'],
                item['name'],
                item['address'].replace('\xa0', ' '),
                item['postal'].strip(),
                item['latitude'],
                item['longitude'],
                item['type'],
                item['price_range'],
                item['cuisine'],
            ])
        if spider.name == 'hgw-reviews':
            self.review_file.writerow([
                item['business_id'],
                item['review_user'],
                item['review_date'],
                item['review_title'],
                item['review_text'],
                item['review_url']
            ])
        return item

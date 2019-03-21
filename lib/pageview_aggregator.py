import re
from pathlib import Path
from collections import defaultdict
from pymongo import MongoClient
import pickle
import os

class PageviewAggregator():
    '''
        Aggregates monthly totals of pageviews into one total per page, then
        inserts that total into each document with a matching title in the DB.
        Call either aggregate or load_totals, then insert.
    '''

    TOTALS_PATH = os.path.join(
        os.path.dirname(__file__),
        '../data/pageviews'
    )

    def aggregate(self, disaggregate_filepath):
        with open(disaggregate_filepath) as disaggregate_file:
            self.pageview_totals = defaultdict(int)
            for line in disaggregate_file:
                parsed = self.parse(line)
                self.pageview_totals[parsed['title']] += parsed['monthly_count']
        Path(self.TOTALS_PATH).touch()
        with open(self.TOTALS_PATH, 'w') as totals_file:
            for name, total in self.pageview_totals.items():
                totals_file.write(f'{name} {total}\n')
        self.cross_page_total = sum(self.pageview_totals.values())
        

    def load_totals(self):
        self.pageview_totals = defaultdict(int) # just keeping type consistent
        with open(self.TOTALS_PATH, 'r') as totals_file:
            for line in totals_file:
                match = re.match('([^ ]+) ([^ ]+)', line)
                name, views = match[1], int(match[2])
                self.pageview_totals[name] = views        

    def insert(
        self,
        db_name='who',
        collection_name='bios',
        views_field_name='views',
        verbose='True'
    ):
        bios = MongoClient()[db_name][collection_name]
        for update_count, bio in enumerate(bios.find({}, {'name': 1})):
            if verbose and update_count % 1000 == 0:
                print(f'pageview total insertation count: {update_count}')
            bios.update_one(
                {'_id': bio['_id']},
                {'$set': {
                    views_field_name: self.pageview_totals[
                        self.url_format(bio['name'])
                    ]
                }}
            )

    def parse(self, line):
        match = re.match('[\w\.]+ ([^ ]+) (\d+)', line)
        return {
            'title': match[1],
            'monthly_count': int(match[2])
        }

    def url_format(self, page_title):
        return re.sub(' ', '_', page_title)

    def normalize(self, view_count):
        return (view_count / self.cross_page_total)

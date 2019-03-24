import re
import unicodedata
from pymongo import MongoClient

DB_NAME = 'who'

class FieldMapper():
    '''
        Parent class for querying some field from MongoDB, performing an
        arbitrary series of transformations, and reinserting the result as a new
        field
    '''
    def map_field(
        self,
        collection,
        source_field_name,
        new_field_name,
        transformations,
        verbose=True
    ):
        db = MongoClient()[DB_NAME]
        current_stream = self.id_text_tuples(db[collection], source_field_name)
        for transformation in transformations:
            current_stream = self.apply_preserving_id(transformation, current_stream)
        for i, (doc_id, new_field_val) in enumerate(current_stream):
            if verbose and i % 1000 == 0:
                print(f'insertation count: {i}')
            db[collection].update_one(
                {'_id': doc_id},
                {'$set': {
                    new_field_name: new_field_val
                }}
            )

    # methods supporting map

    def apply_preserving_id(self, funk, transform_target):
        return (
            (
                name,
                funk(intro_para)
            )
            for name, intro_para
            in transform_target
        )

    def id_text_tuples(self, collection, text_field):
        return (
            (doc['_id'], doc[text_field])
            for doc
            in collection.find({}, {text_field: 1})
        )

    # methods common to children

    def strip_parentheticals(self, text):
        return re.sub('\([^\)]*\)', '', text)

    def normalize_encoding(self, text):
        return (
            unicodedata
                .normalize('NFD', text)
                .encode('ascii', 'ignore')
                .decode('ascii', 'ignore')
        )

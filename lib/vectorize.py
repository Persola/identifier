import re
from collections import Counter
import unicodedata
import os
from itertools import islice

import numpy as np
import spacy
from scipy.spatial.distance import cosine
from pymongo import MongoClient

from biography_streamer import BiographyStreamer
from introductory_paragraph_streamer import IntroductoryParagraphStreamer

DB_NAME = 'who'
# path to a copy of pages-articles-multistream.xml
#   contains all current Wikipedia articles
#   unzipped
SOURCE_PATH = 'data/enwiki-20190101-pages-articles-multistream.xml'
SPACY_MODEL = 'en_vectors_web_lg'

# next line only needs to run once, but rerunning is < 1s delay
# assumes python command is 'python3'
os.system(f'python3 -m spacy download {SPACY_MODEL}')
print('loading spaCy model...')
nlp = spacy.load(SPACY_MODEL) # TO DO: turn off parts of pipeline
print('done loading spaCy model')

# def hashibalize(vector):
#     return str(vector)

# def query(query_str, limit=None):
#     return ranked_names(nlp(query_str).vector, limit)

# def ranked_names(query_vector, limit=None):
#     distance_to_vector = {
#         cosine(
#             query_vector,
#             hashable_vector_to_vector[hashable_vector]
#         ): hashable_vector_to_vector[hashable_vector]
#         for hashable_vector, name
#         in hashable_vector_to_name.items()
#     }
#     distances = sorted(distance_to_vector.keys())
#     return [
#         hashable_vector_to_name[
#             hashibalize(distance_to_vector[distance])
#         ]
#         for distance
#         in distances[:limit]
#     ]

def chain(*funktions):
    def chained(arg):
        for funktion in funktions:
            arg = funktion(arg)
        return arg
    return chained

def apply_preserving_id(funk, transform_target):
    return (
        (
            name,
            funk(intro_para)
        )
        for name, intro_para
        in transform_target
    )

def normalize_encoding(text):
    return (
        unicodedata
            .normalize('NFD', text)
            .encode('ascii', 'ignore')
            .decode('ascii', 'ignore')
    )

def strip_parentheticals(text):
    return re.sub('\([^\)]*\)', '', text)

def mongo_compatible(vector):
    return [
        float(numpy_float)
        for numpy_float
        in vector
    ]

def vectorize(collection, field_name='vector'):
    db = MongoClient()[DB_NAME]
    encoding_normalized = apply_preserving_id(
        normalize_encoding,
        (
            (bio['_id'], bio['bio'])
            for bio
            in db[collection].find({}, {'bio': 1})
        )
    )
    no_parens = apply_preserving_id(strip_parentheticals, encoding_normalized)
    spacy_docs = apply_preserving_id(nlp, no_parens)
    vectors = apply_preserving_id(lambda doc : doc.vector, spacy_docs)
    # print(type(list(vectors[0])))
    for doc_id, vector in vectors:
        db[collection].update_one(
            {'_id': doc_id},
            {'$set': {
                field_name: mongo_compatible(vector)
            }}
        )

    # steps for identification (to extract)

    # hashable_vector_to_name = {}
    # hashable_vector_to_vector = {}
    # for i, (name, vector) in enumerate(vectors):
    #     print(i) if i % 10 == 0 else None
    #     hashable_vector_to_name[hashibalize(vector)] = name
    #     hashable_vector_to_vector[hashibalize(vector)] = vector

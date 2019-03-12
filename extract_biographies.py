import re
from collections import Counter
import unicodedata
import os

import numpy as np
import spacy
from scipy.spatial.distance import cosine

from biography_streamer import BiographyStreamer
from introductory_paragraph_streamer import IntroductoryParagraphStreamer

from time import sleep
import pdb

# path to a copy of pages-articles-multistream.xml
#   contains all current Wikipedia articles
#   unzipped
SOURCE_PATH = 'data/enwiki-20190101-pages-articles-multistream.xml'

def normalize_encoding(text):
    return (
        unicodedata
            .normalize('NFD', text)
            .encode('ascii', 'ignore')
            .decode('ascii', 'ignore')
    )

def strip_parentheticals(text):
    return re.sub('\([^\)]*\)', '', text)

# def strip_lifespan_parenthetical(intro_para):
#     match = re.match('[\w\-\.,\"\'\s]+\([^\)]*\) (was|is)', intro_para)
#     if match:
#         None
#         # print(match)
#     else:
#         print(f'NONE: {intro_para[:99]}')

SPACY_MODEL = 'en_vectors_web_lg'
# next line only needs to run once, but rerunning is < 1s delay
# os.system(f'python -m spacy download {SPACY_MODEL}')
print('loading spaCy model...')
nlp = spacy.load(SPACY_MODEL)
print('done loading spaCy model')

def chain(*funktions):
    def chained(arg):
        for funktion in funktions:
            arg = funktion(arg)
        return arg
    return chained

def apply_preserving_names(funk, transform_target):
    return (
        (
            name,
            funk(intro_para)
        )
        for name, intro_para
        in transform_target
    )

def hashibalize(vector):
    return str(vector)

def query(query_str, limit=None):
    return ranked_names(nlp(query_str).vector, limit)

def ranked_names(query_vector, limit=None):
    distance_to_vector = {
        cosine(
            query_vector,
            hashable_vector_to_vector[hashable_vector]
        ): hashable_vector_to_vector[hashable_vector]
        for hashable_vector, name
        in hashable_vector_to_name.items()
    }
    distances = sorted(distance_to_vector.keys())
    return [
        hashable_vector_to_name[
            hashibalize(distance_to_vector[distance])
        ]
        for distance
        in distances[:limit]
    ]

with open(SOURCE_PATH, 'rb') as file:
    bio_streamer = BiographyStreamer(limit=10).stream(file)
    intro_paras = IntroductoryParagraphStreamer().stream(bio_streamer)
    encoding_normalized = apply_preserving_names(normalize_encoding, intro_paras)
    no_parens = apply_preserving_names(strip_parentheticals, encoding_normalized)
    vectors = apply_preserving_names(lambda x : nlp(x).vector, no_parens)

    hashable_vector_to_name = {}
    hashable_vector_to_vector = {}    
    for i, (name, vector) in enumerate(vectors):
        print(i) if i % 10 == 0 else None
        hashable_vector_to_name[hashibalize(vector)] = name
        hashable_vector_to_vector[hashibalize(vector)] = vector

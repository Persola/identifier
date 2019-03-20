import re
import os

import spacy
from scipy.spatial.distance import cosine
from pymongo import MongoClient

DB_NAME = 'who'
SPACY_MODEL = 'en_vectors_web_lg'

class Searcher():
    def __init__(
        self,
        nlp=None,
        collection_name='bios',
        vector_field_name='vector',
        verbose=True
    ):
        if not nlp:
            print('downloading spaCy model...') if verbose else None
            os.system(f'python3 -m spacy download {SPACY_MODEL}')
            print('...done') if verbose else None
            print('loading spaCy model...') if verbose else None
            nlp = spacy.load(SPACY_MODEL) # TO DO: turn off parts of pipeline
            print('...done') if verbose else None
        self.nlp = nlp
        self.hashable_vector_to_name = {}
        self.hashable_vector_to_vector = {}
        if verbose:
            print('generating vector similarity maps...')
        for doc in MongoClient()[DB_NAME][collection_name].find({}, {'name': 1, vector_field_name: 1}):
            hashible_vector = self.hashibalize(doc[vector_field_name])
            self.hashable_vector_to_name[hashible_vector] = doc['name']
            self.hashable_vector_to_vector[hashible_vector] = doc[vector_field_name]

    def query(self, query_str, limit=None):
        return self.ranked_names(self.nlp(query_str).vector, limit)

    def hashibalize(self, vector):
        return str(vector)

    def ranked_names(self, query_vector, limit=None):
        distance_to_vector = {
            cosine(
                query_vector,
                self.hashable_vector_to_vector[hashable_vector]
            ): self.hashable_vector_to_vector[hashable_vector]
            for hashable_vector, name
            in self.hashable_vector_to_name.items()
        }
        distances = sorted(distance_to_vector.keys())
        return [
            self.hashable_vector_to_name[
                self.hashibalize(distance_to_vector[distance])
            ]
            for distance
            in distances[:limit]
        ]

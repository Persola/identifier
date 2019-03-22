import re
from math import log

import spacy
from scipy.spatial.distance import cosine
from pymongo import MongoClient

from load_spacy_model import load_spacy_model

DB_NAME = 'who'
SPACY_MODEL = 'en_vectors_web_lg'

class Searcher():
    DEFAULT_RESULT_LIMIT = 8

    def __init__(
        self,
        nlp=None,
        collection_name='bios',
        vector_field_name='vector',
        verbose=True
    ):
        self.nlp = (nlp or load_spacy_model())
        self.bios = MongoClient()[DB_NAME][collection_name]
        self.vector_field_name = vector_field_name

    def query(self, query_str, limit=DEFAULT_RESULT_LIMIT):
        '''
            Given a query as a string, returns a ranked list of the most
            relevant biographies.
        '''
        return self._closest_bios(self.nlp(query_str).vector, limit)

    def _closest_bios(self, query_vector, limit):
        matches = []
        candidates = self.bios.find({}, {
            'name': 1,
            'views': 1,
            'first_sentence': 1,
            self.vector_field_name: 1
        })
        for candidate in candidates:
            candidate_rank = self._rank(query_vector, candidate)
            if len(matches) < limit:
                self._sorted_insert(matches, candidate_rank, limit, grow=True)
            elif candidate_rank['rank'] > matches[-1]['rank']:
                self._sorted_insert(matches, candidate_rank, limit)
        return matches

    def _rank(self, query_vector, candidate):
        cosine_similarity = 1 - cosine(query_vector, candidate[self.vector_field_name])
        prominence = candidate['views']**(1/500)
        return {
            'name': candidate['name'],
            'cosine_distance': cosine_similarity,
            'views': candidate['views'],
            'prominence': prominence,
            'rank': cosine_similarity * prominence,
            'first_sentence': candidate['first_sentence']
        }

    def _sorted_insert(self, matches, candidate_rank, limit, grow=False):
        matches.insert(
            self._insert_index(matches, candidate_rank, limit),
            candidate_rank
        )
        if not grow:
            matches.pop()

    def _insert_index(self, matches, candidate_rank, limit):
        if len(matches) == 0:
            return 0
        for match_index, match in enumerate(matches):
            if candidate_rank['rank'] > match['rank']:
                return match_index
        if len(matches) < limit:
            return len(matches)
        raise ValueError('Match candidate does not fit within match list')

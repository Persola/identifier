import re

import numpy as np
from pymongo import MongoClient
from sklearn.neighbors import KDTree

from load_spacy_model import load_spacy_model

DB_NAME = 'who'
SPACY_MODEL = 'en_vectors_web_lg'

class Searcher():
    DEFAULT_RESULT_LIMIT = 8

    def __init__(
        self,
        nlp=None,
        collection_name='bios',
        vector_field_name='normalized_vector',
        verbose=True
    ):
        self.nlp = (nlp or load_spacy_model())
        self.bios = MongoClient()[DB_NAME][collection_name]
        self.vector_field_name = vector_field_name
        self._build_tree(verbose)

    def _build_tree(self, verbose):
        bio_count = self.bios.count_documents({})
        dimension_count = len(next(self.bios.find({}))[self.vector_field_name])
        all_vectors = np.zeros((bio_count, dimension_count))
        self.np_index_to_mongo_id = {}
        for ind, bio in enumerate(self.bios.find({})):
            self.np_index_to_mongo_id[ind] = bio['_id']
            all_vectors[ind] = bio[self.vector_field_name]
        if verbose:
            print('building KDTree...')
        self.tree = KDTree(all_vectors, leaf_size=2)              
        if verbose:
            print('...done')

    def query(self, query_str, limit=DEFAULT_RESULT_LIMIT):
        '''
            Given a query as a string, returns a ranked list of the most
            relevant biographies.
        '''
        normalized_query = self._normalize(self.nlp(query_str).vector).reshape(1, -1)
        _, nearest_indices = self.tree.query(normalized_query, k=limit)
        return [self._bio_for_ind(ind) for ind in nearest_indices[0]]

    def _normalize(self, vector):
        length = np.linalg.norm(vector)
        return np.array(vector) / length
        
    def _bio_for_ind(self, ind):
        return next(
            self.bios.find({
                '_id': self.np_index_to_mongo_id[ind]
            }, {
                'name': 1,
                'views': 1,
                'first_sentence': 1
            })
        )

import re

import pickle
import numpy as np
from pymongo import MongoClient
from sklearn.neighbors import KDTree
import os

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
        load_tree=False,
        verbose=True
    ):
        self.collection_name = collection_name
        self.vector_field_name = vector_field_name
        self.bios = MongoClient()[DB_NAME][collection_name]
        self.nlp = (nlp or load_spacy_model())
        if load_tree:
            self.load_tree(verbose)
        else:
            self._build_tree(verbose)
            self.save_tree(verbose)

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

    def load_tree(self, verbose):
        if verbose:
            print('loading tree...')
        with open(self._tree_path(), 'rb') as tree_file:
            self.np_index_to_mongo_id, self.tree = pickle.load(tree_file)
        if verbose:
            print('...done')

    def save_tree(self, verbose):
        if verbose:
            print('saving tree to disk...')
        with open(self._tree_path(), 'wb') as tree_file:
            pickle.dump(
                (self.np_index_to_mongo_id, self.tree),
                tree_file,
                protocol=4
            )
        if verbose:
            print('...done')
            
    def _tree_path(self):
        return os.path.join(
            __file__,
            f'kd_trees/{self.collection_name}-{self.vector_field_name}'
        )

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

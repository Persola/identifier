import os

import spacy

from field_mapper import FieldMapper
from load_spacy_model import load_spacy_model

SPACY_MODEL = 'en_vectors_web_lg'

class Vectorizer(FieldMapper):
    '''Adds vector field to collection'''

    def __init__(self, nlp=None, verbose=True):
        self.nlp = (nlp or load_spacy_model())

    def vectorize_text(
        self,
        collection_name,
        text_field_name='bios',
        vector_field_name='vector'
    ):
        self.map_field(
            collection_name,
            text_field_name,
            vector_field_name,
            [
                self.normalize_encoding,
                self.strip_parentheticals,
                self.nlp,
                lambda doc : doc.vector,
                self.mongo_compatible
            ]
        )

    def mongo_compatible(self, vector):
        return [
            float(numpy_float)
            for numpy_float
            in vector
        ]

import os

import spacy

from field_mapper import FieldMapper

SPACY_MODEL = 'en_vectors_web_lg'

class Vectorizer(FieldMapper):
    '''Adds vector field to collection'''

    def __init__(self, nlp=None, verbose=True):
        if not nlp:
            print('downloading spaCy model...') if verbose else None
            os.system(f'python3 -m spacy download {SPACY_MODEL}')
            print('...done') if verbose else None
            print('loading spaCy model...') if verbose else None
            nlp = spacy.load(SPACY_MODEL) # TO DO: turn off parts of pipeline
            print('...done') if verbose else None
        self.nlp = nlp

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

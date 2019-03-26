import sys
import os
import re

sys.path.append(
    os.path.join(os.path.dirname(__file__), '..')
)

from field_mapper import FieldMapper
from load_spacy_model import load_spacy_model

class IntroCleaner(FieldMapper):
    def __init__(
        self,
        nlp=None,
        collection_name='bios',
        source_field_name='normalized_vector',
        verbose=True
    ):
        self.collection_name = collection_name
        self.source_field_name = source_field_name
        self.nlp = (nlp or load_spacy_model())

    def clean(
        self,
        new_field_name='clean_intro',
        verbose=True
    ):
        self.map_field(
            self.collection_name,
            self.source_field_name,
            new_field_name,
            [
                self.clean_intro
            ],
            verbose
        )

    def clean_intro(self, intro_para):
        doc = self.nlp(intro_para)
        return ' '.join([
            str(token)
            for token
            in doc
            if not token.is_stop
        ])
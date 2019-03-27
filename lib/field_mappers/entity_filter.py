import sys
import os
import re

sys.path.append(
    os.path.join(os.path.dirname(__file__), '..')
)

from field_mapper import FieldMapper
from load_spacy_model import load_spacy_model

class EntityFilter(FieldMapper):
    def __init__(
        self,
        nlp=None,
        collection_name='bios',
        source_field_name='bio',
        verbose=True
    ):
        self.collection_name = collection_name
        self.source_field_name = source_field_name
        self.nlp = (nlp or load_spacy_model('en_core_web_lg'))

    def filter(
        self,
        new_field_name='entities',
        verbose=True
    ):
        self.map_field(
            self.collection_name,
            self.source_field_name,
            new_field_name,
            [
                self.extract_entities
            ],
            verbose
        )

    def extract_entities(self, text):
        return ' '.join([
            str(ent)
            for ent
            in self.nlp(text).ents
            if not re.match('\d\d', str(ent))
        ])

import re

from field_mapper import FieldMapper

class FirstSentenceExtractor(FieldMapper):
    '''
        Given the introductory paragraph of a biography, extracts and stores the
        first sentence
    '''

    CHAR_LENGTH_GUESS = 150

    def extract(self, collection_name, new_field_name='first_sentence'):
        self.map_field(
            collection_name,
            'bio',
            new_field_name,
            [
                self.first_sentence,
                self.strip_parentheticals,
                self.normalize_encoding
            ]
        )

    def first_sentence(self, text):
        first_verb_index = self.get_first_verb_index(text)
        from_first_verb = text[first_verb_index:]
        period_after_first_verb_match = re.search('\.\s', from_first_verb)
        if not first_verb_index or not period_after_first_verb_match:
            return text[:self.CHAR_LENGTH_GUESS]
        end_of_first_sentence_index = (
            first_verb_index +
            period_after_first_verb_match.start(0)
        )
        return text[:(end_of_first_sentence_index + 1)]

    def get_first_verb_index(self, text):
        is_index = self.first_index(text, ' is ')
        was_index = self.first_index(text, ' was ')
        if is_index and was_index:
            return min(is_index, was_index)
        return (is_index or was_index)

    def first_index(self, text, substring):
        return text.index(substring) if substring in text else None

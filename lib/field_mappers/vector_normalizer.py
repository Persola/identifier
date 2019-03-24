import numpy as np
import pdb
from field_mapper import FieldMapper

class VectorNormalizer(FieldMapper):
    '''
        Maps vector field to normalized vector field
        (making each a unit vector)
    '''

    def normalize(
        self,
        collection_name,
        vector_field_name='vector',
        normalized_field_name='normalized_vector',
        verbose=True
    ):
        self.map_field(
            collection_name,
            vector_field_name,
            normalized_field_name,
            [self._normalize],
            verbose
        )

    def _normalize(self, vector):
        length = np.linalg.norm(vector)
        return list(np.array(vector) / length)

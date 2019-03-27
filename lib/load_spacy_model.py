import os
import spacy

def load_spacy_model(model_name='en_vectors_web_lg', download=True, verbose=True):
    if download:
        print('downloading spaCy model...') if verbose else None
        # only needs to happen once per model:
        os.system(f'python3 -m spacy download {model_name}')
        print('...done') if verbose else None
    print('loading spaCy model...') if verbose else None
    nlp = spacy.load(model_name) # should disable things if not vector version
    print('...done') if verbose else None
    return nlp

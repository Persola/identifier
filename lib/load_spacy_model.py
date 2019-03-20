import spacy

SPACY_MODEL = 'en_vectors_web_lg'

def load_spacy_model(verbose=True):
    print('downloading spaCy model...') if verbose else None
    # only needs to happen once:
    os.system(f'python3 -m spacy download {SPACY_MODEL}')
    print('...done') if verbose else None
    print('loading spaCy model...') if verbose else None
    nlp = spacy.load(SPACY_MODEL) # should disable things if not vector version
    print('...done') if verbose else None
    return nlp

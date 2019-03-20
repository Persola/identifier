from itertools import islice

from pymongo import MongoClient

from biography_streamer import BiographyStreamer
from introductory_paragraph_streamer import IntroductoryParagraphStreamer

DB_NAME = 'who'
COLLECTION_NAME = 'bios'
# path to a copy of pages-articles-multistream.xml
#   contains all current Wikipedia articles
#   unzipped
SOURCE_PATH = 'data/enwiki-20190101-pages-articles-multistream.xml'
BATCH_SIZE = 998

def extract_biographies(collection_name='bios', limit=None, verbose=True):
    def batch(iterator, batch_size):
        batch_iter = iter(iterator)
        while(True):
            try:
                next(iter(batch_iter))
                yield islice(batch_iter, batch_size)
            except StopIteration:
                return

    with open(SOURCE_PATH, 'rb') as file:
        bio_streamer = BiographyStreamer(limit=limit).stream(file)
        intro_paras = IntroductoryParagraphStreamer().stream(bio_streamer)
        collection = MongoClient()[DB_NAME][COLLECTION_NAME]
        for each_batch in batch(intro_paras, BATCH_SIZE):
            print(f'inserting batch (max {BATCH_SIZE})...') if verbose else None
            collection.insert_many(
                [
                    {
                        'name': name,
                        'bio': bio
                    }
                    for name, bio
                    in each_batch
                ]
            )

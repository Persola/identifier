import re
from collections import Counter
import unicodedata
import os
from itertools import islice

import numpy as np
import spacy
from scipy.spatial.distance import cosine
from pymongo import MongoClient

from biography_streamer import BiographyStreamer
from introductory_paragraph_streamer import IntroductoryParagraphStreamer

# path to a copy of pages-articles-multistream.xml
#   contains all current Wikipedia articles
#   unzipped
SOURCE_PATH = 'data/enwiki-20190101-pages-articles-multistream.xml'

def batch(iterator, batch_size):
    batch_iter = iter(iterator)
    while(True):
        try:
            next(iter(batch_iter))
            yield islice(batch_iter, batch_size)
        except StopIteration:
            return

with open(SOURCE_PATH, 'rb') as file:
    bio_streamer = BiographyStreamer(limit=None).stream(file)
    intro_paras = IntroductoryParagraphStreamer().stream(bio_streamer)
    client = MongoClient()
    for batch in batch(intro_paras, 996):
        client.who.bios.insert_many(
            [
                {
                    'name': name,
                    'bio': bio
                }
                for name, bio
                in batch
            ]
        )

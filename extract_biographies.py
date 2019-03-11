import re

from biography_streamer import BiographyStreamer
from introductory_paragraph_streamer import IntroductoryParagraphStreamer

# path to a copy of pages-articles-multistream.xml
#   contains all current Wikipedia articles
#   unzipped
SOURCE_PATH = 'data/enwiki-20190101-pages-articles-multistream.xml'

def strip_parentheticals(text):
    return re.sub('\([^\)]*\)', '', text)

with open(SOURCE_PATH, 'rb') as file:
    bio_streamer = BiographyStreamer(file).stream(limit=10_000)
    intro_para_streamer = IntroductoryParagraphStreamer(bio_streamer)
    for intro_para in intro_para_streamer.stream():
        no_parentheticals = strip_parentheticals(intro_para)
        print(no_parentheticals)
        print('\n' * 4)

import re
from lxml import etree

class BiographyStreamer():
    '''
        Streams the texts of biographical Wikipedia articles.
        Initialize with an open file of dumped Wikipedia content, which should
        be named something like 'enwiki-20190101-pages-articles-multistream.xml'.
        English version available here:
        https://meta.wikimedia.org/wiki/Data_dump_torrents#English_Wikipedia
        Then call the 'stream' method for a stream of the biographies from the
        file (truncate the stream with 'limit').
    '''

    WIKIMEDIA_NAMESPACES = (
        'Media',
        'Special',
        '(Main)',
        'Talk',
        'User',
        'User talk',
        'Project',
        'Project talk',
        'File',
        'File talk',
        'MediaWiki',
        'MediaWiki talk',
        'Template',
        'Template talk',
        'Help',
        'Help talk',
        'Category',
        'Category talk'
    )
    NAMESPACE_PAGE_TITLE = f"^({'|'.join(WIKIMEDIA_NAMESPACES)}):"
    # re matchers for things that appear in Wikitext
    BIRTH_OR_DEATH_CATEGORY_TAG = r'\[\[Category:\s*\d+[\w-]* (?:\w+ )?(?:births|deaths)'
    PERSON_INFOBOX = r'\{\{Infobox person'
    LIST_TITLE = r'^List of'

    def __init__(self, limit=None):
        self.limit = limit

    def stream(self, file, limit=None):
        self.limit = (self.limit or limit)
        bio_count = 0
        for _, el in etree.iterparse(file):
            if self.is_article(el):
                revision_el = self.first_child_of_tag(el, 'revision')
                text_el = self.first_child_of_tag(revision_el, 'text')
                title_el = self.first_child_of_tag(el, 'title')
                if self.is_biography(title_el.text, text_el.text):
                    if self.limit and bio_count > self.limit:
                        return
                    bio_count += 1
                    title_el = self.first_child_of_tag(el, 'title')
                    yield (title_el.text, text_el.text)
                    # below: clean up is necessary to keep memory usage constant
                    # see https://www.ibm.com/developerworks/xml/library/x-hiperfparse/
                    el.clear()
                    while el.getprevious() is not None:
                        del el.getparent()[0]
        return

    def is_article(self, el):
        '''
            Takes an XML element from the Wikipedia source file and tests
            whether it is an article
        '''
        if self.strip_tag(el.tag) != 'page':
            return False
        if 'redirect' in self.child_tags(el):
            return False
        title_el = self.first_child_of_tag(el, 'title')
        if re.match(self.NAMESPACE_PAGE_TITLE, title_el.text):
            return False
        return True

    def strip_tag(self, whole_tag):
        '''
            Strips off the URL to the schema definition for the MediaWiki export
            format, leaving a simple name (e.g. 'title')
        '''
        return re.findall('\}(\w+)$', whole_tag)[0]

    def child_tags(self, parent):
        '''Returns tags of children of an XML element'''
        return [self.strip_tag(child.tag) for child in parent]

    def first_child_of_tag(self, parent, tag):
        '''Returns the first child of an XML element that has a given tag'''
        first_matching_child_index = self.child_tags(parent).index(tag)
        return parent[first_matching_child_index]

    def is_biography(self, title, text):
        '''
            Takes an article as a string and identifies whether it is a
            biography. This probably has good precision but lackluster recall.
        '''
        return (
            self.any_line_matches(text, self.BIRTH_OR_DEATH_CATEGORY_TAG) or
            self.any_line_matches(text, self.PERSON_INFOBOX)
        ) and (
            not re.match(title, self.LIST_TITLE)
        )

    def any_line_matches(self, text, uncompiled_pattern):
        '''Takes an article as a string'''
        return any(
            re.match(uncompiled_pattern, line)
            for line
            in text.split('\n')
        )

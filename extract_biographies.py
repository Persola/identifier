from functools import reduce
from itertools import islice
import re
from time import sleep
import xml.etree.ElementTree as etree
import pdb

# import wikitextparser
import mwparserfromhell

PARSER_TYPES = {
    'text': mwparserfromhell.nodes.text.Text,
    'header': mwparserfromhell.nodes.heading.Heading,
    'template': mwparserfromhell.nodes.template.Template,
    'tag': mwparserfromhell.nodes.tag.Tag,
    'wikilink': mwparserfromhell.nodes.wikilink.Wikilink
}

# path to a copy of pages-articles-multistream.xml
#   contains all current Wikipedia articles
#   unzipped
SOURCE_PATH = 'data/enwiki-20190101-pages-articles-multistream.xml'
# base of the XML types that appear in the .xml above
EL_TYPE_BASE = '{http://www.mediawiki.org/xml/export-0.10/}'
# re matchers for things that appear in Wikitext
BIRTH_OR_DEATH_CATEGORY_TAG = r'\[\[Category:\s*\d+(?:[\w-]+)? (?:\w+ )?(?:births|deaths)'
PERSON_INFOBOX = r'\{\{Infobox person'
CATEGORY_TAG_WITH_PEOPLE = r'\[\[Category:.*[Pp]eople[^s]'
MAGIC_WORD = '\_\_[A-Z]+\_\_'
# [[Category:Year of birth missing (living people)]]

def strip_tag(whole_tag):
    return re.findall('\}(\w+)$', whole_tag)[0]

def child_tags(parent):
    return [strip_tag(child.tag) for child in parent]

def find_child_of_tag(parent, tag):
    first_matching_child_index = child_tags(parent).index(tag)
    return parent[first_matching_child_index]

def el_is_of_tag(el, tag):
    return el.tag == f'{EL_TYPE_BASE}{tag}'

def is_entry(el):
    if strip_tag(el.tag) != 'page':
        return False
    if 'redirect' in child_tags(el):
        return False
    return True

# def chain(funktions):
#     def chained(argument):
#         current_data = argument
#         for funktion in funktions:
#             current_data = funktion(current_data)
#     return chained

# def descend(ancestor, ordered_descendant_tags):
#     current_el = ancestor
#     for tag in ordered_descendant_tags:
#         current_el = find_child_of_tag(current_el, tag)
#     return current_el

def lines_matching(text, uncompiled_pattern):
    return [
        line
        for line
        in text.split('\n')
        if re.match(uncompiled_pattern, line)
    ]

def any_line_matches(text, uncompiled_pattern):
    return any(
        re.match(uncompiled_pattern, line)
        for line
        in text.split('\n')
    )

def is_biography(text):
    return (
        any_line_matches(text, BIRTH_OR_DEATH_CATEGORY_TAG) or
        # any_line_matches(text, CATEGORY_TAG_WITH_PEOPLE) or
        any_line_matches(text, PERSON_INFOBOX)
    )

def node_of_type(wiki_node, type_str):
    return type(wiki_node) == PARSER_TYPES[type_str]

def certainly_visible_text(wiki_node):
    '''Whether the text is actually displayed on the page'''
    if node_of_type(wiki_node, 'tag') or (
        node_of_type(wiki_node, 'text')
        and not re.match(MAGIC_WORD, wiki_node.value)
        and not re.match('^\s*$', wiki_node.value)
    ):
        return True
    return False

def wikinode_stream(text):
    parsed = mwparserfromhell.parse(text)
    i = 0
    while(True):
        try:
            yield parsed.get(i)
            i += 1
        except IndexError:
            return

def nodes_from_intro_para_begin(node_stream):
    intro_para_has_begun = False
    for wiki_node in node_stream:
        if certainly_visible_text(wiki_node):
            intro_para_has_begun = True
        if intro_para_has_begun:
            yield(wiki_node)
    return

def nodes_until_intro_para_end(node_stream):
    for wiki_node in node_stream:
        if node_of_type(wiki_node, 'header'):
            return
        yield(wiki_node)

def intro_para_node_stream(text):
    return nodes_until_intro_para_end(
        nodes_from_intro_para_begin(
            wikinode_stream(text)
        )
    )

def text_from_wikinode(wiki_node):
    if node_of_type(wiki_node, 'text'):
        return wiki_node.value
    elif node_of_type(wiki_node, 'tag'):
        if not wiki_node.contents:
            return ''
        return wiki_node.contents.strip_code()
    elif node_of_type(wiki_node, 'wikilink'):
        return (wiki_node.text or wiki_node.title).strip_code()
    else:
        # This omits all other node type
        # For example, templates such as pronunciation guides and footnotes
        return ''

def extract_introductory_paragraph(text):
    return ''.join([
        text_from_wikinode(intro_node)
        for intro_node
        in intro_para_node_stream(text)
    ])

with open(SOURCE_PATH, 'rb') as file:
    for _, el in etree.iterparse(file):
        if is_entry(el):
            entry_el = el
            revision_el = find_child_of_tag(el, 'revision')
            text_el = find_child_of_tag(revision_el, 'text')
            text = text_el.text
            if is_biography(text):
                intro_para = extract_introductory_paragraph(text)
                print(intro_para)
                print('\n' * 19)
                sleep(0.1)


import re

import mwparserfromhell

import pdb

class IntroductoryParagraphStreamer():
    '''
        Provided with a stream of Wikipedia article texts, cuts them down to
        their introductory paragraphs and strips out markup and elements that
        are not part of the main text such as references
    '''

    PARSER_TYPES = {
        'text': mwparserfromhell.nodes.text.Text,
        'header': mwparserfromhell.nodes.heading.Heading,
        'template': mwparserfromhell.nodes.template.Template,
        'tag': mwparserfromhell.nodes.tag.Tag,
        'wikilink': mwparserfromhell.nodes.wikilink.Wikilink
    }
    MAGIC_WORD = '\_\_[A-Z]+\_\_'
    
    def stream(self, article_stream):
        return (
            (
                name,
                self.extract_introductory_paragraph(
                    mwparserfromhell.parse(article)
                    )
            )
            for name, article
            in article_stream
        )

    def extract_introductory_paragraph(self, wikicode_node):
        return ''.join([
            self.text_from_wikinode(intro_node)
            for intro_node
            in self.intro_para_node_stream(wikicode_node)
        ])

    def node_of_type(self, wiki_node, type_str):
        '''Identifies type of mwparserfromhell node'''
        return type(wiki_node) == self.PARSER_TYPES[type_str]

    def article_beginning_node(self, wiki_node):
        '''Takes a mwparserfromhell node'''
        if self.node_of_type(wiki_node, 'tag') or (
            self.node_of_type(wiki_node, 'text')
            and not re.match(self.MAGIC_WORD, wiki_node.value)
            and not re.match('^\s*$', wiki_node.value)
        ):
            return True
        return False

    def nodes_from_intro_para_begin(self, node_stream):
        intro_para_has_begun = False
        for wiki_node in node_stream:
            if self.article_beginning_node(wiki_node):
                intro_para_has_begun = True
            if intro_para_has_begun:
                yield(wiki_node)
        return

    def nodes_until_intro_para_end(self, node_stream):
        for wiki_node in node_stream:
            if self.node_of_type(wiki_node, 'header'):
                return
            yield(wiki_node)

    def intro_para_node_stream(self, wikicode_node):
        '''
            Takes a mwparserfromhell node representing a Wikipedia article and
            returns a stream of the child nodes in its introductory paragraph
        '''
        return self.nodes_until_intro_para_end(
            self.nodes_from_intro_para_begin(
                wikicode_node.ifilter(recursive=False)
            )
        )

    def tag_type(self, tag_node):
        '''
            Takes a mwparserfromhell.nodes.tag.Tag
            This class has an attribute 'tag' of class
            mwparserfromhell.wikicode.Wikicode
        '''
        return tag_node.tag.get(0).value

    def text_from_wikinode(self, wiki_node):
        '''
            Takes mwparserfromhell node
            Returns simplified text representation (recursive)
        '''
        if self.node_of_type(wiki_node, 'text'):
            return wiki_node.value
        elif self.node_of_type(wiki_node, 'tag'):
            if (not wiki_node.contents) or (self.tag_type(wiki_node) == 'ref'):
                return ''
            return ' '.join([
                self.text_from_wikinode(node)
                for node
                in wiki_node.contents.ifilter(recursive=False)
            ])
        elif self.node_of_type(wiki_node, 'wikilink'):
            return (wiki_node.text or wiki_node.title).strip_code()
        else:
            # This omits all other node type
            # For example, templates such as pronunciation guides and footnotes
            return ''

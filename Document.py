import os
import html
import html5_parser
from lxml import etree
from lxml.cssselect import CSSSelector

SELECTOR_FIRST_PARAGRAPH = CSSSelector('div[class=body] > div[class=section] > p:first-of-type')


def node_to_text(node):
    return ''.join(node.itertext())


class Document:
    '''Return indexing data from an html document.'''
    def __init__(self, root_dir_path, html_document_path):
        # Paths
        self._root_dir_path = root_dir_path
        self._html_document_path = html_document_path

        # Soups
        text = html_document_path.read()

        capsule = html5_parser.html_parser.parse(text, maybe_xhtml=True)
        self._html_document = etree.adopt_external_document(capsule).getroot()
        self._html_main_column = self._html_document.find('.//div[@class="main-column"]')

        # Properties
        self.slug     = self.get_url_slug()
        self.title    = self.get_page_title()
        self.headings = self.get_page_headings()
        self.text     = self.get_page_text()
        self.preview  = self.get_page_preview()
        self.tags     = self.get_page_tags()



    def get_url_slug(self):
        '''Return the slug after the base url.'''
        url_slug = self._html_document_path.name.__str__()[len(self._root_dir_path):]
        return url_slug

    def get_page_title(self):
        '''Return the title of the page.'''
        page_title = self._html_document.find('.//title').text.strip()
        return page_title

    def get_page_headings(self):
        '''Return all heading tags (<h1>, <h2>, ..., <h6>) and their contents.'''
        all_headings = []
        # <h4>, <h5>, and <h6> seem to be used too granularly (if at all) to be used for heading search.
        for heading in self._html_main_column.iter('h1', 'h2', 'h3'):
            heading = node_to_text(heading)
            if not heading:
                continue

            if heading[:1] == "<":
                # Remove headings that have internal tags. This only happens h4 and below from my observations.
                pass
            else:
                all_headings.append(heading)
        return all_headings

    def get_page_text(self):
        '''Return the text inside the <body> tag.'''
        page_text = node_to_text(self._html_main_column.find('.//div[@class="body"]'))
        #return page_text.replace('\n', ' ').replace('\r', '')
        return ' '.join(page_text.split())

    def get_page_preview(self):
        '''Return a summary of the page.'''
        page_preview = ""
        def set_to_meta_description():
            '''Set preview to the page's meta description.'''
            return node_to_text(self._html_document.find('.//meta[@name="description"]'))
        def set_to_first_paragraph():
            '''Set preview to the first descriptive paragraph on the page.'''
            nodes = SELECTOR_FIRST_PARAGRAPH(self._html_main_column)
            if not nodes:
                return ''

            return node_to_text(nodes[0])
        try:
            page_preview = set_to_meta_description()
        except AttributeError:
            page_preview = set_to_first_paragraph()
        return page_preview.replace('\n', ' ').replace('\r', ' ')

    def get_page_tags(self):
        '''Return the tags for the page.'''
        meta_keywords = self._html_document.find('.//meta[@name="keywords"]')
        if meta_keywords is not None:
            return meta_keywords.get('content')
        else:
            return ''

    def export(self):
        '''Generate the manifest dictionary for an html page.'''
        document = {
            "slug": self.slug,
            "title": self.title,
            #"headings": self.headings,
            "text": self.text,
            "preview": self.preview,
            "tags": self.tags
        }
        return document

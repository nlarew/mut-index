import os
import html
import html5_parser
from lxml import etree
from lxml.cssselect import CSSSelector

def node_to_text(node):
    '''Convert an lxml node to text.'''
    return ''.join(node.itertext())

class Document:
    '''Return indexing data from an html document.'''
    def __init__(self, root_dir_path, html_document_path):
        # Paths
        self._root_dir_path = root_dir_path
        self._html_document_path = html_document_path

        # Document Trees
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
        sel = CSSSelector('title:first-of-type')
        page_title = node_to_text(sel(self._html_document)[0])
        return page_title

    def get_page_headings(self):
        '''Return all heading tags (<h1>, <h2>, ..., <h6>) and their contents.'''
        all_headings = []
        for heading in self._html_main_column.iter('h1', 'h2', 'h3'):
            heading = node_to_text(heading)
            if not heading or heading[:1] == "<":
                continue
            all_headings.append(heading)
        return all_headings

    def get_page_text(self):
        '''Return the text inside the <body> tag.'''
        sel = CSSSelector('.body')
        page_text = node_to_text(sel(self._html_main_column)[0])
        page_text = ' '.join(page_text.split())
        return page_text

    def get_page_preview(self):
        '''Return a summary of the page.'''
        def set_to_meta_description():
            '''Set preview to the page's meta description.'''
            sel = CSSSelector('meta[name="description"]')
            return node_to_text(sel(self._html_document)[0]) #Throws IndexError if no meta[name="description"] tag.
        def set_to_first_paragraph():
            '''Set preview to the first descriptive paragraph on the page.'''
            sel = CSSSelector('div[class=body] > div[class=section] > p:first-of-type')
            nodes = sel(self._html_main_column)
            if not nodes:
                return ''
            return node_to_text(nodes[0])

        try:
            page_preview = set_to_meta_description()
        except IndexError:
            page_preview = set_to_first_paragraph()

        page_preview = ' '.join(page_preview.split())
        return page_preview

    def get_page_tags(self):
        '''Return the tags for the page.'''
        sel = CSSSelector('meta[name="keywords"]')
        meta_keywords = sel(self._html_document)
        if not meta_keywords:
            return ''
        else:
            return meta_keywords[0].get('content')

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

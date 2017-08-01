import os
import sys
import html
import html5_parser
import re
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
        def test_page_preview(preview):
            '''Return False if bad preview.'''
            is_good_preview = False
            bad_previews = [
                re.compile('On this page'),
                re.compile('\u00a9 MongoDB, Inc. 2008-2017'),
                re.compile('Run.'),
                re.compile('Base URL.'),
                re.compile('The Atlas API uses HTTP Digest Authentication.')
            ]
            is_good_preview = not any(map(lambda bp: bp.match(preview), bad_previews))
            return is_good_preview

        def set_to_meta_description():
            '''Set preview to the page's meta description.'''
            candidate_list = self._html_document.cssselect('meta[name="description"]')
            if len(candidate_list) > 0: #Check if the selector found ANY meta[name="description"] tags
                candidate_preview = candidate_list[0]
                if type(candidate_preview) is etree._Element and candidate_preview.tag == 'meta':
                    candidate_preview = candidate_preview.get('content')
                is_good_preview = test_page_preview(candidate_preview)
                if is_good_preview:
                    return candidate_preview
            return False
        def set_to_first_paragraph():
            '''Set preview to the first descriptive paragraph on the page.'''
            preview = 'No good preview found.'
            candidate_selectors = [ #Order is very important! The first good preview is selected without further search.
                '.section > p:first-of-type'
                # 'div .main-column .section > p:first-of-type'
            ]
            for selector in candidate_selectors:
                candidate_list = self._html_main_column.cssselect(selector)
                if len(candidate_list) > 0: #Check if the selector found ANY p tags
                    candidate_preview = candidate_list[0]
                    if type(candidate_preview) is etree._Element and candidate_preview.tag == 'p':
                        candidate_preview = node_to_text(candidate_preview)
                    is_good_preview = test_page_preview(candidate_preview)
                    if is_good_preview:
                        preview = candidate_preview
                        break
            return preview
        page_preview = set_to_meta_description()
        if not page_preview:
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
            "headings": self.headings,
            "text": self.text,
            "preview": self.preview,
            "tags": self.tags
        }
        return document

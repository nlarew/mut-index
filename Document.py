import os
import html
from bs4 import BeautifulSoup

class Document:
    '''Return indexing data from an html document.'''
    def __init__(self, root_dir_path, html_document_path):
        # Paths
        self._root_dir_path = root_dir_path
        self._html_document_path = html_document_path

        # Soups
        self._html_document = BeautifulSoup(html_document_path, "html.parser")
        self._html_main_column = self._html_document.select('div[class="main-column"]')[0]

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
        page_title = self._html_document.title.contents[0].__str__().strip()
        return page_title

    def get_page_headings(self):
        '''Return all heading tags (<h1>, <h2>, ..., <h6>) and their contents.'''
        all_headings = []
        # <h4>, <h5>, and <h6> seem to be used too granularly (if at all) to be used for heading search.
        heading_types = ["h1", "h2", "h3"]#, "h4", "h5", "h6"]
        for heading_type in heading_types:
            headings = self._html_main_column.select(heading_type)
            for heading in headings:
                heading = heading.contents[0].__str__()
                if heading[:1] == "<":
                    # Remove headings that have internal tags. This only happens h4 and below from my observations.
                    pass
                else:
                    all_headings.append(heading)
        return all_headings

    def get_page_text(self):
        '''Return the text inside the <body> tag.'''
        page_text = self._html_main_column.select('div[class=body]')[0].get_text()
        #return page_text.replace('\n', ' ').replace('\r', '')
        return ' '.join(page_text.split()).__str__()

    def get_page_preview(self):
        '''Return a summary of the page.'''
        page_preview = ""
        def set_to_meta_description():
            '''Set preview to the page's meta description.'''
            return self._html_document.select("meta[type='description']")[0]
        def set_to_first_paragraph():
            '''Set preview to the first descriptive paragraph on the page.'''
            first_p_tag = self._html_main_column.select('div[class=body] > div[class=section] > p:first-of-type')[0]
            return first_p_tag
        try:
            page_preview = set_to_meta_description()
        except:
            try:
                page_preview = set_to_first_paragraph()
            except:
                pass
        return page_preview.replace('\n', ' ').replace('\r', ' ')

    def get_page_tags(self):
        '''Return the tags for the page.'''
        page_tags = []
        meta_keywords = self._html_document.find('meta', attrs={'name': 'keywords'})
        if meta_keywords != None:
            page_tags.extend(meta_keywords.attrs['content'].split(', '))
        return page_tags

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

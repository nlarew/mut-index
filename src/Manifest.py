'''Create and export an index manifest.'''
import os
import time
import json
import concurrent.futures
# from termcolor import colored
def colored(s, c): return(s)

from utils.Logger import log_unsuccessful
from utils.ProgressBar import ProgressBar
from Document import Document

BLACKLIST = [
    '401.html',
    '403.html',
    '404.html',
    '410.html',
    'genindex.html',
    'faq.html',
    'search.html',
    'contents.html'
]

class NothingIndexedError(Exception):
    def __init__(self):
        message = 'No documents were found.'
        log_unsuccessful('index')(exception=super(NothingIndexedError, self).__init__(),
                                  message=message)


class Manifest:
    '''Manifest of index results.'''
    def __init__(self, url, globally):
        self.url = url
        self.globally = globally
        self.documents = []

    def add_document(self, document):
        '''Adds a document to the manifest.'''
        self.documents.append(document)

    def json(self):
        '''Return the manifest as json.'''
        manifest = {
            'url': self.url,
            'includeInGlobalSearch': self.globally,
            'documents': self.documents
        }
        return json.dumps(manifest, indent=4)


def generate_manifest(url, root_dir, globally, show_progress):
    '''Build the index and compile a manifest.'''
    start_time = time.time()
    manifest = Manifest(url, globally)
    html_path_info = _get_html_path_info(root_dir, url)
    if not html_path_info:
        raise NothingIndexedError()
    num_documents = len(html_path_info)
    if show_progress:
        progress_bar = ProgressBar(start_time=start_time,
                                   num_documents=num_documents)
    else:
        progress_bar = None
    _process_html_files(html_path_info, manifest, progress_bar)
    _summarize_build(num_documents, start_time)
    return manifest.json()

def _get_html_path_info(root_dir, url):
    '''Return a list of parsed path_info for html files.'''
    def should_index(file):
        '''Returns True the file should be indexed.'''
        return file.endswith('.html') and file not in BLACKLIST
    path_info = []
    for root, _, files in os.walk(root_dir):
        path_info.extend([(file, root+'/', url)
                          for file in files
                          if should_index(file)])
    return path_info

def _parse_html_file(path_info):
    '''Open the html file with the given path then parse the file.'''
    file, file_dir, url = path_info
    with open(file_dir + file, 'r') as html:
        return Document(url, file_dir, html).export()

def _process_html_files(html_path_info, manifest, progress_bar=None):
    '''Apply a function to a list of .html file paths in parallel.'''
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for document in executor.map(_parse_html_file, html_path_info):
            manifest.add_document(document)
            if progress_bar:
                progress_bar.update(document['slug'])

def _summarize_build(num_documents, start_time):
    summary = ('\nFinished indexing!\n'
               'Indexed {num_docs} documents in {time} seconds.')
    summary = summary.format(num_docs=num_documents,
                             time=str(time.time() - start_time))
    print(colored(summary, 'green'))

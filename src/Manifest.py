import os, sys, time, math, json
import concurrent.futures
from termcolor import colored

from utils.ProgressBar import ProgressBar
from Document import Document

class Manifest:
    '''Build the index and compile a manifest.'''
    def __init__(self, base_url, root_dir, include_in_global_search, show_progress):
        self.root_dir = root_dir
        self.manifest = {
            'url': base_url,
            'includeInGlobalSearch': include_in_global_search,
            'documents': []
        }
        self.blacklist = [
            '401.html',
            '403.html',
            '404.html',
            '410.html',
            'genindex.html',
            'faq.html',
            'search.html',
            'contents.html'
        ]
        self.num_documents_processed = 0
        self.start_time = time.time()
        self.html_files = self._get_html_files()
        self.progress_bar = ProgressBar(start_time=self.start_time, num_documents=len(self.html_files)) if show_progress else None

    def build(self, filetype=None):
        '''Build the index from scratch.'''
        self._process_html_files(self.html_files)
        self._summarize_build()
        if filetype and filetype == 'json':
            return json.dumps(self.manifest, indent=4)
        else:
            print('!! Manifest returned as python dict object.')
            return self.manifest

    def _get_html_files(self):
        '''Return a list of absolute paths for html files.'''
        html_files = []
        def should_index(file):
            '''Return a boolean indicating whether the file should be indexed.'''
            return file.endswith('.html') and file not in self.blacklist
        for root, _, files in os.walk(self.root_dir):
            html_files.extend([str(os.path.join(root, file)) for file in files if should_index(file)])
        self.num_documents_total = len(html_files)
        return html_files


    def _process_html_files(self, html_files):
        '''Parse a list of .html file paths in parallel.'''
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for document in executor.map(self._parse_html_file, html_files):
                self.manifest['documents'].append(document)
                self.num_documents_processed += 1
                if self.progress_bar:
                    self.progress_bar.update(document['slug'])


    def _parse_html_file(self, html_file):
        '''Open the html file with the given path then parse the file.'''
        with open(html_file, 'r') as doc:
            return Document(self.manifest['url'], self.root_dir, doc).export()

    def _summarize_build(self):
        summary = '\nFinished indexing!\nIndexed {num_docs} documents in {time} seconds.'
        summary = summary.format(num_docs=self.num_documents_processed,
                                 time=str(time.time() - self.start_time))
        print(colored(summary, 'green'))

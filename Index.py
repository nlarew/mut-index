import os
import sys
import time
import math
import concurrent.futures
from Document import Document

class Index:
    '''Build the index and compile a JSON manifest.'''
    def __init__(self, base_url, root_dir, include_in_global_search):
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
        self.num_documents_total = 0
        self.num_documents_processed = 0
        self.start_time = time.time()

    def build(self):
        '''Build the index from scratch.'''
        html_files = self._get_html_files()
        self._process_html_files(html_files)
        self._summarize_build()

    def _summarize_build(self):
        summary = 'Finished indexing!\nIndexed {num_docs} documents in {time} seconds.\n'
        summary = summary.format(num_docs=self.num_documents_processed,
                                 time=str(time.time() - self.start_time))
        print(summary)

    def _process_html_files(self, html_files):
        '''Parse a list of .html file paths in parallel.'''
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for document in executor.map(self._parse_html_file, html_files):
                self.manifest['documents'].append(document)
                self.num_documents_processed += 1
                self.update_progress_bar(document)

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


    def _parse_html_file(self, html_file):
        '''Open the html file with the given path then parse the file.'''
        with open(html_file, 'r') as doc:
            return Document(self.root_dir, doc).export()

    def update_progress_bar(self, doc):
        '''Update the stdout progress bar.'''
        total_elapsed_time = '{elapsed_time: .3f} (s)'
        elapsed_time=round(time.time() - self.start_time, 3)
        total_elapsed_time = total_elapsed_time.format(elapsed_time=elapsed_time).ljust(13, ' ')

        progress_count = '[{num_docs_processed} / {num_docs_total}]'
        total_digits = len(str(self.num_documents_total))
        num_docs_processed = self.num_documents_processed.__str__().ljust(total_digits)
        progress_count = progress_count.format(num_docs_processed=num_docs_processed,
                                               num_docs_total=self.num_documents_total)

        progress_bar = '{percent_done}|{progress_bar_color}{done}{todo}{default_color}|'
        done=math.floor(30*self.num_documents_processed / self.num_documents_total)*u'\u2588'
        todo=(30 - math.floor(30*self.num_documents_processed / self.num_documents_total))*' '
        percent_done = (str(int(100 * self.num_documents_processed / self.num_documents_total)) + '%').rjust(4, ' ')
        progress_bar_color = '\033[94m' if self.num_documents_processed != self.num_documents_total else '\033[92m'
        default_color = '\033[0m'
        progress_bar = progress_bar.format(done=done,
                                           todo=todo,
                                           percent_done=percent_done,
                                           progress_bar_color=progress_bar_color,
                                           default_color=default_color)
        current_doc_slug = doc['slug']

        logstring = total_elapsed_time + '   ' + progress_bar + '    '+ progress_count + '    ' + current_doc_slug
        if self.num_documents_processed == self.num_documents_total:
            logstring += "\n"

        if self.num_documents_processed == 1:
            print("\nProcessing Documents...")
            print(
                'Elapsed Time:'.ljust(14, ' '),
                'Progress:'.ljust(39, ' '),
                'HTML Files:'.ljust(8+2*total_digits, ' '),
                'Current File:'
            )
        sys.stdout.write("\033[K") #Delete contents of stdout line.
        print(logstring, end="\r") #Print to stdout without newline then carriage return.3
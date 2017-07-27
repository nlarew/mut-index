import time, math, sys
from termcolor import colored

class Section:
    def __init__(self, header='', output='', format='', data={}):
        self.header = header
        self.output = output
        self.data = data
        self.width = 0
    def update(self, num_processed):
        pass

class Timer(Section):
    def __init__(self, start_time):
        self.header='Elapsed Time'
        self.output='{elapsed_time: 3.3f} (s)'
        self.data={
            'elapsed_time': 0
        }
        self.start_time = start_time
        self.width = 13
    def update(self):
        self.data['elapsed_time'] = round(time.time() - self.start_time, 3)

class Percentage(Section):
    def __init__(self, num_documents):
        self.header = 'Progress'
        self.output = '{percent_done: 2.2f}%|{done}{todo}|'
        self.data = {
            'percent_done': 0,
            'done': '',
            'todo': ' ' * 30
        }
        self.width = 39
        self.num_documents = num_documents
    def update(self, num_processed):
        self.data['percent_done'] = 100*(num_processed / self.num_documents)
        self.data['done'] = self._colorize(u'\u2588' * math.floor(30*self.data['percent_done']/100))
        self.data['todo'] = ' ' * (30 - math.floor(30*self.data['percent_done']/100))
    def _colorize(self, input_string):
        if self.data['percent_done'] == 100:
            color = 'green'
        else:
            color = 'blue'
        return colored(input_string, color)

class Counter(Section):
    def __init__(self, num_documents):
        self.header = 'Files'
        self.output = '[{num_processed} / {num_documents}]'
        self.data = {
            'num_processed': 0,
            'num_documents': int(num_documents)
        }
        self.width = 5 + 2*len(str(num_documents))
    def update(self, num_processed):
        self.data['num_processed'] = num_processed

class CurrentFile(Section):
    def __init__(self):
        self.header = 'Last Processed File'
        self.output = '{current_file}'
        self.data = {
            'current_file': ''
        }
        self.width = 0
    def update(self, current_file):
        self.data['current_file'] = current_file
        self.width = len(current_file)

class ProgressBar():
    def __init__(self, num_documents, start_time):
        self.sections = {
            'Timer': Timer(start_time),
            'Percentage': Percentage(num_documents),
            'Counter': Counter(num_documents),
            'CurrentFile': CurrentFile()
        }
        self.num_processed = 0
        self.build()

    def build(self):
        self._print_header_row()
        self._print_sections()

    def update(self, processed_file_name):
        self.num_processed += 1
        for section_name in self.sections:
            section = self.sections[section_name]
            update_call = 'self.sections["' + type(section).__name__ + '"].update('
            num_args = section.update.__code__.co_argcount - 1 # Subtract one for implicit 'self' argument
            if num_args > 0:
                update_args = section.update.__code__.co_varnames # Tuple of all argument names
                for i, arg in enumerate(update_args):
                    more_args = i != (num_args - 1) # True if more args. subtract one for zero-index normalization
                    if arg == 'num_processed':
                        update_call += 'num_processed=' + str(self.num_processed) + more_args*','
                    if arg == 'current_file':
                        update_call += 'current_file="' + processed_file_name + '"' + more_args*','
            update_call += ')'
            eval(update_call)
        self._print_sections()

    def _print_header_row(self):
        header_row = ''
        for section in self.sections.values():
            header_row += (section.header + ':').ljust(section.width, ' ') + '   '
        print(header_row)

    def _print_sections(self):
        section_row = ''
        for position, section in enumerate(self.sections.values()):
            section_string = 'section.output.format('
            for key in section.data:
                value = section.data[key] if type(section.data[key]) in [int, float] else '"' + section.data[key] + '"'
                section_string += key + '=' + str(value) + ','
            section_string = section_string[:-1] + ').rjust(int(str(section.width)), " ")'
            section_row += eval(section_string) + '   '
        sys.stdout.write("\033[K") # Delete contents of stdout line.
        print(section_row, end='\r') # Print to stdout without newline then carriage return.

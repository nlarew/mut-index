'''
Usage:
    mut-index <root> -o <outputFile> --url <url> [--includeInGlobalSearch]

    -h, --help               list CLI prototype, arguments, and options
    --url <url>              base url for the product to index
    --includeInGlobalSearch  includes the manifest when searching all properties
    -o <outputFile>          name of the file to output the manifest json to
    <root>                   path of the directory containing html files
'''

import os
import time
import json
from Index import Index
from docopt import docopt

def main():
    '''Generate index files.'''
    options = docopt(__doc__)
    root_dir = options['<root>']
    output_file = options['-o']
    base_url = options['--url'] #todo: make sure this is a safe url
    include_in_global_search = options['--includeInGlobalSearch']

    print_intro_message(root_dir, output_file, base_url, include_in_global_search)
    
    #Build the Index and manifest
    index = Index(base_url, root_dir, include_in_global_search)
    index.build()
    manifest = json.dumps(index.manifest, indent=4)

    # Export the manifest
    print('Exporting index manifest...')
    with open('./manifests/'+output_file, 'w') as file:
        file.seek(0)
        file.truncate()
        file.write(manifest)
    print('Index written to', output_file, '\n')

def print_intro_message(root_dir, output_file, base_url, include_in_global_search):
    '''Print information on the current index task.'''
    intro_message = '\nGenerating manifest {0}'.format(output_file)
    intro_message += '\nManifest will{is_global}be included in global property searches\n\n'.format(
        is_global=(' ' if include_in_global_search else ' NOT '))
    intro_message += 'url: {base_url}\nroot: {root_dir}\n'.format(base_url=base_url, root_dir=root_dir)
    print(intro_message)

if __name__ == "__main__":
    main()

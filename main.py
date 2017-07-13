'''
Usage:
    mut-index --url <url> <propertyName> <root> [--includeInGlobalSearch]

    -h, --help               list CLI prototype, arguments, and options
    --url <url>              base url for the product to index
    --includeInGlobalSearch  includes the manifest when searching all properties
    <propertyName>           name of the property to index
    <root>                   path of the directory containing html files
'''

import os
import time
import json
from Index import Index
from docopt import docopt

## Server Manual
# mut-index --url http://docs.mongodb.com/ manual-master /Users/nick/VirtualEnvProjects/mut-index/html_files
# mut-index --url http://docs.mongodb.com/ manual-master /Users/nick/mongodb/docs/build/DOCS-9808/html --includeInGlobalSearch

def print_intro_message(property_name, base_url, root_dir, include_in_global_search):
    '''Print information on the current index task.'''
    intro_message = '''
    Indexing {property_name}
    Manifest will {is_global}be included in global property searches.

        url: {base_url}
       root: {root_dir}
    '''.format(property_name=property_name, base_url=base_url, root_dir=root_dir, is_global=('' if include_in_global_search else 'NOT '))
    print(intro_message)

def main():
    '''Generate index files.'''
    options = docopt(__doc__)

    property_name = options['<propertyName>']
    base_url = options['--url'] #todo: make sure this is a safe url
    root_dir = options['<root>']
    include_in_global_search = options['--includeInGlobalSearch']

    print_intro_message(property_name, base_url, root_dir, include_in_global_search)

    #Build the Index and manifest
    index = Index(base_url, property_name, root_dir, include_in_global_search)
    index.build()
    manifest = json.dumps(index.manifest, indent=4)

    # Export the manifest
    print('Exporting index manifest...')
    with open('./manifest.json', 'a') as file:
        file.seek(0)
        file.truncate()
        file.write(manifest)
    print('Index written to manifest.json!\n')

if __name__ == "__main__":
    main()

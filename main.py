'''
Usage:
    mut-index <root> -o <outputFile> --url <url> [--includeInGlobalSearch]

    -h, --help               List CLI prototype, arguments, and options.
    <root>                   Path to the directory containing html files.
    -o <outputFile>          File name for the output manifest json.
    --url <url>              Base url of the property.
    --includeInGlobalSearch  Includes the manifest when searching all properties. Default: False
'''

import os
import time
import json
import requests
from Index import Index
from docopt import docopt
from s3upload import upload_manifest_to_s3

def main():
    '''Generate index files.'''
    options = docopt(__doc__)
    root_dir = options['<root>']
    output_file = options['-o']
    base_url = options['--url']
    include_in_global_search = options['--includeInGlobalSearch']

    print_intro_message(root_dir, output_file, base_url, include_in_global_search)

    #Build the Index and manifest
    index = Index(base_url, root_dir, include_in_global_search)
    index.build()
    manifest = json.dumps(index.manifest, indent=4)

    # Export the manifest
    upload_manifest_to_s3('nicklarew', output_file, manifest)
    # Refresh Marian
    requests.post('http://01cfe8a4.ngrok.io/refresh', data={})

    # with open('./manifests/'+output_file, 'w') as file:
    #     file.seek(0)
    #     file.truncate()
    #     file.write(manifest)
    # print('Index written to', output_file, '\n')

def print_intro_message(root_dir, output_file, base_url, include_in_global_search):
    '''Print information on the current index task.'''
    intro_message = '\nGenerating manifest {0}'.format(output_file)
    intro_message += '\nManifest will{is_global}be included in global property searches\n\n'.format(
        is_global=(' ' if include_in_global_search else ' NOT '))
    intro_message += 'url: {base_url}\nroot: {root_dir}\n'.format(base_url=base_url, root_dir=root_dir)
    print(intro_message)

if __name__ == "__main__":
    main()

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
from IntroMessage import print_intro_message

def main():
    '''Generate index files.'''

    # Parse options and print intro message
    options = docopt(__doc__)
    root_dir = options['<root>']
    output_file = options['-o']
    base_url = options['--url']
    include_in_global_search = options['--includeInGlobalSearch']
    print_intro_message(root_dir, output_file, base_url, include_in_global_search)
    # Build the Index
    index = Index(base_url, root_dir, include_in_global_search)
    index.build()
    print('index\n', index)
    # Export the manifest
    manifest = json.dumps(index.manifest, indent=4)
    upload_manifest_to_s3('nicklarew', output_file, manifest)
    # Refresh Marian
    requests.post('http://01cfe8a4.ngrok.io/refresh', data={})

if __name__ == "__main__":
    main()

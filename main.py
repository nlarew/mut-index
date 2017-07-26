'''
Usage:
    mut-index <root> -o <output> -u <url> [-b <bucket> -p <prefix> -g]

    -h, --help             List CLI prototype, arguments, and options.
    <root>                 Path to the directory containing html files.
    -o, --output <output>  File name for the output manifest json. (e.g. manual-v3.2.json)
    -u, --url <url>        Base url of the property.

    -b, --bucket <bucket>  Name of the s3 bucket to upload the index manifest to. [default: docs-mongodb-org-prod]
    -p, --prefix <prefix>  Name of the s3 prefix to attached to the manifest. [default: search-indexes]
    -g, --global           Includes the manifest when searching all properties.
'''
# external/built-in imports
import os
import time
from docopt import docopt
from termcolor import colored
# internal imports
from Index         import Index
from s3upload      import upload_manifest_to_s3
from IntroMessage  import print_intro_message
from MarianActions import refresh_marian

def main():
    '''Generate index files.'''
    options          = docopt(__doc__)
    root             = options['<root>']
    output           = options['--output']
    url              = options['--url']
    bucket           = options['--bucket']
    prefix           = options['--prefix']
    include_globally = options['--global']

    print_intro_message(root, output, url, include_globally)
    manifest = Index(url, root, include_globally).build(filetype='json')
    upload_manifest_to_s3(bucket, prefix, output, manifest)
    refresh_marian()
    print('\nAll according to plan!\n')

if __name__ == "__main__":
    main()

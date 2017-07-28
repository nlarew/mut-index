'''
Usage:
    mut-index <root> -o <output> -u <url> [-b <bucket> -p <prefix> -g, --no-progress]

    -h, --help             List CLI prototype, arguments, and options.
    <root>                 Path to the directory containing html files.
    -o, --output <output>  File name for the output manifest json. (e.g. manual-v3.2.json)
    -u, --url <url>        Base url of the property.

    -b, --bucket <bucket>  Name of the s3 bucket to upload the index manifest to. [default: docs-mongodb-org-prod]
    -p, --prefix <prefix>  Name of the s3 prefix to attached to the manifest. [default: search-indexes]
    -g, --global           Includes the manifest when searching all properties.
    --no-progress          Hides the progress bar.
'''
# external/built-in imports
import os
import time
from docopt import docopt
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
    no_progress_bar  = options['--no-progress']

    print_intro_message(root, output, url, include_globally)
    manifest = Index(url, root, include_globally, no_progress_bar).build()#filetype='json')
    #upload_manifest_to_s3(bucket, prefix, output, manifest)
    print(type(manifest['documents']))
    for x in manifest['documents']:#filter(lambda d: d['preview'] is 'No good preview found.', manifest['documents']):
        print(x['preview'])
    #with open('/Users/nick/VirtualEnvProjects/mut-index/cloud-manifest.json', 'w') as m:
        #m.write(manifest2)
    

    #refresh_marian()
    print('\nAll according to plan!\n')

if __name__ == "__main__":
    main()

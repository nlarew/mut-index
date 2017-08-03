# pylint: disable=line-too-long
'''
Usage:
    mut-index <root> -o <output> -u <url> [-b <bucket> -p <prefix> -g -s]

    -h, --help             List CLI prototype, arguments, and options.
    <root>                 Path to the directory containing html files.
    -o, --output <output>  File name for the output manifest json. (e.g. manual-v3.2.json)
    -u, --url <url>        Base url of the property.

    -b, --bucket <bucket>  Name of the s3 bucket to upload the index manifest to. [default: docs-mongodb-org-prod]
    -p, --prefix <prefix>  Name of the s3 prefix to attached to the manifest. [default: search-indexes]
    -g, --global           Includes the manifest when searching all properties.
    -s, --show-progress    Shows a progress bar and other information via stdout.
'''
# internal imports
from docopt import docopt
from Manifest import generate_manifest
from MarianActions import refresh_marian, FailedRefreshError
from s3upload import upload_manifest_to_s3
from utils.IntroMessage import print_intro_message

def main():
    '''Generate index files.'''
    options = docopt(__doc__)
    root = options['<root>']
    output = options['--output']
    url = options['--url']
    bucket = options['--bucket']
    prefix = options['--prefix']
    globally = options['--global']
    show_progress = options['--show-progress']

    print_intro_message(root, output, url, globally)
    manifest = generate_manifest(url, root, globally, show_progress)
    backup = upload_manifest_to_s3(bucket, prefix, output, manifest)
    try:
        refresh_marian()
        print('\nAll according to plan!')
    except FailedRefreshError:
        backup.restore()


if __name__ == "__main__":
    main()

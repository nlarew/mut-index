'''
Usage:
    mut-index <root> -o <output> -u <url> [-b <bucket> -p <prefix> -g, --show-progress]

    -h, --help             List CLI prototype, arguments, and options.
    <root>                 Path to the directory containing html files.
    -o, --output <output>  File name for the output manifest json. (e.g. manual-v3.2.json)
    -u, --url <url>        Base url of the property.

    -b, --bucket <bucket>  Name of the s3 bucket to upload the index manifest to. [default: docs-mongodb-org-prod]
    -p, --prefix <prefix>  Name of the s3 prefix to attached to the manifest. [default: search-indexes]
    -g, --global           Includes the manifest when searching all properties.
    -s, --show-progress    Shows a progress bar and other information via stdout.
'''
# external/built-in imports
import sys, os, time
sys.path.append(os.getcwd())
from docopt              import docopt
# internal imports
from Manifest            import Manifest
from MarianActions       import refresh_marian, FailedRefreshError
from s3upload            import upload_manifest_to_s3
from utils.IntroMessage  import print_intro_message
from utils.Logger        import log_unsuccessful

def main():
    '''Generate index files.'''
    options          = docopt(__doc__)
    root             = options['<root>']
    output           = options['--output']
    url              = options['--url']
    bucket           = options['--bucket']
    prefix           = options['--prefix']
    include_globally = options['--global']
    show_progress    = options['--show-progress']

    print_intro_message(root, output, url, include_globally)
    manifest = Manifest(url, root, include_globally, show_progress).build(filetype='json')
    backup = upload_manifest_to_s3(bucket, prefix, output, manifest)
    try:
        refresh_marian()
    except FailedRefreshError as ex:
        backup.restore()
    else:
        print('\nAll according to plan!')
    finally:
        print('\n')


if __name__ == "__main__":
    main()

def print_intro_message(root_dir, output_file, base_url, include_in_global_search):
    '''Print information on the current index task.'''
    print('\n### Generating Index Manifest\n')
    print(
        ("  file: {1}\n"
         "  root: {0}\n"
         "   url: {2}\n"
         "global: {3}\n").format(root_dir, output_file, base_url, 'True' if include_in_global_search else 'False')
    )
def print_intro_message(root_dir, output_file, base_url, include_in_global_search):
    '''Print information on the current index task.'''
    intro_message = '\nGenerating manifest {0}'.format(output_file)
    intro_message += '\nManifest will{is_global}be included in global property searches\n\n'.format(
        is_global=(' ' if include_in_global_search else ' NOT '))
    intro_message += 'url: {base_url}\nroot: {root_dir}\n'.format(base_url=base_url, root_dir=root_dir)
    print(intro_message)
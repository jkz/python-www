def header_case(name):
    splits = name.replace('-', '_').split('_')
    if splits[0].upper() == 'HTTP':
        splits = splits[1:]
    return '-'.join(w.capitalize() for w in splits)

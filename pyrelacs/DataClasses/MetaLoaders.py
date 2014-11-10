import linecache
import re
import types
import yaml
from IPython import embed


def flatten_dict(d, prefix=None):
    """
    Takes a nested dictionary and flattens it. Values in nested dictionaries are stored behind new keys
    that are generated by concatenating the nested keys with a double underscore. Spaces are replaced
    by single underscores and non-alphanumeric characters are deleted. The keys itself are converted to
    lower case.

    :param d: dictionary
    :param prefix: needed for recursion and not important on the upper level.
    :return: flattened dictionary
    """
    if prefix is None: prefix = []
    ret = {}
    for k, v in d.iteritems():
        k = re.sub('[^0-9a-zA-Z_]+', '', k.lower().replace(" ", "_"))
        if type(v) == types.DictionaryType:
            ret.update(flatten_dict(v, prefix + [k]))
        else:
            ret["__".join(prefix + [k])] = v
    return ret

def parse_old_meta(meta):
    ret = {'description':[]}

    for line in meta:
        if '=' in line:
            k,v = [e.strip() for e in line.split('=')]
            ret[k] = v
        elif ':' in line:
            k,v = [e.strip() for e in line.split(':')]
            ret[k] = v
        else:
            ret['description'].append(line.strip())
    ret['description'] = ', '.join(ret['description'])
    return ret

def parse_meta(block, filename):
    meta = [linecache.getline(filename, i + 1)[1:] for i in range(block.start, block.end)]
    try:
        tmp =  yaml.load(''.join(meta))
        if type(tmp) == str:
            return parse_old_meta(meta)
        else:
            return tmp
    except:
        tmp = yaml.load(''.join(fix_meta_block(meta)))
        if type(tmp) == str:
            return parse_old_meta(meta)
        else:
            return tmp



def fix_meta_block(meta):
    indent_stack = [(len(meta[0]) - len(meta[0].lstrip())) * ' ']
    indent = indent_stack[0]
    for i, m in enumerate(meta):
        while not m.startswith(indent):
            indent_stack.pop()
            indent = indent_stack[-1]

        if m.split(':')[-1].strip() and len(meta) > i + 1:
            if len(indent) != (len(meta[i + 1]) - len(meta[i + 1].lstrip())):
                meta[i + 1] = indent + meta[i + 1].lstrip()

        if not m.split(':')[-1].strip():
            indent_stack.append(indent)
            ws1 = len(m) - len(m.lstrip())
            ws2 = len(meta[i + 1]) - len(meta[i + 1].lstrip())
            indent += (ws2 - ws1) * ' '
    return meta
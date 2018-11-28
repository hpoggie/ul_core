import re


def serialize(args):
    return ''.join([{int: 'i', bool: 'b'}[type(x)] +
                    (repr(int(x)) if isinstance(x, bool) else repr(x))
                    for x in args])


def deserialize(packet):
    return [{'i': int, 'b': bool}[s[0]](int(s[1:]))
            for s in re.findall('[a-z][^a-z]*', packet)]

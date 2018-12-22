import re


# Longer than this and the deserialization becomes slow.
# Allowing arbitrary length packets could lead to DoS attacks.
# Under normal circumstances you will never need to send a
# packet this long.
maxPacketLength = 10000


class DeserializationError(Exception):
    pass


def serialize(args):
    def typeSpecifier(x):
        return {int: 'i', bool: 'b', str: 's'}[type(x)]

    def data(x):
        return x if isinstance(x, str) else repr(int(x))

    # \uffff is guaranteed not to be a valid unicode character.
    # Thus it will never be part of a string that we would
    # want to serialize and can be used as a separator for strings
    return bytes('\uffff'.join([typeSpecifier(x) + data(x) for x in args]),
                 'utf-8')


def deserialize(packet):
    if len(packet) > maxPacketLength:
        raise DeserializationError('Packet is too long.')

    try:
        packet = packet.decode('utf-8')
    except UnicodeDecodeError as e:
        raise DeserializationError('Bad unicode', e)

    ret = []

    for s in re.findall('[a-z][^\uffff]+', packet):
        try:
            t = {'i': int, 'b': bool, 's': str}[s[0]]
        except KeyError as e:
            raise DeserializationError('Bad type specifier', e)

        try:
            i = t(s[1:])
        except ValueError as e:
            raise DeserializationError('Bad literal', e)

        ret.append(i)

    if ret == []:
        raise DeserializationError('No sequence found.')

    return ret

import re


# Longer than this and the deserialization becomes slow.
# Allowing arbitrary length packets could lead to DoS attacks.
# Under normal circumstances you will never need to send a
# packet this long.
maxPacketLength = 10000


class DeserializationError(Exception):
    pass


def serialize(args):
    return ''.join([{int: 'i', bool: 'b'}[type(x)] +
                    (repr(int(x)) if isinstance(x, bool) else repr(x))
                    for x in args])


def deserialize(packet):
    if len(packet) > maxPacketLength:
        raise DeserializationError('Packet is too long.')

    ret = []

    for s in re.findall('[a-z][^a-z]*', packet):
        try:
            t = {'i': int, 'b': bool}[s[0]]
        except KeyError as e:
            raise DeserializationError('Bad type specifier', e)

        try:
            i = int(s[1:])
        except ValueError as e:
            raise DeserializationError('Bad literal', e)

        ret.append(i)

    if ret == []:
        raise DeserializationError('No sequence found.')

    return ret

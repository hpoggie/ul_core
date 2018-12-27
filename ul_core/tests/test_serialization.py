import pytest
from net.serialization import serialize, deserialize, DeserializationError


def test_sanity_check():
    deserialize(serialize([135, True, 'abc']))


def test_bools():
    lst = [False, True, False]
    assert lst == deserialize(serialize(lst))


def test_no_separator():
    try:
        deserialize(b'i1i2s3')
    except DeserializationError:
        pass
    else:
        assert False


def test_invalid_characters():
    try:
        deserialize(b'i1@34$')
    except DeserializationError:
        pass
    else:
        assert False


def test_invalid_starting_character():
    try:
        i = deserialize(b'00000')
    except DeserializationError:
        pass
    else:
        print(i)
        assert False


@pytest.mark.timeout(5, method='thread')
def test_too_long_integer():
    try:
        a = deserialize(b'i' + b'6' * (10 ** 6))
    except DeserializationError:
        pass
    else:
        assert False

import pytest
from net.serialization import serialize, deserialize


def test_sanity_check():
    deserialize(serialize([135, True]))


def test_invalid_characters():
    try:
        deserialize('i1@34$')
    except Exception:
        pass
    else:
        assert False


@pytest.mark.timeout(5, method='thread')
def test_too_long_integer():
    try:
        a = deserialize('i' + '6' * (10 ** 6))
    except Exception:
        pass
    else:
        assert False

import pytest
from ..main import is_binary


def test_is_binary_text():
    text_data = "Hello, world!".encode('utf-8')
    assert is_binary(text_data) is False


def test_is_binary_binary():
    binary_data = bytes([0x80, 0x81, 0x82, 0x83]) # Ascii ends at 127
    assert is_binary(binary_data) is True

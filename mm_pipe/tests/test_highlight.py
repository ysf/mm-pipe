import pytest
from whats_that_code.election import guess_language_all_methods
from ..main import format_with_highlight


def test_detect_language_python():
    content = """
def hello_world():
    print("Hello, World!")
    return True """
    assert guess_language_all_methods(content) == "python"


def test_format_with_highlight_no():
    content = "print('hello')"
    result = format_with_highlight(content, "no")
    assert result == content


def test_format_with_highlight_specific_language():
    content = "print('hello')"
    result = format_with_highlight(content, "python")
    assert result == "```python\nprint('hello')\n```"


def test_format_with_highlight_auto_python():
    content = """
def test():
    return True"""
    result = format_with_highlight(content, "auto")
    assert result == "```python\n\ndef test():\n    return True\n```"


def test_format_with_highlight_empty():
    content = ""
    with pytest.raises(SystemExit) as exc_info:
        format_with_highlight(content, "auto")
    assert exc_info.value.code == 1

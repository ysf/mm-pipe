import pytest
from unittest.mock import MagicMock, patch
from ..main import process_stdin_content


@patch('sys.stdin.buffer.read')
def test_process_stdin_content_text_within_limits(mock_stdin_read):
    mock_stdin_read.return_value = "This is text".encode('utf-8')
    mock_client = MagicMock()
    channel_id = "channel123"
    message = "some message"
    file_ids = []
    highlight = "no"
    max_length = 1000

    result_message, result_file_ids = process_stdin_content(
        mock_client, channel_id, message, file_ids, highlight, max_length
    )

    assert "some message" in result_message
    assert "This is text" in result_message
    assert mock_client.upload_content.call_count == 0
    assert len(result_file_ids) == 0


@patch('sys.stdin.buffer.read')
def test_process_stdin_content_text_exceeds_max_length(mock_stdin_read):
    mock_stdin_read.return_value = "This is some longer text".encode('utf-8')
    mock_client = MagicMock()
    mock_client.upload_content.return_value = {
        'file_infos': [{'id': 'file123'}]
    }
    channel_id = "channel123"
    message = "some message"
    file_ids = []
    highlight = "no"
    max_length = 10

    result_message, result_file_ids = process_stdin_content(
        mock_client, channel_id, message, file_ids, highlight, max_length
    )

    assert result_message == "some message"
    assert mock_client.upload_content.call_count == 1
    assert len(result_file_ids) == 1
    assert 'file123' in result_file_ids


@patch('sys.stdin.buffer.read')
def test_process_stdin_content_binary(mock_stdin_read):
    mock_stdin_read.return_value = bytes([0x80, 0x81, 0x82, 0x83])
    mock_client = MagicMock()
    mock_client.upload_content.return_value = {
        'file_infos': [{'id': 'binary_file123'}]
    }
    channel_id = "channel123"
    message = "some message"
    file_ids = []
    highlight = "no"
    max_length = 1000

    result_message, result_file_ids = process_stdin_content(
        mock_client, channel_id, message, file_ids, highlight, max_length
    )

    assert result_message == "some message"
    assert mock_client.upload_content.call_count == 1
    assert len(result_file_ids) == 1
    assert 'binary_file123' in result_file_ids


@patch('sys.stdin.buffer.read')
def test_process_stdin_content_binary_empty_message(mock_stdin_read):
    mock_stdin_read.return_value = bytes([0x80, 0x81, 0x82, 0x83])
    mock_client = MagicMock()
    mock_client.upload_content.return_value = {
        'file_infos': [{'id': 'binary_file123'}]
    }
    channel_id = "channel123"
    message = ""
    file_ids = []
    highlight = "auto"
    max_length = 1000

    result_message, result_file_ids = process_stdin_content(
        mock_client, channel_id, message, file_ids, highlight, max_length
    )

    assert result_message == "attaching binary content:\n"
    assert mock_client.upload_content.call_count == 1
    assert len(result_file_ids) == 1
    assert 'binary_file123' in result_file_ids


@patch('sys.stdin.buffer.read')
def test_process_stdin_empty(mock_stdin_read):
    mock_stdin_read.return_value = b""
    mock_client = MagicMock()
    channel_id = "channel123"
    message = "some message"
    file_ids = []
    highlight = "auto"
    max_length = 1000

    result_message, result_file_ids = process_stdin_content(
        mock_client, channel_id, message, file_ids, highlight, max_length
    )

    assert result_message == "some message"
    assert result_file_ids == []
    assert mock_client.upload_content.call_count == 0

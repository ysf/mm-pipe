import os
import pytest

from unittest.mock import patch, MagicMock
from mm_pipe.main import ConfigManager


@pytest.fixture
def mock_config_file(tmp_path):
    config_path = tmp_path / "test_config.conf"
    config_content = """
[default]
server_url=https://mattermost.example.com
token=default_token

[tokencmd_only]
server_url=https://mattermost.example.com
tokencmd=echo "cmd_token"

[both_tokens]
server_url=https://mattermost.example.com
token=config_token
tokencmd=echo "cmd_token"
"""
    config_path.write_text(config_content)
    return str(config_path)


def test_config_manager_loads_tokencmd(mock_config_file):
    config_manager = ConfigManager(mock_config_file)
    default_instance = config_manager.get_instance("default")
    assert default_instance["token"] == "default_token"
    assert default_instance["tokencmd"] == ""

    tokencmd_instance = config_manager.get_instance("tokencmd_only")
    assert tokencmd_instance["token"] == ""
    assert tokencmd_instance["tokencmd"] == 'echo "cmd_token"'

    both_instance = config_manager.get_instance("both_tokens")
    assert both_instance["token"] == "config_token"
    assert both_instance["tokencmd"] == 'echo "cmd_token"'


@patch('subprocess.check_output')
def test_tokencmd_execution(mock_check_output, mock_config_file):
    from mm_pipe.main import main

    mock_check_output.return_value = b"token_from_cmd\n"

    with patch('sys.argv', ['mm-pipe', '--instance', 'tokencmd_only', '--list-users']), \
         patch('mm_pipe.main.ConfigManager'), \
         patch('mm_pipe.main.MattermostClient'):

        mock_config_manager = MagicMock()
        mock_config_manager.get_instance.return_value = {
            'server_url': 'https://mattermost.example.com',
            'token': '',
            'tokencmd': 'some_password_command retrieving secrets',
            'auto_highlight': False,
            'max_message_length': 4000
        }

        from mm_pipe.main import ConfigManager as OriginalConfigManager
        with patch('mm_pipe.main.ConfigManager', return_value=mock_config_manager):
            main()

    mock_check_output.assert_called_once_with('some_password_command retrieving secrets', shell=True)

#!/usr/bin/env python3

import argparse
import configparser
import logging
import os
import requests
import sys
import select

from whats_that_code.election import guess_language_all_methods as glam

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def exit_with_error(message):
    logger.error(f"Error: {message}\n")
    sys.exit(1)


def stdin_has_data():
    return select.select([sys.stdin], [], [], 0.0)[0] != []


def format_with_highlight(content, highlight):
    if not content.strip():
        exit_with_error("Error: Empty content provided")

    if highlight == "no":
        return content

    if highlight != "auto":
        return f"```{highlight}\n{content}\n```"

    return f"```{glam(content)}\n{content}\n```"


class ConfigManager:
    def __init__(self, config):
        self.config_file = os.path.expanduser(config)
        self.config = configparser.ConfigParser()

        if os.path.exists(self.config_file):
            self.load_config()

    def load_config(self):
        self.config.read(self.config_file)

    def get_instance(self, instance_name="default"):
        if instance_name not in self.config:
            return {"server_url": "", "token": "", "auto_highlight": False}

        instance = self.config[instance_name]

        return {
            "server_url": instance.get("server_url", ""),
            "token": instance.get("token", ""),
            "auto_highlight": instance.getboolean("auto_highlight", False)
        }


class MattermostClient:
    def __init__(self, server_url, token):
        if not server_url or not token:
            exit_with_error("server_url and token are required")

        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.token = token
        self.server_url = server_url.rstrip('/')
        self.my_teams = self._get_my_teams()

    def _request(self, method, endpoint, data=''):
        url = f"{self.server_url}/api/v4/{endpoint}"
        response = requests.request(method=method, url=url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json() if response.content else {}

    def _get(self, endpoint):
        return self._request("GET", endpoint)

    def _post(self, endpoint, data):
        return self._request("POST", endpoint, data)

    def _get_my_teams(self):
        response = self._get("users/me/teams")
        return [{"id": t["id"], "name": t["name"]} for t in response]

    def _get_channels_for_team(self, team_id):
        response = self._get(f"users/me/teams/{team_id}/channels")
        return [{"id": c["id"], "name": c["display_name"], "team_id": team_id} for c in response]

    def list_channels(self):
        return [channel for team in self.my_teams for channel in self._get_channels_for_team(team["id"])]

    def list_users(self):
        response = self._get("users")
        return [{"id": u["id"], "name": u["username"]} for u in response]

    def get_channel_id(self, channel_name):
        channels = self.list_channels()

        for channel in channels:
            if channel["name"] == channel_name:
                return channel["id"], channel["team_id"]

    def get_user_id(self, username):
        users = self.list_users()

        for user in users:
            if user["name"] == username:
                return user["id"]

    def get_direct_channel(self, user_id):
        response = self._post("channels/direct", [user_id, self.get_my_user_id()])
        return response["id"], ""

    def get_my_user_id(self):
        response = self._get("users/me")
        return response["id"]

    def upload_file(self, channel_id, filepath):
        with open(filepath, 'rb') as f:
            files = {'files': (os.path.basename(filepath), f, 'application/octet-stream')}
            url = f"{self.server_url}/api/v4/files"

            response = requests.post(url, headers={'Authorization': f'Bearer {self.token}'}, files=files, data={'channel_id': channel_id})
            response.raise_for_status()

            return response.json()

    def send_message(self, channel_id, team_id, message, file_ids):
        data = {'channel_id': channel_id, 'message': message, 'team_id': team_id}

        if file_ids:
            data['file_ids'] = file_ids

        self._post("posts", data)


def main():
    parser = argparse.ArgumentParser(description='Send or pipe messages to Mattermost')
    parser.add_argument('--config', default='~/.mm-pipe.conf', help='Path to config file (default: ~/.mm-pipe.conf)')
    parser.add_argument('--instance', default='default', help='Configuration instance to use')
    parser.add_argument('--server-url', help='Mattermost server URL (overrides config)')
    parser.add_argument('--token', help='Mattermost access token (overrides config)')
    parser.add_argument('--user', '-u', help='User to send direct message to')
    parser.add_argument('--channel', '-c', help='Channel to send message to')
    parser.add_argument('--list-users', action='store_true', help='List available users')
    parser.add_argument('--list-channels', action='store_true', help='List available channels')
    parser.add_argument('--file', '-f', help='Send content of this file')
    parser.add_argument('--message', '-m', nargs='?', default='', help='Message to send (in quotes)')
    parser.add_argument('--highlight', default='auto', nargs='?', const=True, help='Force syntax highlighting with optional language (e.g. --highlight auto|no or -hl python|js etc.)')
    parser.add_argument('--zsh', action='store_true', help='Output zsh completion script')
    parser.add_argument('--bash', action='store_true', help='Output bash completion script')
    args = parser.parse_args()

    completions_dir = os.path.abspath(os.path.join(__file__, "..", "completions"))
    if args.zsh:
        print(f"fpath+={completions_dir}")
        print(f"source {completions_dir}/mm-pipe.fzf.zsh")
        print("autoload -Uz compinit")
        print("compinit")
        return

    if args.bash:
        print(f"source {completions_dir}/mm-pipe.completion.bash")
        print(f"source {completions_dir}/mm-pipe.fzf.bash")
        return

    config_manager = ConfigManager(args.config)
    instance = config_manager.get_instance(args.instance)

    server_url = args.server_url or instance['server_url'] or os.environ.get('MM_SERVER_URL')
    token = args.token or instance['token'] or os.environ.get('MM_TOKEN')

    client = MattermostClient(server_url, token)

    if args.list_channels or args.list_users:
        if args.list_users:
            print('\n'.join([u["name"] for u in client.list_users() if u["name"]]))
        if args.list_channels:
            print('\n'.join([c["name"] for c in client.list_channels() if c["name"]]))
        return

    if not args.channel and not args.user:
        exit_with_error("Either --channel or --user is required")
    if args.channel and args.user:
        exit_with_error("Cannot specify both --channel and --user")

    channels = client.get_channel_id(args.channel)
    users = client.get_direct_channel(client.get_user_id(args.user))
    channel_id, team_id = channels or users

    if not channel_id:
        exit_with_error('No channel/user found.')

    file_ids = []
    if args.file:
        file_response = client.upload_file(channel_id, args.file)
        file_ids = [file_response['file_infos'][0]['id']]

    message = args.message

    if stdin_has_data():
        content = sys.stdin.read()
        if content:
            highlight = args.highlight
            message += "\n"
            message += format_with_highlight(content, highlight) if highlight != "no" else content

    client.send_message(channel_id, team_id, message, file_ids if file_ids else None)


if __name__ == '__main__':
    main()

# mm-pipe

**mm-pipe** is a command-line tool designed to facilitate seamless interactions with a Mattermost instance. It enables users to send messages, share files, and perform various operations directly from the terminal.

## Features

- **Send Messages**: Pipe text directly to specific users or channels.
- **File Sharing**: Upload and share files effortlessly.
- **Syntax Highlighting**: Automatically apply syntax highlighting to code snippets.
- **Flexible Configuration**: Supports multiple methods for setting server URL and API token.
- **User and Channel Listing**: Retrieve and display lists of users and channels.
- **Instance Selection**: Access different configurations using the `--instance` parameter.

## Installation

To install mm-pipe, clone the repository, install the required dependencies, and the package too

```bash
git clone https://github.com/ysf/mm-pipe.git
cd mm-pipe
pip install .
```

add this if you want to debug/fix/add a feature to allow tests to work:
```bash
pip install ".[dev]"
```

If you have a working python setup, after the installation, `mm-pipe` should be available in your cli. I suggest creating a config file with your personal token and using the autocompletion features for bash/zsh and fzf next.

## Configuration

mm-pipe requires the server URL and an API token to connect to your Mattermost instance.

### Obtaining a Personal Access Token

To use mm-pipe, you'll need a personal access token from your Mattermost account:

1. **Enable Personal Access Tokens:**
   - As a System Admin, navigate to **System Console > Integrations > Integration Management**.
   - Ensure that **Enable Personal Access Tokens** is set to `true`.

2. **Generate a Token:**
   - Log in to your Mattermost account.
   - Go to **Account Settings > Security > Personal Access Tokens**.
   - Click **Create Token**, provide a description, and save it.
   - Copy the generated token and store it securely; you won't be able to view it again.

For detailed instructions, refer to the [Mattermost Personal Access Tokens documentation](https://developers.mattermost.com/integrate/reference/personal-access-token/).

Now that you have a token, mm-pipe can be configured in several ways:

### 1. Configuration File (Recommended)

Create a default configuration file at `~/.mm-pipe.conf`:

```ini
[default]
server_url=https://mattermost.yoururl.com
token=<yourtokenhere>
auto_highlight=True
```

Replace `https://mattermost.yoururl.com` with your Mattermost server URL and `<yourtokenhere>` with your personal access token.

**Using Multiple Instances:**

To manage multiple configurations, define them under different sections in the configuration file:

```ini
[default]
server_url=https://mattermost.default.com
token=<defaulttoken>

[work]
server_url=https://mattermost.work.com
token=<worktoken>

[friends]
server_url=https://mattermost.friends.com
token=<personaltoken>
```

You can specify which instance to use with the `--instance` parameter:

```bash
echo "Your message" | mm-pipe --instance work --user username
```

**Using a Custom Configuration File:**

If you prefer to use a different location for the configuration file, specify its path with the `--config` parameter:

```bash
mm-pipe --config /path/to/your/config.conf
```

### 2. Environment variables

Set the following environment variables:

```bash
export MM_PIPE_SERVER_URL=https://mattermost.yoururl.com
export MM_PIPE_TOKEN=<yourtokenhere>
```

### 3. Command-Line arguments

Provide the server URL and token directly when running mm-pipe:

```bash
echo "Your message" | mm-pipe --server https://mattermost.yoururl.com --token <yourtokenhere> --user username
```

## Usage

Here are some common use cases for mm-pipe:

### Send a message to a user

```bash
mm-pipe --user username --message "hey there."
# or
echo "Hello, this is a test message." | mm-pipe --user username
```

### Send a message to a channel

```bash
echo "System maintenance will occur at midnight." | mm-pipe --channel channelname
```

### Send a file to a user

```bash
mm-pipe --user username --file /path/to/yourfile.txt
```

### The optional message parameter will be put in front of everything:
```bash
echo "System maintenance will occur at midnight." | mm-pipe --channel channelname -m "## IMPORTANT"
```

### Send a code snippet with syntax highlighting

```bash
cat script.py | mm-pipe --channel devs --highlight python
```

### List all users or channels

To see if your mm-pipe setup works, you can list the users/channels on your provided default instance. This feature is used for the autocompletion on --user or fzf-completion via CTRL+N, but might still be useful for a different workflow.

```bash
mm-pipe --list-users
# or
mm-pipe --list-channels
```

## Command-Line Options

- `--help`: Shows commandline help.
- `--server-url`: Mattermost server URL.
- `--token`: Personal access token.
- `--instance`: Specify the configuration instance to use.
- `--config`: Path to a custom configuration file.
- `--user`: Specify the recipient username.
- `--channel`: Specify the target channel.
- `--file`: Path to the file to send.
- `--message`: Directly specify a message.
- `--highlight`: Apply syntax highlighting (e.g.,`auto`, `python`, `javascript`).
- `--list-users`: Display a list of all users.
- `--list-channels`: Display a list of all channels.
- `--bash`: Output bash completion to source with `source <(mm-pipe --bash)`
- `--zsh`: Output zsh completion to source with `source <(mm-pipe --zsh)`

## Autocompletion

mm-pipe supports autocompletion for zsh shells.

### Bash

After installing mm-pipe, add the following to your `~/.bashrc`:

```bash
export MM_PIPE_USE_FZF=1
# export MM_PIPE_KEYBIND="\\C-n" # CTRL+N is default

source <(mm-pipe --bash)
```

### Zsh

Add the following to your `~/.zshrc`:

```zsh
export MM_PIPE_USE_FZF=1
# export MM_PIPE_KEYBIND="^N" # CTRL+N is default
source <(mm-pipe --zsh)
```

## Aliases

If you're regurlarly copy and pasting something to a specific Mattermost target. Using an alias might help:

```bash
# you put this to your aliases
alias devs="mm-pipe --instance work --channel devs -m"
alias bestfriend="mm-pipe --instance friends --user bestfriend -m"

# and later in your shell, will
$ ps aux | grep http | devs
$ bestfriend "time for lunch?"


The tabcompletion on `--instance` will show the instances found in your `~/.mm-pipe.conf` file. On --user and --channel it will show/complete valid users and channels. The fzf completion on CTRL+N will add `| mm-pipe --user username` to the current commandline. This allows sending command outputs directly to mattermost. If the commandline is empty, hence no command has been entered yet, CTRL+N assumes you want to send a message and `mm-pipe --user username -m ""` will be entered into the prompt, with the cursor waiting between the quotes for your message.


## License

This project is licensed under the MIT License.

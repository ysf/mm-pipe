#compdef mm-pipe

function _mm_pipe {

    _comp_helper() {
        local name cmd list selected
        name="$1"
        shift
        cmd=("$@")
        IFS=$'\n' list=($($cmd 2>/dev/null | sort))
        if (( ${#list[@]} )); then
            if [[ -n ${commands[fzf]} && ${MM_PIPE_USE_FZF:-0} -eq 1 ]]; then
                selected=$(printf '%s\n' "${list[@]}" | fzf-tmux -i --height=~30% --reverse)
                if [[ -n $selected ]]; then
                    compadd -U -S ' ' -- "$selected"
                fi
            else
                compadd -o nosort -S ' ' -Q -- "${(q)list[@]}"
            fi
            return 0
        fi
        return 1
    }

    local curcontext="$curcontext" state
    typeset -A opt_args

    _arguments -C \
        '--instance[Specify the configuration instance]:instance:->instances' \
        '--channel[Specify the channel to interact with]:channel:->channels' \
        '--file[Specify the file to send]:file:_files' \
        '--highlight[Specify syntax highlight]:highlight:(auto language no)' \
        '--message[Specify the message to send]:message' \
        '--user[Specify the user to interact with]:user:->users' \
        '--config[Specify the config file]:config:_files' \
        '--server-url[Specify the Mattermost server URL]:server_url' \
        '--token[Specify the Mattermost access token]:token' \
        '--zsh[Generate Zsh completion script]' \
        '--help[Show help message]' \
        '--list-channels[List available channels]' \
        '--list-users[List available users]'

    local config_file="${opt_args[--config]:-${HOME}/.mm-pipe.conf}"
    local instance="${opt_args[--instance]}"
    [[ -z "$instance" || "$instance" == "default" ]] && instance_arg="" || instance_arg="--instance $instance"

    case $state in
        instances)
            if [[ -r $config_file ]]; then
                local instances=(${(f)"$(grep '^\[' "$config_file" | tr -d '[]')"})
                (( ${#instances[@]} )) && compadd -V instances -a instances
            fi
            ;;
        channels)
            _comp_helper "channels" "mm-pipe" "$instance_arg" "--list-channels"
            ;;
        users)
            _comp_helper "users" "mm-pipe" "$instance_arg" "--list-users"
            ;;
    esac
}

_mm_pipe "$@"

# mm-pipe fzf helper for bash + zsh

_mm_pipe_fzf_core() {
    local color_user="\033[34m"
    local color_channel="\033[32m"
    local ansi_reset="\033[0m"
    local selection type colored name users channels

    users=$(mm-pipe --list-users | awk -v cu="$color_user" -v r="$ansi_reset" '{printf("user\t%s%s%s\t%s\n", cu, $0, r, $0)}')
    channels=$(mm-pipe --list-channels | awk -v cc="$color_channel" -v r="$ansi_reset" '{printf("channel\t%s%s%s\t%s\n", cc, $0, r, $0)}')

    [[ -z "$users" && -z "$channels" ]] && return 1

    selection=$( (echo "$users"; echo "$channels") | fzf-tmux --ansi --delimiter='\t' --height=~30% --prompt="User/Channel: " --with-nth=2 )

    [[ -z "$selection" ]] && return 1

    IFS=$'\t' read -r type colored name <<< "$selection"

    if [ "$type" = "user" ]; then
        echo "--user $(printf '%q' "$name")"
    elif [ "$type" = "channel" ]; then
        echo "--channel $(printf '%q' "$name")"
    else
        return 1
    fi
}

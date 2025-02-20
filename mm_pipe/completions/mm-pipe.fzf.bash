if [ "${MM_PIPE_USE_FZF:-0}" -eq 1 ] && command -v fzf > /dev/null; then
    source "$(dirname "${BASH_SOURCE[0]}")/mm-pipe.fzf.sh"
    shopt -s extglob

    _mm_pipe_fzf() {
        local suffix
        suffix=$(_mm_pipe_fzf_core)
        [[ -z "$suffix" ]] && return 1

        if [[ -z "$READLINE_LINE" ]]; then
            READLINE_LINE="mm-pipe $suffix -m \"\""
            READLINE_POINT=$(( ${#READLINE_LINE} - 1 ))
        else
            READLINE_LINE+=" | mm-pipe $suffix"
            READLINE_POINT=${#READLINE_LINE}
        fi
    }

    : ${MM_PIPE_KEYBIND:="\\C-n"}
    bind -x '"'"$MM_PIPE_KEYBIND"'": _mm_pipe_fzf'
fi

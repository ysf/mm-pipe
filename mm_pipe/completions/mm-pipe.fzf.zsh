if [ "${MM_PIPE_USE_FZF:-0}" -eq 1 ] && command -v fzf > /dev/null; then
    source "$(dirname "${(%):-%x}")/mm-pipe.fzf.sh"
    autoload -Uz add-zsh-hook

    _mm_pipe_fzf() {
        local suffix
        suffix=$(_mm_pipe_fzf_core)
        [[ -z "$suffix" ]] && return 1

        if [[ -z "$LBUFFER" ]]; then
            LBUFFER="mm-pipe $suffix -m \"\""
            CURSOR=$(( ${#LBUFFER} - 1 ))
        else
            LBUFFER+=" | mm-pipe $suffix"
        fi
        zle reset-prompt
    }

    zle -N _mm_pipe_fzf
    : ${MM_PIPE_KEYBIND:="^N"}
    bindkey "$MM_PIPE_KEYBIND" _mm_pipe_fzf
fi

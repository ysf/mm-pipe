_mm_pipe() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    opts="--instance --channel --file --highlight --message --user --config --server-url --token --help --list-channels --list-users --zsh --bash"

    case "${prev}" in
        --instance)
            local config_file="${HOME}/.mm-pipe.conf"
            if [[ -r "${config_file}" ]]; then
                local instances=$(grep '^\[' "${config_file}" | tr -d '[]')
                COMPREPLY=( $(compgen -W "${instances}" -- ${cur}) )
            fi
            return 0
            ;;
        --highlight)
            COMPREPLY=( $(compgen -W "auto language no" -- ${cur}) )
            return 0
            ;;
        --file|--config)
            COMPREPLY=( $(compgen -f -- ${cur}) )
            return 0
            ;;
        --channel|--user)
            local instance=""
            for ((i=1; i < ${#COMP_WORDS[@]}; i++)); do
                if [[ "${COMP_WORDS[i-1]}" == "--instance" ]]; then
                    instance="--instance ${COMP_WORDS[i]}"
                    break
                fi
            done
            local IFS=$'\n'
            local list_type="--list-${prev#--}"
            local items=($(mm-pipe ${instance} ${list_type}s 2>/dev/null))
            local i
            for i in "${!items[@]}"; do
                if [[ "${items[i]}" == "${cur}"* ]]; then
                    COMPREPLY+=("$(printf '%q' "${items[i]}")")
                fi
            done
            return 0
            ;;
      mm-pipe)
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
            ;;
        *)
            if [[ ${cur} == -* ]] || [[ ${COMP_CWORD} -eq 1 ]]; then
                COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                return 0
            fi
            ;;
    esac
}

complete -F _mm_pipe mm-pipe

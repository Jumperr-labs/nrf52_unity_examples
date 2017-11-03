#!/usr/bin/env bash

set -e

POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"

    case $key in
        generate)
            COMMAND=generate
            shift
            ;;
        *)    # unknown option
        POSITIONAL+=("$1") # save it in an array for later
        shift # past argument
        ;;
    esac
done

#set -- "${POSITIONAL[@]}" # restore positional parameters

if [ "${COMMAND}" == "generate" ]; then
    cd "$(pwd)/../../../../../../"
    if [ ! -d "venv" ]; then
        virtualenv venv
        source venv/bin/activate
        pip install -r requirements.txt
        deactivate
    fi
    cd "$(pwd)"
fi

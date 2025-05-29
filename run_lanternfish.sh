#!/bin/bash

# Initialize variables
model=""
new_args=()

# Process arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--model)
            if [[ $# -gt 1 ]]; then
                model="$2"
                shift 2  # Skip both -m/--model and its value
            else
                # If -m/--model is last argument, pass it through for Python to handle the error
                new_args+=("$1")
                shift
            fi
            ;;
        *)
            new_args+=("$1")
            shift
            ;;
    esac
done

# Set ENV_MODEL_NAME if model was found
if [ -n "$model" ]; then
    export CLI_MODEL_NAME="$model"
fi

uv run --env-file .env_ollama lanternfish/__main__.py "${new_args[@]}"

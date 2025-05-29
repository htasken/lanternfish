#!/bin/bash

# Function to display help
show_help() {
    cat << EOF
Usage: $0 -p|--prompt <prompt words...> [-m|--model <model_name>] [-h|--help]

This script runs the lanternfish LLM client with the specified prompt and optional model.

Options:
  -p, --prompt <words...>    Specify the prompt (required). Can be multiple words.
  -m, --model <model_name>   Specify the model name (optional). Sets ENV_MODEL_NAME.
  -h, --help                 Display this help message and exit.

Examples:
  # Basic usage with a prompt
  $0 -p "How are potatoes affected by climate change?"

  # Using long form options
  $0 --prompt "How are potatoes affected by climate change?"

  # With a model specified
  $0 -p "How are potatoes affected by climate change?" -m gpt-4

  # Model can come before prompt
  $0 -m gemma3:4b -p "How are potatoes affected by climate change?"

  # Multi-word prompt without quotes
  $0 -p How are potatoes affected by climate change?
EOF
}

# Initialize variables
prompt=""
model=""

# Check if no arguments provided
if [[ $# -eq 0 ]]; then
    show_help
    exit 1
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--prompt)
            shift
            # Collect all arguments until we hit another flag or end of arguments
            while [[ $# -gt 0 && ! "$1" =~ ^- ]]; do
                if [ -z "$prompt" ]; then
                    prompt="$1"
                else
                    prompt="$prompt $1"
                fi
                shift
            done
            ;;
        -m|--model)
            if [[ $# -lt 2 ]]; then
                echo "Error: -m|--model requires an argument"
                echo
                show_help
                exit 1
            fi
            model="$2"
            shift 2
            ;;
        *)
            echo "Error: Unknown option: $1"
            echo
            show_help
            exit 1
            ;;
    esac
done

# Check if prompt was provided
if [ -z "$prompt" ]; then
    echo "Error: Prompt is required"
    echo
    show_help
    exit 1
fi

# Set ENV_MODEL_NAME if model was specified
if [ -n "$model" ]; then
    export CLI_MODEL_NAME="$model"
fi

# Execute the command
uv run --env-file .env_ollama lanternfish/__main__.py -p "$prompt"

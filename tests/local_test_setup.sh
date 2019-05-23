# Usage: source local_test_setup.sh [test file to run]

export PYTHONPATH="$(git rev-parse --show-toplevel)"

if [[ -n "$1" ]]; then
    # To test tab completion
    export PATH=$PATH:$(dirname "$1")
    eval "$(register-python-argcomplete "$1")"
    chmod +x "$1"
fi

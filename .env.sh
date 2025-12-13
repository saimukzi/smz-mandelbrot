# get absolute path of the directory containing this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source system bashrc for colors and settings
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

source "$DIR/.venv/bin/activate"

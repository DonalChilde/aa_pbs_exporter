#!/usr/bin/env bash

# This script is based on: https://github.com/adriancooney/Taskfile

# TODO move to snippets, add snippet header
# update curl instructions
# curl -O https://raw.githubusercontent.com/DonalChilde/dev-tool/main/scripts/dev-tool.sh
# or
# curl --create-dirs -O --output-dir ./scripts https://raw.githubusercontent.com/DonalChilde/dev-tool/main/scripts/dev-tool.sh

# General usage is ./scripts/task.sh do <arguments>
# Usage instructions ./scripts/task.sh help

# Setup Instructions
#
# 1. in the `do` function, choose with or without confirmation
# 2. in the `_do_with*` function provide custom logic and messaging
# 3. in the `help` function, provide usage instructions

# -e Exit immediately if a pipeline returns a non-zero status.
# -u Treat unset variables and parameters other than the special parameters ‘@’ or ‘*’ as an error when performing parameter expansion.
# -o pipefail If set, the return value of a pipeline is the value of the last (rightmost) command to exit with a non-zero status, or zero if all commands in the pipeline exit successfully.
set -euo pipefail

# For use inside functions
# The name of the script
SCRIPT=$0
# The script command line arguments
ARGS=("$@")

function do() {
    _do_with_confirmation
    # _do_without_confirmation
}

function _do_without_confirmation() {
    _argument_check

    # Name your arguments
    path=$(realpath ${ARGS[1]})

    # Define your actions
    ACTION_1="echo 'Action_1'"
    ACTION_2="echo 'Action_2'"
    ACTION_3="ls -la $path"

    # Action messages
    printf "\nRunning the following commands:"
    echo
    printf "\n\t$ACTION_1"
    printf "\n\t$ACTION_2"
    printf "\n\t$ACTION_3"

    # For spacing
    echo
    echo

    # Do the Actions
    eval $ACTION_1
    eval $ACTION_2
    eval $ACTION_3
}
function _do_with_confirmation() {
    _argument_check

    # Name your arguments
    path=$(realpath ${ARGS[1]})

    # Define your actions
    ACTION_1="if [ -d '$path/.venv' ]; then rm -rf '$path/.venv'; fi"
    ACTION_2="python3 -m virtualenv '$path/.venv'"
    ACTION_3="source '$path/.venv/bin/activate'"
    ACTION_4="export PIP_REQUIRE_VIRTUALENV=true"
    ACTION_5="pip3 install -U pip"
    ACTION_6="pip3 install -e .[dev,lint,doc,vscode,testing]"

    # Action messages
    printf "\nThis will run the following commands:"
    echo
    printf "\n\t$ACTION_1"
    printf "\n\t$ACTION_2"
    printf "\n\t$ACTION_3"
    printf "\n\t$ACTION_4"
    printf "\n\t$ACTION_5"
    printf "\n\t$ACTION_6"
    # printf "\n\t$ACTION_3"

    # For spacing
    echo
    echo

    # # Delay message
    # printf "Take ten seconds to be sure:"
    # echo
    # _countdown 10
    # echo

    # Confirmation dialog
    # https://stackoverflow.com/a/1885534/105844
    read -p "-----Are you sure? (Y/N)-----" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Do the Actions
        eval $ACTION_1
        eval $ACTION_2
        eval $ACTION_3
        eval $ACTION_4
        eval $ACTION_5
        eval $ACTION_6
    else
        echo "Action Declined"
        exit 1
    fi
}
function _argument_check() {
    # check for the presence of an argument, but not validity. Output help if missing.
    # Arguments start at 1, 0 is the `do` command.
    : ${ARGS[1]?"Missing a required command line argument. run '$SCRIPT --help' for usage instructions."}
    # : ${ARGS[2]?"Missing a required command line argument. run '$SCRIPT help' for usage instructions."}
}
function --help() {

    HELPTEXT=$(
        cat <<END
    NAME
        $SCRIPT - Create a virtualenv in the project directory, and 
            install the project with editable flag.

    SYNOPSIS
        $SCRIPT do [DIRECTORY]
        $SCRIPT --help

    DESCRIPTION
        $SCRIPT is used to create a virtualenv in the project directory, and 
            install the project with editable flag. Will remove an existing .venv 
            directory if found. Runs the following commands:

                if [ -d '[DIRECTORY]/.venv' ]; then rm -rf '[DIRECTORY]/.venv'; fi
                python3 -m virtualenv '[DIRECTORY]/.venv'
                source '[DIRECTORY]/.venv/bin/activate'
                export PIP_REQUIRE_VIRTUALENV=true
                pip3 install -U pip
                pip3 install -e .[dev,lint,doc,vscode,testing]

        --help display this help and exit

    EXAMPLES:
        $SCRIPT do .
            Run the script passing in the current directory.

        $SCRIPT --help
            Output the usage instructions.

END
    )
    printf "$HELPTEXT"
    echo
}
function _countdown() {
    # https://superuser.com/questions/611538/is-there-a-way-to-display-a-countdown-or-stopwatch-timer-in-a-terminal
    # Display a countdown clock.
    # $1 = int seconds
    date1=$(($(date +%s) + $1))
    while [ "$date1" -ge $(date +%s) ]; do
        echo -ne "$(date -u --date @$(($date1 - $(date +%s))) +%H:%M:%S)\r"
        sleep 0.1
    done
}

# Runs the help function if no arguments given to script.
TIMEFORMAT=$'\nTask completed in %3lR'
time "${@:---help}"
################### No code below this line #####################

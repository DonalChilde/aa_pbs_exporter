#!/usr/bin/env bash

# This script is based on: https://github.com/adriancooney/Taskfile

# TODO move to snippets, add snippet header
# update curl instructions
# curl -O https://raw.githubusercontent.com/DonalChilde/dev-tool/main/scripts/dev-tool.sh
# or
# curl --create-dirs -O --output-dir ./scripts https://raw.githubusercontent.com/DonalChilde/dev-tool/main/scripts/dev-tool.sh

# General usage is ./scripts/task.sh do <arguments>
# Usage instructions ./scripts/task.sh --help

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
    ACTION_1="rm -fr $path/build/"
    ACTION_2="rm -fr $path/dist/"
    ACTION_3="rm -fr $path/.eggs/"
    ACTION_4="find $path -name '*.egg-info' -exec rm -fr {} +"
    ACTION_5="find $path -name '*.egg' -exec rm -f {} +"

    # Action messages
    printf "\nThis will run the following commands:"
    echo
    printf "\n\t$ACTION_1"
    printf "\n\t$ACTION_2"
    printf "\n\t$ACTION_3"
    printf "\n\t$ACTION_4"
    printf "\n\t$ACTION_5"

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
        $SCRIPT - Remove python package build artifacts

    SYNOPSIS
        $SCRIPT do [DIRECTORY]
        $SCRIPT --help

    DESCRIPTION
        $SCRIPT is used to remove python package build artifacts
        starting in DIRECTORY by running the following commands:

            rm -fr [DIRECTORY]/build/
            rm -fr [DIRECTORY]/dist/
            rm -fr [DIRECTORY]/.eggs/
            find [DIRECTORY] -name '*.egg-info' -exec rm -fr {} +
            find [DIRECTORY] -name '*.egg' -exec rm -f {} +

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

# # -e Exit immediately if a pipeline returns a non-zero status.
# # -u Treat unset variables and parameters other than the special parameters ‘@’ or ‘*’ as an error when performing parameter expansion.
# # -o pipefail If set, the return value of a pipeline is the value of the last (rightmost) command to exit with a non-zero status, or zero if all commands in the pipeline exit successfully.
# set -euo pipefail

# : ${1?"Usage: $0 <path to directory>"}
# path=$(realpath $1)

# printf "\nThis will run the following commands:"
# printf "\n\t'rm -fr $path/build/'"
# printf "\n\t'rm -fr $path/dist/'"
# printf "\n\t'rm -fr $path/.eggs/'"
# printf "\n\t'find $path -name '*.egg-info' -exec rm -fr {} +'"
# printf "\n\t'find $path -name '*.egg' -exec rm -f {} +'"
# printf "\n\n"
# read -p "-----Are you sure? (Y/N)-----" -n 1 -r
# echo
# if [[ $REPLY =~ ^[Yy]$ ]]; then
#     rm -fr $path/build/
#     rm -fr $path/dist/
#     rm -fr $path/.eggs/
#     find $path -name '*.egg-info' -exec rm -fr {} +
#     find $path -name '*.egg' -exec rm -f {} +
# else
#     echo "Action Declined"
#     # exit 1
# fi
# sleep 2
# function help() {
#     echo
# }
# # This idea is heavily inspired by: https://github.com/adriancooney/Taskfile
# # Runs the help function if no arguments given to script.
# TIMEFORMAT=$'\nTask completed in %3lR'
# time "${@:-help}"
# # time "${@:-help}"
# ################### No code below this line #####################

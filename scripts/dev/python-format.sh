#!/usr/bin/env bash

# This script is based on: https://github.com/adriancooney/Taskfile
# HOME: https://github.com/DonalChilde/bash-task

# This template mimics a cli program, with --help and dry-run display.
# It makes it easy to define a list of commands to run,
# with optional parameters from the command line.
# Confirmation before execution with optional
# delay before execution is also available.

# General usage is ./scripts/task.sh do <arguments>
# For a dry-run ./scripts/task.sh dry-run <arguments>
# Usage instructions ./scripts/task.sh --help

########################################
########## Setup Instructions ##########
########################################

# 1. Set script configuration variables.
# 2. Set custom script variables.
# 3. Edit custom script functions.
# 4. Set --help configuration variables.

##########################################
########## Script configuration ##########
##########################################

# -e Exit immediately if a pipeline returns a non-zero status.
# -u Treat unset variables and parameters other than the special parameters ‘@’ or ‘*’ as an error when performing parameter expansion.
# -o pipefail If set, the return value of a pipeline is the value of the last (rightmost) command to exit with a non-zero status, or zero if all commands in the pipeline exit successfully.
set -euo pipefail

# The script command line arguments as an array
# Do not alter this variable
ARGS=("$@")

# echo commands before eval
ECHO_COMMANDS=1 # true
# ECHO_COMMANDS=0 # false

# confirm execution of commands before eval
EXECUTION_CONFIRMATION=1 # true
# EXECUTION_CONFIRMATION=0 # false

# Seconds to delay execution. Used in conjunction with EXECUTION_CONFIRMATION
DELAY=3

######################################
########## Custom variables ##########
######################################

# None

##########################################
########## --help configuration ##########
##########################################

# The name of the script
SCRIPT=$(basename $0)

# A one line description.
SHORT_DESCRIPTION="Format Python code files."

# A Multiline description of the script.
LONG_DESCRIPTION=$(
    cat <<END
With python code files, sort the imports with isort and format using black.
            If no arguments given for paths, './src ./tests' will be used.
END
)

# CLI arguments expected, used in the --help output
# CLI_ARGS="PATH_IN PATH_OUT"
CLI_ARGS="PATH_ONE PATH_TWO 'Path three'"

#############################################
########## custom script functions ##########
#############################################

function _define_commands() {
    # Define the commands used in this script.
    # Variables used in these commands are expected to be defined
    #   - in the script settings above, and/or
    #   - in the `_define_variables` function for actual use, and
    #   - in the `_define_placeholder_variables` function for --help display.

    for i in "${CODE_PATHS[@]}"; do
        COMMANDS+=("./.venv/bin/isort '$i'" "./.venv/bin/black '$i'")
    done
}

function _define_placeholder_variables() {
    # Define the command variables to be used in the --help output.
    # These are variables that are normaly defined from cli arguments,
    # not ones that are already defined in the script settings.

    CODE_PATHS=(PATH_ONE PATH_TWO 'Path three')
    # PATH_OUT="PATH_OUT
}

function _define_variables() {
    # Turn arguments from the command line into variables for use in _define_commands
    # This function is called for `do` and `dry-run` but not `--help`.
    # Variables defined here are not visible during --help display.

    # Check for cli arguments in excess of action command - ie. `do` or `dry-run`
    EXCESS_ARGS=("${ARGS[@]:1}")
    if [ ${#EXCESS_ARGS[@]} -eq 0 ]; then
        # Set default arguments for CODE_PATHS
        CODE_PATHS=(./src ./tests)
    else
        CODE_PATHS=(${EXCESS_ARGS[@]})
    fi
}

function _confirmation_message() {
    # Edit this function for a custom confirmation message.
    echo "This will run the following commands:"
    echo
    _dry-run
    echo
    echo "Have you saved all open/dirty code files?"
}

##########################################
########## NOT USUALLY MODIFIED ##########
##########################################

function do() {
    if [ $EXECUTION_CONFIRMATION -eq 1 ]; then
        _confirmation_message
        _confirmation_delay
        _confirmation_dialog
    fi
    _run_commands
}

function _confirmation_dialog() {
    # Confirmation dialog
    # https://stackoverflow.com/a/1885534/105844
    read -p "-----Are you sure? (Y/N)-----" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        :
    else
        echo "Commands Declined"
        exit 1
    fi
}

function _confirmation_delay() {
    if [ $DELAY -gt 0 ]; then
        echo "Take $DELAY seconds to be sure:"
        echo
        _countdown $DELAY
        echo
    fi
}

function _run_commands() {
    _define_variables
    _define_commands

    for i in "${COMMANDS[@]}"; do
        if [ $ECHO_COMMANDS -eq 1 ]; then
            echo "$i"
        fi
        eval "$i"
    done
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

function dry-run() {
    echo "Dry run for $SCRIPT"
    echo
    echo "These are the commands that would be executed."
    echo
    _dry-run
}

function _dry-run() {
    _define_variables
    _define_commands
    for i in "${COMMANDS[@]}"; do
        echo "$i"
    done
}

function --help() {
    _define_placeholder_variables
    _define_commands

    HELPTEXT=$(
        cat <<END
    NAME
        $SCRIPT - $SHORT_DESCRIPTION

    SYNOPSIS
        $SCRIPT do $CLI_ARGS
        $SCRIPT dry-run $CLI_ARGS
        $SCRIPT --help

    DESCRIPTION
        $LONG_DESCRIPTION

    EXAMPLES:
        $SCRIPT do $CLI_ARGS
            Do the script.

        $SCRIPT dry-run $CLI_ARGS
            Display the commands that would be run.

        $SCRIPT --help
            Output the usage instructions.

    COMMANDS:

END
    )
    printf "$HELPTEXT"
    echo
    for i in "${COMMANDS[@]}"; do
        printf "\n\t$i"
    done
    echo
}

function _command_check() {
    if [ "${ARGS[0]}" = "do" ]; then
        :
    elif [ "${ARGS[0]}" = "dry-run" ]; then
        :
    elif [ "${ARGS[0]}" = "--help" ]; then
        :
    else
        echo "The first script argument must be one of ['do', 'dry-run', '--help']."
        echo "Received '${ARGS[0]}'"
        echo "Use '$SCRIPT --help' for usage instructions."
        exit 1
    fi
}

_command_check
# Runs the help function if no arguments given to script.
TIMEFORMAT=$'\nTask completed in %3lR'
time "${@:---help}"
#################################################################
################### No code below this line #####################
#################################################################

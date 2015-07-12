#!/usr/bin/env bash

# EXIT CODES
#  0 - should have worked
#  1 -
#  2 - Yum clean failed
#  4 - Yum list updates failed
#  8 - Yum update failed

# Thanks
## bbbco - http://stackoverflow.com/questions/5719030/bash-silently-kill-background-function-process

# Bugs
## Output from yum list does not show packages installed due to dependencies or packages removed.

# Print Help
patchhelp () 
{ 
    echo "Usage: $0 [options]... [package]...";
    echo "options:";
    echo " -b  print <br> tags, useful for html outputs";
    echo " -r  reboot"
}

# Print output, adding <br> if output is on web page
patchprint () 
{ 
    if [[ $HTML -eq 1 ]]; then
        echo "$@" | sed 's/$/<br>/gm';
    else
        echo "$@";
    fi
}

# Print a progress bar.  Helps keep ssh sessions from timing out
startprogress () 
{ 
    unit="${1:-.}";
    delay="${2:-1}";
    while :; do
        echo -n "$unit";
        sleep "$delay";
    done
}

# Stop printing progess bar
stopprogress () 
{ 
    kill -9 "$1" 2> /dev/null;
    wait "$1" 2> /dev/null
}

# Yum clean
yumclean () 
{ 
    local RETVAL=0;
    echo -n "Cleaning: ";
    startprogress "c" & pid=$!;
    trap "stopprogress $pid; exit" INT TERM EXIT;
    YUMCLEAN=$(yum --quiet clean all 2>&1);
    RETVAL=$?;
    stopprogress $pid;
    patchprint;
    trap - INT TERM EXIT;
    return $RETVAL
}

# Yum list
yumlist () 
{ 
    local RETVAL=0;
    echo -n "Listing: ";
    startprogress "l" & pid=$!;
    trap "stopprogress $pid; exit" INT TERM EXIT;
    YUMLIST=$(yum --quiet list updates $@ 2>&1);
    RETVAL=$?;
    stopprogress $pid;
    patchprint;
    trap - INT TERM EXIT;
    return $RETVAL
}

# Yum update
yumupdate () 
{ 
    local RETVAL=0;
    echo -n "Updating: ";
    startprogress "u" & pid=$!;
    trap "stopprogress $pid; exit" INT TERM EXIT;
    YUMUPDATE=$(yum -y --quiet update $@ 2>&1);
    RETVAL=$?;
    stopprogress $pid;
    patchprint;
    trap - INT TERM EXIT;
    return $RETVAL
}

# Yum patch process
patchyum () 
{ 
    set -o pipefail;
    if yumclean; then
        if yumlist "$@"; then
            if yumupdate "$@"; then
                if [[ "$YUMLIST" != "" ]]; then
                    patchprint "$YUMLIST";
                else
                    patchprint "No updates available";
                fi;
                patchprint "yum update complete";
                if [[ $REBOOT -eq 0 ]]; then
                    patchprint "OKAY";
                fi;
            else
                patchprint "$YUMUPDATE";
                patchprint "yum update failed";
                patchprint "FAILED";
                RETVAL=$((RETVAL+8));
            fi;
        else
            patchprint "$YUMLIST";
            patchprint "yum list updates $@ failed";
            patchprint "FAILED";
            RETVAL=$((RETVAL+4));
        fi;
    else
        patchprint "$YUMCLEAN";
        patchprint "yum clean failed";
        patchprint "FAILED";
        RETVAL=$((RETVAL+2));
    fi
}

function patchup2date ()
{
    if UP2DATE=$(up2date -u 2>&1); then
        patchprint "$UP2DATE";
        patchprint "up2date -u complete";
        patchprint "OKAY";
    else
        patchprint "$UP2DATE";
        patchprint "up2date -u failed";
        patchprint "FAILED";
        RETVAL=$((RETVAL+8));
    fi
}

# Detect if old, up2date, is used
function detectup2date ()
{
    if $(which up2date >/dev/null 2>&1); then
        return 0;
    fi;
    return 1
}

function main ()
{
    if detectup2date; then
        patchup2date "$@";
    else
        patchyum "$@";
    fi;
    if [[ $REBOOT -eq 1 && $RETVAL -eq 0 ]]; then
        patchprint "Rebooting...";
        patchprint "OKAY";
        reboot;
    fi
}

YUMCLEAN="";
YUMLIST="";
YUMUPDATE="";

HTML=0;
REBOOT=0;
RETVAL=0;
while getopts ":br" opt; do
    case $opt in 
        b)
            HTML=1
        ;;
        r)
            REBOOT=1
        ;;
        \?)
            patchhelp;
            exit 1
        ;;
    esac;
done;
shift $((OPTIND - 1));
main "$@";
exit $RETVAL

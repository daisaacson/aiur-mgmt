#!/usr/bin/env bash

# EXIT CODES
#  0 - should have worked
#  1 -
#  2 - Yum clean failed
#  4 - Yum list updates failed
#  8 - Yum update failed

function aiurpatchhelp ()
{
  echo "Usage: $0 [options]... [package]...";
  echo "options:";
  echo " -b  print <br> tags";
  echo " -r  reboot";
}

function aiurpatchprint ()
{
  if [[ $HTML -eq 1 ]]; then
    echo "$@" | sed 's/$/<br>/gm';
  else
    echo "$@" 
  fi;
}

function aiurpatchyum ()
{
  set -o pipefail;
  # yum clean
  if YUMCLEAN=$(yum --quiet clean all 2>&1); then
    # yum list updates
    if YUMLIST=$(yum --quiet list updates $@ 2>&1); then
      # yum update
      if YUMUPDATE=$(yum -y --quiet update $@ 2>&1); then
        if [[ "$YUMLIST"  != "" ]]; then
          aiurpatchprint "$YUMLIST";
        else
          aiurpatchprint "No updates available";
        fi;
        aiurpatchprint "yum update complete";
        aiurpatchprint "OKAY"
      # yum update failed
      else
        aiurpatchprint "$YUMLIST"
        aiurpatchprint "$YUMUPDATE"
        aiurpatchprint "yum update failed";
        aiurpatchprint "FAILED"
        RETVAL=$((RETVAL+8));
      fi;
    # yum list updates failed
    else
      aiurpatchprint "$YUMLIST";
      aiurpatchprint "yum list updates $@ failed";
      aiurpatchprint "FAILED"
      RETVAL=$((RETVAL+4));
    fi;
  # yum clean failed
  else
    aiurpatchprint "$YUMCLEAN"
    aiurpatchprint "yum clean failed";
    aiurpatchprint "FAILED"
    RETVAL=$((RETVAL+2));
  fi
}

function aiurpatchup2date ()
{
  if UP2DATE=$(up2date -u 2>&1); then
    aiurpatchprint "$UP2DATE";
    aiurpatchprint "up2date -u complete"
    aiurpatchprint "OKAY";
  else
    aiurpatchprint "$UP2DATE";
    aiurpatchprint "up2date -u failed"
    aiurpatchprint "FAILED"
    RETVAL=$((RETVAL+8))
  fi
}

# Detect if old, up2date, is used
function detectup2date ()
{
  if $(which up2date >/dev/null 2>&1); then
    return 0;
  fi
  return 1;
}

function main ()
{
  if detectup2date; then
    aiurpatchup2date "$@";
  else
    aiurpatchyum "$@";
  fi
  if [[ $REBOOT -eq 1 && $RETVAL -eq 0 ]]; then
    reboot;
  fi
}

HTML=0;
REBOOT=0;
RETVAL=0;

while getopts ":br" opt; do
  case $opt in
    b)
      HTML=1;
      ;;
    r)
      REBOOT=1;
      ;;
    \?)
      aiurpatchhelp;
      exit 1;
      ;;
  esac;
done;
shift $((OPTIND - 1));

main $@
exit $RETVAL

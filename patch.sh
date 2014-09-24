#!/usr/bin/env bash

function printHelp ()
{
  echo "$0:";
  echo " -h  html ouput";
  echo " -r  reboot";
}

function main ()
{
  set -o pipefail;
  if $(yum --quiet clean all >/dev/null 2>&1); then
    if PKGS=$(yum --quiet list updates 2>/dev/null); then
      if $(yum -y --quiet update >/dev/null 2>&1); then
        if [[ "$PKGS"  != "" ]]; then
          if [[ $HTML -eq 0 ]]; then
            echo "$PKGS"
          else
            echo "$PKGS" | sed 's/$/<br>/gm';
          fi;
        else
          if [[ $HTML -eq 0 ]]; then
            echo "No updates available";
          else
            echo "No updates available<br>";
          fi;
        fi;
        echo "Yum update complete";
        if [[ $REBOOT -eq 1 ]]; then
          reboot;
        fi;
      else
        echo "Yum update failed";
      fi;
    else
      echo "Yum list updates failed";
    fi;
  else
    echo "Yum clean failed";
  fi
}

HTML=0;
REBOOT=0;

while getopts ":hr" opt; do
  case $opt in
    h)
      HTML=1;
      ;;
    r)
      REBOOT=1;
      ;;
    \?)
      printHelp;
      exit 1;
      ;;
  esac;
done;
shift $((OPTIND - 1));

main

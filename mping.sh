#!/usr/bin/env bash

. /etc/init.d/functions

function main ()
{
  iteration=0
  trap "exit 0" INT
  while true; do
    iteration=$((iteration+1))
    date
    for i in $@; do
      echo -ne "$i:\t"
      ping -c $pcount -W $pwait $i >/dev/null 2>&1 && success || failure
      echo
    done
    echo
    if [[ ! -z $count && $iteration -ge $count ]]; then
      break;
    fi
    sleep $delay
    if [[ $erase -eq 1 ]]; then
      clear
    fi
  done
}

pcount=1
pwait=1
delay=2
erase=0

function isDigit () 
{
  if [[ $# -ne 1 ]]; then
    echo "$0 called wrong" >&2
    return 2
  fi
  if [[ $1 =~ ^[0-9]+$ ]]; then
    return 0
  fi
  return 1
}
function optError ()
{
  if [[ $# -eq 0 ]]; then
    echo "$0 called wrong" >&2
    return 2
  fi
  
}

while getopts ":c:d:w:e" opt; do
  case $opt in
    c)
      if isDigit $OPTARG; then
        count=$OPTARG
      else
        echo "-c parameter, $OPTARG, was not a number" >&2
        exit 2
      fi
      ;;
    d)
      if [[ $OPTARG =~ ^[0-9]+$ ]]; then
        delay=$OPTARG
        echo "-d was triggered, Parameter: $OPTARG" >&2
      else
        echo "-c parameter, $OPTARG, was not a number" >&2
        exit 2
      fi
      ;;
    e)
      erase=1
      echo "-e was triggered" >&2
      ;;
    w)
      if [[ $OPTARG =~ ^[0-9]+$ ]]; then
        pwait=$OPTARG
        echo "-w was triggered, Parameter: $OPTARG" >&2
      else
        echo "-c parameter, $OPTARG, was not a number" >&2
        exit 2
      fi
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      printhelp;
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 2
      ;;
  esac;
done
shift $((OPTIND-1));

main $@

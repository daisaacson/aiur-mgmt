#!/bin/sh

case "$SSH_ORIGINAL_COMMAND" in
  *\&*)
    echo "Rejected"
    ;;
  *\(*)
    echo "Rejected"
    ;;
  *\{*)
    echo "Rejected"
    ;;
  *\;*)
    echo "Rejected"
    ;;
  *\<*)
    echo "Rejected"
    ;;
  *\`*)
    echo "Rejected"
    ;;
  *\|*)
    echo "Rejected"
    ;;
  tar\ cf*|cat\ *)
    $SSH_ORIGINAL_COMMAND
    ;;
  *)
    echo "Rejected"
    ;;
esac

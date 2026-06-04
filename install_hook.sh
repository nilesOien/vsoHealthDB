#!/bin/bash

if [ ! -d .git/hooks ]
then
  echo Script needs to be run in the root of a git repo
  exit -1
fi

if [ -e .git/hooks//pre-commit ]
then
 echo Hook is already in place
 exit 0
fi

cd .git/hooks
ln -sf ../../pre_commit_hook.sh pre-commit
echo Hook installed

exit 0

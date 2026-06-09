#!/bin/bash

# Script that runs unit tests and ruff code tests.
# Can be used as a git hook. To do that it needs
# to be installed as a hook with :
#
# $ ln -sf pre_commit_hook.sh pre-commit
#
# Once this is installed as a pre commit hook, both
# unit tests and ruff code check have to pass for
# git to accept a commit. Hook scripts have to exit
# with 0 status for the requested action to go ahead.
# It's also possible to have pre-push hooks, I just like
# pre-commit hooks more.

final_exit="0"
# Run unit tests.
# They fail if they have non-zero status.
echo Running unit tests...
export PYTHONPATH="$HOME/vsoHealthDB"
pytest -v
status="$?"
if [ "$status" -ne 0 ]
then
 echo pytest unit tests failed
 final_exit="-1"
fi

# Run ruff code checks - similar
echo
echo Running code checks...
ruff check
status="$?"
if [ "$status" -ne 0 ]
then
 echo ruff code check failed
 final_exit="-1"
fi

# Say something
if [ "$final_exit" -eq 0 ]
then
 echo git hook : Tests passed, commit accepted
else
 echo git hook : There were issues, commit rejected
fi

# Exit with status that git will use to
# evaluate if the commit should go ahead.
exit "$final_exit"


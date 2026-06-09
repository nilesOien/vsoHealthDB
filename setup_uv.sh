#!/bin/bash


which uv &> /dev/null
status="$?"
if [ "$status" -ne 0 ]
then
 echo uv is not installed, exiting
 exit -1
fi

# Initialize a bare bones uv project.
uv init --name vsoHealthDB --description "vsoHealthDB" --bare .

uv add -r requirements.txt

exit 0


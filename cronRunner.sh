#!/bin/bash

cd $HOME/vsoHealthDB


if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]
then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH


num=`ps aux | grep "$USER" | grep uvicorn | grep -v grep | wc -l`

if [ "$num" -ne 0 ]
then
 echo Already running
 exit 0
fi

echo Starting

uv run uvicorn vsoHealthReportAPI:healthReportApp --host `hostname -f` --port 26996 --workers 1 &> /dev/null &

exit 0


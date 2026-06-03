#!/bin/bash

cd /home/noien/vsoHealthDB

num=`ps aux | grep "$USER" | grep uvicorn | grep -v grep | wc -l`

if [ "$num" -ne 0 ]
then
 echo Already running
 exit 0
fi

echo Starting

# Enter the env
source pyEnv/bin/activate
uvicorn vsoHealthReportAPI:healthReportApp --host `hostname -f` --port 26996 --workers 1 &> /dev/null &

exit 0


#!/bin/bash

cd /home/noien/vsoHealthDB

num=`ps aux | grep uvicorn | grep -v grep | wc -l`

if [ "$num" -ne 0 ]
then
 echo Already running
 exit 0
fi

echo Starting

# Enter the env
source pyEnv/bin/activate
uvicorn vsoHealthReportAPI:healthReportApp --host vso05.nispdc.nso.edu --port 8001 --workers 1 &> /dev/null &

exit 0


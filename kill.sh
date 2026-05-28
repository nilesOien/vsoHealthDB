#!/bin/bash

num=`ps aux | grep uvicorn | grep -v grep | wc -l`

if [ "$num" -eq 0 ]
then
 echo Not running
 exit 0
fi

pid=`ps aux | grep $USER | grep uvicorn | grep -v grep | awk '{print $2}'`
echo $pid
kill -11 "$pid"

exit 0


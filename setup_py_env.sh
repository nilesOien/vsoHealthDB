#!/bin/bash

if [ -f pyEnv/bin/activate ]
then
 echo Python env already exists
 exit -1
fi

python -m venv pyEnv

if [ ! -f pyEnv/bin/activate ]
then
 echo echo Failed to create python env
 exit -1
fi

source  pyEnv/bin/activate

num=`which python | grep pyEnv | wc -l`
if [ "$num" -eq 0 ]
then
 echo Failed to activate python env
 exit -1
fi

pip install --upgrade pip
pip install sqlalchemy sqlalchemy-utils ruff
pip install fastapi uvicorn python-dotenv email-validator pytest httpx

exit 0


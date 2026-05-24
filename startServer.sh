#!/bin/bash

# Enter the env
source pyEnv/bin/activate

# This starts the uvicorn server, which in turn
# runs the code in vsoHealthReportAPI.py. The syntax is :
# uvicorn path:appName
#
# So that
# uvicorn vsoHealthReportAPI:healthReportApp
# means look in vsoHealthReportAPI.py and start the application healthReportApp in there
#
uvicorn vsoHealthReportAPI:healthReportApp --host 127.0.0.1 --port 8090 --workers 1

exit 0


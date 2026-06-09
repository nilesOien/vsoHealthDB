#!/bin/bash

# This starts the uvicorn server, which in turn
# runs the code in vsoHealthReportAPI.py. The syntax is :
# uvicorn path:appName
#
# So that
# uvicorn vsoHealthReportAPI:healthReportApp
# means look in vsoHealthReportAPI.py and start the application healthReportApp in there
#
uv run uvicorn vsoHealthReportAPI:healthReportApp --host `hostname -f` --port 26996 --workers 1

exit 0


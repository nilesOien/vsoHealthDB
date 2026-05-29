#!/usr/bin/env python

# A series of tests to run with pytest.
# Tests the JSON delivered by FastAPI.
#
# The file __init__.py has to be present for this
# to work (so that the directory is treated as a package).
#
# To see this run the linux command is :
# $ pytest -v

from fastapi.testclient import TestClient
from fastapi import status

# Import the app from 
from .vsoHealthReportAPI import healthReportApp

client=TestClient(healthReportApp)

# Test the max time end point. JSON looks like :
# {
#  "statusMessage": "Success",
#  "statusCode": 0,
#  "maxTime": "20260522_130015"
#  "minTime": "20220422_130015"
# }
def test_response_max_time():
    response=client.get('/vso-health-report-max-time')
    returnedObj = response.json()
    expectedKeys = [ 'statusMessage', 'statusCode', 'maxTime', 'minTime' ]
    for eKey in expectedKeys :
        assert eKey in returnedObj
    assert isinstance(returnedObj.get('statusMessage'), str)
    assert isinstance(returnedObj.get('statusCode'), int)
    assert isinstance(returnedObj.get('maxTime'), str)
    assert isinstance(returnedObj.get('minTime'), str)

    assert returnedObj.get('statusCode') == 0


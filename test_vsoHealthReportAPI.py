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
from pathlib import Path

# Import the app from 
from .vsoHealthReportAPI import healthReportApp

client=TestClient(healthReportApp)

# Test that the database has been made and the .env file exists
def test_setup():
    env_file = Path(".env")
    assert env_file.is_file()
    db_file = Path("report.db")
    assert db_file.is_file()

    return


# Test the time range end point. JSON looks like :
# {
#  "statusMessage": "Success",
#  "statusCode": 0,
#  "maxTime": "20260522_130015"
#  "minTime": "20220422_130015"
# }
def test_response_time_range():
    response=client.get('/vso-health-report-time-range')
    assert response.status_code == status.HTTP_200_OK

    returnedObj = response.json()
    assert(isinstance(returnedObj, dict))

    expectedKeys = [ 'statusMessage', 'statusCode', 'maxTime', 'minTime' ]
    for eKey in expectedKeys :
        assert eKey in returnedObj

    assert isinstance(returnedObj.get('statusMessage'), str)
    assert isinstance(returnedObj.get('statusCode'), int)
    assert isinstance(returnedObj.get('maxTime'), str)
    assert isinstance(returnedObj.get('minTime'), str)

    assert returnedObj.get('statusCode') == 0

    return

# Test the main end point with a single day SOLIS query.
# JSON should look like :
# {
#  "statusMessage": "Success",
#  "statusCode": 0,
#  "results": {
#    "20260301_140014": {
#      "NSO": {
#        "SOLIS": {
#          "ISS": 1,
#          "vsm": 0
#        }
#      }
#    }
#  },
#  "psi_list": [
#    {
#      "Provider": "NSO",
#      "Source": "SOLIS",
#      "Instrument": "ISS"
#    },
#    {
#      "Provider": "NSO",
#      "Source": "SOLIS",
#      "Instrument": "vsm"
#    }
#  ]
# }
# This test doesn't really get into the results field except to say that it's a nested dict,
# four deep with ints at the end.
def test_solis_query():
    response=client.get('/vso-health-report-data?minTime=20260301_000000&maxTime=20260301_235959&sourceCSV=SOLIS')
    assert response.status_code == status.HTTP_200_OK

    returnedObj = response.json()
    # Check types, general structure.
    assert isinstance(returnedObj.get('statusMessage'), str)
    assert isinstance(returnedObj.get('statusCode'), int)
    assert isinstance(returnedObj.get('results'), dict)
    assert isinstance(returnedObj.get('psi_list'), list)

    # Check the status code.
    assert(returnedObj.get('statusCode') == 0)

    # Check the general structure of results - four layer deep nested dict with ints at the end.
    validStatusList = [0,1,2,8,9]
    for tmstring in returnedObj.get('results'): # Time string
        assert(isinstance(tmstring, str))
        for pstring in returnedObj.get('results').get(tmstring): # Provider string
            assert(isinstance(pstring, str))
            for srcstring in returnedObj.get('results').get(tmstring).get(pstring): # Source string
                assert(isinstance(srcstring, str))
                for istring in returnedObj.get('results').get(tmstring).get(pstring).get(srcstring): # Instrument string
                    assert(isinstance(istring, str))
                    statusValue = returnedObj.get('results').get(tmstring).get(pstring).get(srcstring).get(istring)
                    assert(isinstance(statusValue, int))
                    assert statusValue in validStatusList

    # Check the general structure of psi_list - a list of dicts with fixed
    # keys, all values are strings (more conventional than the results field)
    expectedKeys = [ 'Provider', 'Source', 'Instrument' ]
    for item in returnedObj.get('psi_list'):
        assert(isinstance(item, dict))
        for eKey in expectedKeys :
            assert eKey in item
            assert isinstance(item.get(eKey), str)

    return

#
# Test the most recent status end point. This returns something like :
# {
#  "statusMessage": "Success",
#  "statusCode": 0,
#  "result": {
#    "Provider": "NSO",
#    "Source": "GONG",
#    "Instrument": "Learmonth",
#    "Timestring": "20260522_130015",
#    "Status": 0
#  }
# }
def test_most_recent():
    response=client.get('/vso-health-report-most-recent-status?Provider=NSO&Source=GONG&Instrument=Learmonth')
    assert response.status_code == status.HTTP_200_OK

    returnedObj = response.json()
    # Check types, general structure.
    assert isinstance(returnedObj.get('statusMessage'), str)
    assert isinstance(returnedObj.get('statusCode'), int)
    assert isinstance(returnedObj.get('result'), dict)

    # Check the status code.
    assert(returnedObj.get('statusCode') == 0)

    expectedKeys=['Provider', 'Source', 'Instrument', 'Timestring', 'Status']
    for eKey in expectedKeys :
        assert(eKey in returnedObj.get('result'))

    assert isinstance(returnedObj.get('result').get('Provider'), str)
    assert isinstance(returnedObj.get('result').get('Source'), str)
    assert isinstance(returnedObj.get('result').get('Instrument'), str)
    assert isinstance(returnedObj.get('result').get('Timestring'), str)
    assert isinstance(returnedObj.get('result').get('Status'), int)

    return

# Test the summary end point.
def test_summary():
    response=client.get('/vso-health-report-summary?minTime=20250501_000000&maxTime=20260501_235959&providerCSV=OMP')
    assert response.status_code == status.HTTP_200_OK
    returnedObj = response.json()
    # Check the status code.
    assert(returnedObj.get('statusCode') == 0)

    # Check types, general structure.
    assert isinstance(returnedObj.get('statusMessage'), str)
    assert isinstance(returnedObj.get('statusCode'), int)
    assert isinstance(returnedObj.get('results'), list)
    assert isinstance(returnedObj.get('skipped'), list)

    expectedKeys=['Provider', 'Source', 'Instrument']
    for item in returnedObj.get('skipped') :
        assert isinstance(item,dict)
        for eKey in expectedKeys :
            assert eKey in item

    expectedKeys=['Provider', 'Source', 'Instrument', 'numBad', 'numGood', 'percentGood']
    for item in returnedObj.get('results') :
        assert isinstance(item,dict)
        for eKey in expectedKeys :
            assert eKey in item

        assert isinstance(item.get('numBad'), int)
        assert isinstance(item.get('numGood'), int)
        assert isinstance(item.get('percentGood'), float)

        assert item.get('numBad') >= 0
        assert item.get('numGood') >= 0
        assert item.get('percentGood') >= 0.0
        assert item.get('percentGood') <= 100.0


    return




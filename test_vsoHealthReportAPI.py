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

url='/vso-health-report?minTime=20260501_000000&maxTime=20260510_235959&sourceCSV=sdo,gong'
url += '&instrumentCSV=aia&providerCSV=jsoc,nso&statusCSV=8,9'

# Test if we get good HTTP status (status 200) when we ask for the JSON
def test_status():
    response=client.get(url)
    assert response.status_code == status.HTTP_200_OK

"""
The returned JSON should look like :
{
  "statusMessage": "Success",
  "statusCode": 0,
  "results": [
    {
      "Timestring": "20260503_130016",
      "Provider": "JSOC",
      "Source": "SDO",
      "Instrument": "AIA",
      "Status": 8
    },
    {
      "Timestring": "20260504_130044",
      "Provider": "JSOC",
      "Source": "SDO",
      "Instrument": "AIA",
      "Status": 8
    },
    {
      "Timestring": "20260506_130014",
      "Provider": "JSOC",
      "Source": "SDO",
      "Instrument": "AIA",
      "Status": 8
    },
    {
      "Timestring": "20260508_130014",
      "Provider": "JSOC",
      "Source": "SDO",
      "Instrument": "AIA",
      "Status": 8
    },
    {
      "Timestring": "20260509_130014",
      "Provider": "JSOC",
      "Source": "SDO",
      "Instrument": "AIA",
      "Status": 8
    },
    {
      "Timestring": "20260510_130014",
      "Provider": "JSOC",
      "Source": "SDO",
      "Instrument": "AIA",
      "Status": 8
    }
  ]
}
"""

# Test the meta data is there and of correct type and in expected structure.
def test_response_structure() :
    response=client.get(url)
    returnedObj = response.json()
    assert isinstance(returnedObj.get('statusMessage'), str)
    assert isinstance(returnedObj.get('statusCode'), int)
    assert isinstance(returnedObj.get('results'), list)
    expectedKeys=[ 'Timestring', 'Provider', 'Source', 'Instrument', 'Status' ]
    for item in returnedObj.get('results') :
        assert isinstance(item, dict)
        for eKey in expectedKeys :
            assert eKey in item

# Test values returned. Highly dependent on URL in use.
def test_response_values() :
    response=client.get(url)
    returnedObj = response.json()
    for item in returnedObj.get('results') :
        assert item.get('Timestring') >= '20260501_000000'
        assert item.get('Timestring') <= '20260510_235959'
        assert item.get('Provider') == 'JSOC' or item.get('Provider') == 'NSO'
        assert item.get('Source') == 'SDO' or item.get('Source') == 'GONG'
        assert item.get('Instrument') == 'AIA'
        assert item.get('Status') >= 8



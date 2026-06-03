#!/usr/bin/env python

from fastapi import FastAPI, Query
from pydantic import BaseModel, RootModel
from typing import List, Dict
from dotenv import load_dotenv
from sqlalchemy import func, select
from fastapi.staticfiles import StaticFiles
import os

from collections import defaultdict

# Database imports.
from sqlalchemy import create_engine, Column, String, Integer, or_
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists

# A recursive function that returns a dictionary that returns a dictionary...
# With this in place, we can declare a variable and set it to be a
# recursive_dict(), like so :
# status_matrix = recursive_dict()
# and then you can set the recursive nested dictionary keys with wild abandon.
def recursive_dict():
    return defaultdict(recursive_dict)


# Set up tags that appear in the documentation pages that FastAPI generates.
tags_metadata = [
    {
        "name":"healthReportApp",
        "description":"Fast API serving out VSO health report results.",
        "externalDocs": {
            "description": "GitHub repo",
            "url": "https://github.com/nilesOien/vsoHealthDB"
        },
    },
    {
        "name":"vso_health_report_time_range_service",
        "description":"Serves out the time range of data in the database."
    },
    {
        "name":"get_health_report_data",
        "description":"Where to go for health report data."
    }
   ]

# Get an application object
healthReportApp = FastAPI(title="VSO Health Report Database API",
        summary="Serving out the VSO health report",
        description="In the API, hit the Try It Out button, then try setting minTime to 20260501_000000 and maxTime to 20260510_235959 and statusCSV to 8,9 and then hit the Execute button.",
        contact={
          "name": "Niles Oien",
          "url": "https://nso.edu",
          "email": "noien@nso.edu",
        },
        version="1.0.0",
        openapi_tags=tags_metadata)


# Class to represent database table. Comes with a handy to_dict() method
# to convert the thing to a dictionary.
Base = declarative_base()
class reportTable(Base):
    __tablename__='reports'
    Timestring = Column(String,  nullable=False, primary_key=True)
    Provider   = Column(String,  nullable=False, primary_key=True)
    Source     = Column(String,  nullable=False, primary_key=True)
    Instrument = Column(String,  nullable=False, primary_key=True)
    Status     = Column(Integer, nullable=False, primary_key=True)
    def to_dict(self) :
        return {
               "Timestring":self.Timestring,
               "Provider":self.Provider,
               "Source":self.Source,
               "Instrument":self.Instrument,
               "Status":self.Status
              }


# Small end point to get the min,max times in the database.
class timeRangeClass(BaseModel):
    statusMessage: str
    statusCode:    int
    maxTime:       str
    minTime:       str

@healthReportApp.get("/vso-health-report-time-range", response_model=timeRangeClass, tags=['vso_health_report_time_range_service'])
async def get_health_report_time_range():
    """
    Small end point to return the maximum and minimum times in the database.
    sqlite databases do not support time types, so times are strings
    in YYYYMMDD_HHMMSS format (as parsed from the health report CSV file names
    that are read into the sqlite database).
    """

    # Load the environment file .env and get the database URL.
    load_dotenv()
    dbURL = os.getenv("DATABASE_URL")
    # Check that it went OK.
    if dbURL is None :
        d={"statusMessage":"Failure to obtain connection string", "statusCode":-3, "maxTime":"Error", "minTime":"Error"}
        return d

    # See if the database exists.
    if not database_exists(dbURL):
        d={"statusMessage":"Failure to connect to database", "statusCode":-4, "maxTime":"Error", "minTime":"Error"}
        return d

    # Connect to the database.
    engine = create_engine(dbURL)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    stmt = select(func.max(reportTable.Timestring))
    max_value = db.scalar(stmt)

    stmt = select(func.min(reportTable.Timestring))
    min_value = db.scalar(stmt)

    db.close()

    d={"statusMessage":"Success", "statusCode":0, "maxTime":max_value, "minTime":min_value}
    return d





# End point to get health report data. It's passed back in a nested dictionary with dynamic keys.
# It has some meta data, specifically a status message and code, and then the results.
# A two day search with source=SOLIS specified thus returns this :
# {
#  "statusMessage": "Success",
#  "statusCode": 0,
#  "results": {
#    "20260501_130051": {
#      "NSO": {
#        "SOLIS": {
#          "ISS": 1,
#          "vsm": 1
#        }
#      }
#    },
#    "20260502_130016": {
#      "NSO": {
#        "SOLIS": {
#          "ISS": 0,
#          "vsm": 1
#        }
#      }
#    }
#  },
#   "psi_list": [
#     {
#       "Provider": "NSO",
#       "Source": "SOLIS",
#       "Instrument": "ISS"
#     },
#     {
#       "Provider": "NSO",
#       "Source": "SOLIS",
#       "Instrument": "vsm"
#    }
#  ]
# }
# where the time strings are the times of the health report run,
# NSO is the provider, SOLIS is the source, ISS and vsm are instruments, and
# the integer values are the status codes for the health report for that day.

# Instrument class represents something like this in the above example :
# {
#  "ISS": 0,
#  "vsm": 1
# }
# With the integer  values being the status values from the health report run.
class instrumentClass(RootModel):
    root: dict[str, int]
   
# Source class represents something like "SOLIS": {...} in the above example : 
class sourceClass(RootModel):
    root: dict[str, instrumentClass]

# Provider class represents something like "NSO": {...} in the above example :
class providerClass(RootModel):
    root: dict[str, sourceClass]

# Time class represents something like "20260502_130016": {...} in the above example :
class timeClass(RootModel):
    root: dict[str, providerClass]

# Class to represent a dict with Provider, Source, Instrument entries. We need to send this
# to cope with the case in which instruments have been added/removed in the time range we're
# looking at, and so not all provider/source/instrument items are present for all times.
class psiClass(BaseModel):
    Provider:   str
    Source:     str
    Instrument: str

# Pydantic class to represent the entire returned data structure :
class statusMatrixClass(BaseModel):
    statusMessage: str
    statusCode:    int
    results:       timeClass
    psi_list:      List[psiClass]

@healthReportApp.get("/vso-health-report-data", response_model=statusMatrixClass, tags=['get_health_report_data'])
async def get_health_report_data(minTime:       str = Query(default=None),
                                 maxTime:       str = Query(default=None),
                                 sourceCSV:     str = Query(default=None),
                                 instrumentCSV: str = Query(default=None),
                                 providerCSV:   str = Query(default=None),
                                 statusCSV:     str = Query(default=None)):
    """
    Returns a JSON structure with VSO health report information from a database.
    Times are in YYYYMMDD_HHMMSS format. Provider, source and instrument CSVs are comma
    separated lists of Strings. Provider and source are are converted to upper case internally,
    with white spaces stripped out. Instruments are left as-is.
    Status is a comma separated list of integer status codes with the following meanings :
    0 => Test passed,  1 => Test passed on known request,
    2 => Test skipped, 8 => Test failed on data download, 9 => Test failed with no response.
    Queries are limited to 50,000 responses just to avoid DoS attacks, accidents etc.
    """
    # Load the environment file .env and get the database URL.
    load_dotenv()
    dbURL = os.getenv("DATABASE_URL")
    # Check that it went OK.
    if dbURL is None :
        d={"statusMessage":"Failure to obtain connection string", "statusCode":-3, "results":[]}
        return d

    # See if the database exists.
    if not database_exists(dbURL):
        d={"statusMessage":"Failure to connect to database", "statusCode":-4, "results":[]}
        return d

    # Connect to the database.
    engine = create_engine(dbURL)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    query = db.query(reportTable)

    # If a minimum time was specified, filter on that.
    if minTime is not None :
        query = query.filter(reportTable.Timestring >= minTime)

    # Ditto maximum time.
    if maxTime is not None :
        query = query.filter(reportTable.Timestring <= maxTime)

    # For the comma separated lists, convert to upper case, split into a list
    # based on the comma, then make a list of filters based on the list of items,
    # then filter on that by passing the list of filters to the or_() function
    # as positional arguments using the star unpacking operator.
    if instrumentCSV is not None :
        inst_list = instrumentCSV.split(',') # Note : don't convert instrument to upper case - no .upper()
        inst_filters = [reportTable.Instrument == inst for inst in inst_list]
        query=query.filter(or_(*inst_filters))

    if providerCSV is not None :
        pCSV = "".join(providerCSV.split()) # Strip spaces
        prov_list = pCSV.upper().split(',')
        prov_filters = [reportTable.Provider == prov for prov in prov_list]
        query=query.filter(or_(*prov_filters))

    if sourceCSV is not None :
        sCSV = "".join(sourceCSV.split())
        src_list = sCSV.upper().split(',')
        src_filters = [reportTable.Source == src for src in src_list]
        query=query.filter(or_(*src_filters))

    # Status is only slightly differrent since have to throw an
    # exception if something is passed in that cannot convert to int.
    if statusCSV is not None :
        sts_list = statusCSV.split(',')
        i_sts_list = []
        for sts in sts_list :
            try :
                int_st = int(sts)
                i_sts_list.append(int_st)
            except ValueError :
                db.close()
                d={"statusMessage":f"Failure since non-integer status {sts} specified", "statusCode":-1, "results":{}, "psi_list":[]}
                return d
        sts_filters = [reportTable.Status == int_stat for int_stat in i_sts_list ]
        query=query.filter(or_(*sts_filters))

    # Set the order in which the output is sorted.
    query=query.order_by(reportTable.Timestring, reportTable.Provider,
                     reportTable.Source, reportTable.Instrument)

    # Set a (high) limit, just to avoid DoS attacks on the API.
    query=query.limit(50000)

    # Do the query
    db_results = query.all()

    # Close the database, we're done with it.
    db.close()


    if db_results is None:
        d={"statusMessage":"Failure to obtain data", "statusCode":-2, "results":{}, "psi_list":[]}
        return d

    # Re-organize the data a bit.
    status_matrix=recursive_dict()
    psi_list = []
    for item in db_results :
        item_dict=item.to_dict()
        status_matrix[item_dict['Timestring']][item_dict['Provider']][item_dict['Source']][item_dict['Instrument']] = item_dict['Status']
        # Be sure we have this provider/source/instrument in the psi_list, add it if not.
        ml_item = { 'Provider':item_dict['Provider'], 'Source':item_dict['Source'], 'Instrument':item_dict['Instrument'] }
        if not ml_item in psi_list :
            psi_list.append(ml_item)

    # Sort the list of provider/source/instrument into order.
    psi_list = sorted(
        psi_list, 
        key=lambda x: (x['Provider'], x['Source'], x['Instrument'])
    )

    d={"statusMessage":"Success", "statusCode":0, "results":status_matrix, "psi_list":psi_list}

    return d





# Serve the web pages.
# In the call below :
#
# * The first argument ("/") is the URL path where the files will be exposed,
#   so it will pop up as "http://localhost:26996/"
# * The second argument is the actual directory on this server,
#   and setting html=True will serve out index.html by default.
# * The third argument is an internal name that can be used for URL
#   generation in templates, often with the url_for function.
#
# Note that order matters. FastAPI matches requests *sequentially* so
# we define this last so that it will try the API end points first.
# Follow sym links to show test coverage results.
healthReportApp.mount("/", StaticFiles(directory="./web_page", html=True, follow_symlink=True), name="webpages")


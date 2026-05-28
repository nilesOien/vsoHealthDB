#!/usr/bin/env python

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from sqlalchemy import func, select
from fastapi.staticfiles import StaticFiles
import os

# Database imports.
from sqlalchemy import create_engine, Column, String, Integer, or_
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists

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
        "name":"vso_health_report_service",
        "description":"An end point that serves out the VSO health report results."
    },
    {
        "name":"vso_health_report_max_time_service",
        "description":"Serves out the max time in the database."
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

Base = declarative_base()
class reportTable(Base):
    __tablename__='reports'
    Timestring = Column(String,  nullable=False, primary_key=True)
    Provider   = Column(String,  nullable=False, primary_key=True)
    Source     = Column(String,  nullable=False, primary_key=True)
    Instrument = Column(String,  nullable=False, primary_key=True)
    Status     = Column(Integer, nullable=False, primary_key=True)

# Define a class that is used in the general format of the JSON response.
# This is a pydantic class (inherits from "BaseModel" class) that is
# used for verification.
class responseClass(BaseModel) :
    # This triple quoted comment winds up on the documentation page
    # for this schema.
    """
    Pydantic class that defines the format of what this endpoint delivers.
    """
    Timestring:      str
    Provider:        str
    Source:          str
    Instrument:      str
    Status:          int

# Actually, embed that class in another class so that some meta data can be returned,
# like a status code and status message.
class embeddedResponseClass(BaseModel):
    statusMessage:   str
    statusCode:      int
    results:         List[responseClass]

@healthReportApp.get("/vso-health-report", response_model=embeddedResponseClass, tags=['vso_health_report_service'])
async def get_health_report(minTime:       str = Query(default=None),
                            maxTime:       str = Query(default=None),
                            sourceCSV:     str = Query(default=None),
                            instrumentCSV: str = Query(default=None),
                            providerCSV:   str = Query(default=None),
                            statusCSV:     str = Query(default=None)):
    """
    Returns a list of dictionaries with VSO health report information.
    Times are in YYYYMMDD_HHMMSS format. Source, instrument and provider CSVs are comma
    separated lists of items. These are converted to upper case internally.
    Status are integer status codes. 0 => Pass, 1 => Pass on known request,
    2 => Skipped, 8 => Fail on download, 9 => Fail no response.
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
        inst_list = instrumentCSV.split(',') # Actually don't convert instrument to upper case
        inst_filters = [reportTable.Instrument == inst for inst in inst_list]
        query=query.filter(or_(*inst_filters))

    if providerCSV is not None :
        prov_list = providerCSV.upper().split(',')
        prov_filters = [reportTable.Provider == prov for prov in prov_list]
        query=query.filter(or_(*prov_filters))

    if sourceCSV is not None :
        src_list = sourceCSV.upper().split(',')
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
                d={"statusMessage":f"Failure since non-integer status {sts} specified", "statusCode":-1, "results":[]}
                return d
        sts_filters = [reportTable.Status == int_stat for int_stat in i_sts_list ]
        query=query.filter(or_(*sts_filters))

    # Set the order in which the output is sorted.
    query=query.order_by(reportTable.Timestring, reportTable.Provider,
                     reportTable.Source, reportTable.Instrument)

    # Do the query
    db_results = query.all()

    # Close the database, we're done with it.
    db.close()

    if db_results is None:
        d={"statusMessage":"Failure to obtain data", "statusCode":-2, "results":[]}
        return d

    d={"statusMessage":"Success", "statusCode":0, "results":db_results}

    return d



# Small end point to get the max time in the database.

class maxTimeClass(BaseModel):
    statusMessage: str
    statusCode:    int
    maxTime:       str
    minTime:       str

@healthReportApp.get("/vso-health-report-max-time", response_model=maxTimeClass, tags=['vso_health_report_max_time_service'])
async def get_health_report_max_time():

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


# Serve the web pages.
# In the call below :
#
# * The first argument ("/") is the URL path where the files will be exposed,
#   so it will pop up as "http://localhost:8001/"
# * The second argument is the actual directory on this server,
#   and setting html=True will serve out index.html by default.
# * The third argument is an internal name that can be used for URL
#   generation in templates, often with the url_for function.
#
# Note that order matters. FastAPI matches requests *sequentially* so
# we define this last so that it will try the API end points first.
# Follow sym links to show test coverage results.
healthReportApp.mount("/", StaticFiles(directory="./web_page", html=True, follow_symlink=True), name="webpages")


#!/usr/bin/env python

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
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
            "description": "How this documentation was added",
            "url": "https://fastapi.tiangolo.com/tutorial/metadata/#use-your-tags"
        },
    },
    {
        "name":"vso_health_report_service",
        "description":"An end point that serves out the VSO health report results."
    }
   ]

# Get an application object
healthReportApp = FastAPI(title="Fast API Example",
        summary="Serving out the VSO health report",
        description="Useful to base a web application on",
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

    # This query would get data from the two columns for the whole table.
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
        inst_list = instrumentCSV.upper().split(',')
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


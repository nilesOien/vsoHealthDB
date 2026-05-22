#!/usr/bin/env python

# Small script to print a selection from the database. The selection
# can be made on a time range, and/or lists of instruments, providers and sources
# as specified on the command line.

import argparse
import pprint

from sqlalchemy import create_engine, UniqueConstraint, Column, String, Integer, or_
from sqlalchemy.orm import declarative_base, sessionmaker

parser = argparse.ArgumentParser(description='Print a selection from the database.')

parser.add_argument('--minTime', '-b', default=None, type=str, help='Minimum time in YYYYMMDD_HHMMSS format')
parser.add_argument('--maxTime', '-e', default=None, type=str, help='Maximum time in YYYYMMDD_HHMMSS format')

parser.add_argument('--instruments', '-i', default=None, type=str, 
 help='Comma separated list of instruments')

parser.add_argument('--providers', '-p', default=None, type=str,
 help='Comma separated list of providers')

parser.add_argument('--sources', '-s', default=None, type=str,
 help='Comma  separated list of sources')

parser.add_argument('--minStatus', '-q', default=None, type=int,
 help='Minimum integer status')

parser.add_argument('--verbose', '-v', action='store_true', help='Activate verbose messaging.')

args = parser.parse_args()


# Get the sqlalchemy base class, then make a class that inherits
# from that base class to represent the table.
Base = declarative_base()

# Added a method to convert this class to a dict for printing.
class reportTable(Base):
    __tablename__='reports'
    Timestring = Column(String,  nullable=False, primary_key=True)
    Provider   = Column(String,  nullable=False, primary_key=True)
    Source     = Column(String,  nullable=False, primary_key=True)
    Instrument = Column(String,  nullable=False, primary_key=True)
    Status     = Column(Integer, nullable=False, primary_key=True)
    __table_args__ = (UniqueConstraint('Timestring', 'Provider', 'Source',
                      'Instrument', 'Status', name='unique_constraint'),)
    def to_dict(self):
       return {
               "Timestring":self.Timestring,
               "Provider":self.Provider,
               "Source":self.Source,
               "Instrument":self.Instrument,
               "Status":self.Status
              } 

# Connect to the database.
engine = create_engine("sqlite:///report.db", echo=args.verbose)
Session = sessionmaker(bind=engine)
session = Session()

# Get the query and start adding filters
query = session.query(reportTable)

if args.minTime is not None :
    query = query.filter(reportTable.Timestring >= args.minTime)

if args.maxTime is not None :
    query = query.filter(reportTable.Timestring <= args.maxTime)

# The Instrument, Source and Provider filters all take a comma separated list of items,
# split that into a list of items based on the comma, and then filter based on the or_()
# function that is given the list as positional arguments using the unpacking
# operator (the star).
if args.instruments is not None :
    inst_list = args.instruments.split(',')
    inst_filters = [reportTable.Instrument == inst for inst in inst_list]
    query=query.filter(or_(*inst_filters))

if args.providers is not None :
    prov_list = args.providers.split(',')
    prov_filters = [reportTable.Provider == prov for prov in prov_list]
    query=query.filter(or_(*prov_filters))

if args.sources is not None :
    src_list = args.sources.split(',')
    src_filters = [reportTable.Source == src for src in src_list]
    query=query.filter(or_(*src_filters))

if args.minStatus is not None :
    query = query.filter(reportTable.Status >= args.minStatus)

# Set the order in which the output is sorted.
query=query.order_by(reportTable.Timestring, reportTable.Provider,
                     reportTable.Source, reportTable.Instrument)

# Get the results, convert to a list of dicts, and print.
results = query.all()
list_of_results = [result.to_dict() for result in results ]
pprint.pprint(list_of_results)
print(f"{len(list_of_results)} results found.")

quit()


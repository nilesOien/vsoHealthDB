#!/usr/bin/env python

# Small script to ingest a CSV file into the database created by
# the createDB.py script.

import csv
import argparse
import pprint

from sqlalchemy import create_engine, UniqueConstraint, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

parser = argparse.ArgumentParser(description='Read a VSO health report CSV file into a database.')

parser.add_argument('--inFile', '-i', required=True, type=str, help='Input file name following the standard convention, like vso_health_check_20260521_134851.csv')
parser.add_argument('--verbose', '-v', action='store_true', help='Activate verbose messaging.')

args = parser.parse_args()

# Parse the timestamp from the filename.
tstring = args.inFile[-19:-4]
if args.verbose :
    print(f"Time parsed from {args.inFile} is {tstring}")
 
# Initialize an empty list to hold the dictionaries
list_of_dicts = []
 
# Open the CSV file for reading
with open(args.inFile, mode='r', newline='') as csvfile:
    # Create a DictReader object
    reader = csv.DictReader(csvfile)
    
    # Iterate over each row in the CSV
    for row in reader:
        # Append each row (as a dictionary) to the list
        list_of_dicts.append(row)
 
# Now list_of_dicts contains all rows as dictionaries
# But we need to add the time that was parsed from the filename.
# So make a new list.
tstring_list = []
for dic in list_of_dicts :
    dic['Timestring'] = tstring # Add the timestring
    tstring_list.append(dic)


if args.verbose :
    pprint.pprint(tstring_list)
print(f"{len(tstring_list)} items read from {args.inFile}")

# Get the sqlalchemy base class, then make a class that inherits
# from that base class to represent the table.
Base = declarative_base()

class reportTable(Base):
    __tablename__='reports'
    Timestring = Column(String,  nullable=False, primary_key=True)
    Provider   = Column(String,  nullable=False, primary_key=True)
    Source     = Column(String,  nullable=False, primary_key=True)
    Instrument = Column(String,  nullable=False, primary_key=True)
    Status     = Column(Integer, nullable=False, primary_key=True)
    __table_args__ = (UniqueConstraint('Timestring', 'Provider', 'Source',
                      'Instrument', 'Status', name='unique_constraint'),)

# Connect to the database.
engine = create_engine("sqlite:///report.db", echo=args.verbose)
Session = sessionmaker(bind=engine)
session = Session()

# Put the list of dicts we just read into the database.
# The dictionary keys are the same as the database table column names.
ok=False
try:
    # Use bulk_insert_mappings (more efficient for large datasets)
    session.bulk_insert_mappings(reportTable, tstring_list)
    session.commit()
    print("Data inserted successfully.")
    ok=True

except Exception as e:
    session.rollback() # Rollback on error
    print(f"Error inserting data : {e}")
    ok=False

finally:
    session.close()

# That's all - the database should be created.
if ok :
    print("Normal termination.")
else :
    print("Something went wrong")

quit()


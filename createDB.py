#!/usr/bin/env python

# Small script that sets up a simple sqlite database with a table in it.
# CSV files can then be read into the database with the fileToDB.py script.

from sqlalchemy import create_engine, UniqueConstraint, Index, Column, String, Integer
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import declarative_base

# Make a table, the column names of which line
# up with what we have in the CSV files. Table name is "reports".
# Unique constraint ensures no duplicate entries.
# In this case, none of the entries can be NULL, so set nullable to False.

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
                      'Instrument', 'Status', name='unique_constraint'),
                      Index('report_indx', 'Timestring', 'Provider', 'Source',
                            'Instrument','Status'),)

# Create the database.
# Had to install sqlalchemy_utils to do this.
engine = create_engine("sqlite:///report.db", echo=False)

Base.metadata.create_all(engine)

if not database_exists(engine.url):
    create_database(engine.url)

# Drop any existing version of that table.
# It was important to make the table first, othwerwise
# drop_all doesn't know what table we're talking about.
Base.metadata.drop_all(engine)

# OK, now create the empty table. Turn echo on, just for this.
engine.echo=True
Base.metadata.create_all(engine)
engine.echo=False

quit()


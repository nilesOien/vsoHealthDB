
from sqlalchemy import or_
from .models import Report
def csv_upper(v): return None if v is None else "".join(v.split()).upper().split(",")
def apply_filters(query,minTime=None,maxTime=None,providerCSV=None,sourceCSV=None,instrumentCSV=None,statusCSV=None):
    if minTime is not None:
        query=query.filter(Report.Timestring>=minTime)
    if maxTime is not None: 
        query=query.filter(Report.Timestring<=maxTime)
    if instrumentCSV is not None: 
        query=query.filter(or_(*[Report.Instrument==i for i in instrumentCSV.split(",")]))
    if providerCSV is not None: 
        query=query.filter(or_(*[Report.Provider==p for p in csv_upper(providerCSV)]))
    if sourceCSV is not None: 
        query=query.filter(or_(*[Report.Source==s for s in csv_upper(sourceCSV)]))
    if statusCSV is not None:
        vals=[int(x) for x in statusCSV.split(",")]
        query=query.filter(or_(*[Report.Status==v for v in vals]))
    return query

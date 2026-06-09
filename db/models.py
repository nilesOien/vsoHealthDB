
from sqlalchemy import Column,String,Integer
from sqlalchemy.orm import declarative_base
Base=declarative_base()
class Report(Base):
    __tablename__='reports'
    Timestring=Column(String,nullable=False,primary_key=True)
    Provider=Column(String,nullable=False,primary_key=True)
    Source=Column(String,nullable=False,primary_key=True)
    Instrument=Column(String,nullable=False,primary_key=True)
    Status=Column(Integer,nullable=False,primary_key=True)
    def to_dict(self):
        return {"Timestring":self.Timestring,"Provider":self.Provider,"Source":self.Source,"Instrument":self.Instrument,"Status":self.Status}

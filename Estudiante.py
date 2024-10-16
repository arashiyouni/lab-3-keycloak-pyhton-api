from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EstudianteDB(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    carnet = Column(String, index=True)
    name = Column(String, index=True)
    lastname = Column(String, index=True)
    university_carrer = Column(String, index=True)

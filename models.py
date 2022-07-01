from sqlalchemy import Column, String, DateTime, Float, Integer
from db import Base


class Flight(Base):
    __tablename__ = "flight"

    flight_id = Column(Integer, primary_key=True)
    callsign = Column(String)
    number = Column(String)
    icao24 = Column(String)
    registration = Column(String)
    typecode = Column(String)
    origin = Column(String)
    destination = Column(String)
    firstseen = Column(DateTime(timezone=True))
    lastseen = Column(DateTime(timezone=True))
    day = Column(DateTime)
    latitude_1 = Column(Float)
    longitude_1 = Column(Float)
    altitude_1 = Column(Float)
    latitude_2 = Column(Float)
    longitude_2 = Column(Float)
    altitude_2 = Column(Float)


class Airport(Base):
    __tablename__ = "airport"

    airport_id = Column(Integer, primary_key=True)
    airport_ident = Column(String)
    airport_type = Column(String)
    airport_name = Column(String)
    airport_latitude_deg = Column(Float)
    airport_longitude_deg = Column(Float)
    airport_elevation_ft = Column(Integer)
    airport_continent = Column(String)
    airport_iso_country = Column(String)
    airport_iso_region = Column(String)
    airport_municipality = Column(String)
    airport_scheduled_service = Column(String)
    airport_gps_code = Column(String)
    airport_iata_code = Column(String)
    airport_local_code = Column(String)
    airport_home_link = Column(String)
    airport_wikipedia_link = Column(String)
    airport_keywords = Column(String)


class Country(Base):
    __tablename__ = "country"

    country_id = Column(Integer, primary_key=True)
    country_code = Column(String)
    country_name = Column(String)
    country_continent = Column(String)
    country_wiki = Column(String)
    country_keywords = Column(String)


class Region(Base):
    __tablename__ = "region"

    region_id = Column(Integer, primary_key=True)
    region_code = Column(String)
    region_local_code = Column(String)
    region_name = Column(String)
    region_continent = Column(String)
    region_iso_country = Column(String)
    region_wiki = Column(String)
    region_keywords = Column(String)


class Airline(Base):
    __tablename__ = "airline"

    airline_id = Column(Integer, primary_key=True)
    airline_name = Column(String)
    airline_iata = Column(String)
    airline_icao = Column(String)
    airline_callsign = Column(String)
    airline_country = Column(String)
    airline_comments = Column(String)

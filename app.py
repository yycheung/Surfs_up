from flask import Flask, jsonify

import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

############# Set Up the Database #############
engine = create_engine("sqlite:///hawaii.sqlite")
###############################################


# reflect the database into our classes
Base = automap_base()

# reflect tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# create a variable for each of the classes
Measurement = Base.classes.measurement 
Station = Base.classes.station

# create a session link from Python to our database
session = Session(engine)

############# Set Up Flask #############
app = Flask(__name__)
###############################################

# Create the Welcome Route
@app.route("/")
def welcome():
    return('''
    Welcome to the Climate Analysis API!<br>
    Available Routes:<br>
    <a href = "/api/v1.0/precipitation"> Precipitation</a><br>
    <a href = "/api/v1.0/stations"> Station</a><br>
    <a href = "/api/v1.0/tobs"> Monthly Temperature</a><br>
    <a href = "/api/v1.0/temp/start/end"> Statistics </a><br>
    ''')
    
    # Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# Stations Route
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

# Monthly Temperature Route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

# Statistics Route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)

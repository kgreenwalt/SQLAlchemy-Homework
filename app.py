import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite", echo=True)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route('/')
def welcome():

    # Return All available routes
    return(
        f"Available Routes<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt<br/>"
        "/api/v1.0/&ltstart&gt/&ltend&gt"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    
    # Query date and precipitation data
    precip = session.query(Measurement.date, Measurement.prcp).all()

    # Turn tuples into list
    all_dates = list(np.ravel(precip))

    # Return JSON library
    return jsonify(all_dates)

@app.route('/api/v1.0/stations')
def stations():

    # Query for names of stations
    names = session.query(Station.station).all()

    # Turn tuples into list
    all_names = list(np.ravel(names))

    # Return JSON library
    return jsonify(all_names)

@app.route('/api/v1.0/tobs')
def tobs():

    # Find most recent date in database
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Convert string of date to datetime
    string_to_date = dt.datetime.strptime(most_recent_date[0], "%Y-%m-%d").date()

    # Find one year prior
    year_ago = string_to_date - dt.timedelta(days=365)

    # Query database for date and temps from the database greater that a year before the most recent date
    temperatures = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()

    # Convert tuples into list
    all_temps = list(np.ravel(temperatures))

    # Return JSON library
    return jsonify(all_temps)

# Setup both routes to go to this definition
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')

# Set end equal to none so that if non is given it will return the max, min, and avg from the start date
def start_and_end(start, end=None):
    
    # If no end calculations are from start date to last date
    if end == None:

        # Query database
        start_only = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
            .filter(Measurement.date >= start).all()
        
        # Convert tuple to list
        all_after = list(np.ravel(start_only))

        # Return JSON library
        return jsonify(all_after)
    else:

        # Query database
        start_end = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
            .filter(Measurement.date >= start).filter(Measurement.date <= end).all()

        # Convert tuple to list
        all_select = list(np.ravel(start_end))

        # Return JSON library
        return jsonify(all_select)

# Run with debugger turn debugger off for public release
if __name__ == "__main__":
    app.run(debug=True)

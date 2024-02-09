import sqlite3
from datetime import datetime, timedelta, timezone
from math import sin, pi

""" Create an example sqlite database for testing the webview
website for the home sensor network.
"""

table_list = ["stations", "temperature", "meteoTemps", "lastUpdates"]

stations_schema = """CREATE TABLE stations
( station_id STRING,
  location STRING,
  sublocation STRING,
  description STRING,
  from_timestamp_utc TIMESTAMP,
  to_timestamp_utc TIMESTAMP,
  is_current BOOLEAN);"""

temperature_schema = """CREATE TABLE temperature
( timestamp_utc TIMESTAMP,
  station_id STRING,
  temp_c FLOAT);"""

meteoTemps_schema = """CREATE TABLE meteoTemps
(station_id STRING,
temp_c FLOAT,
pressure_hpa FLOAT,
relative_hum_pct FLOAT,
timestamp_utc FLOAT);"""

lastUpdates_schema = """CREATE TABLE lastUpdates
( station_id STRING NOT NULL,
  timestamp_utc TIMESTAMP,
  measure_type STRING NOT NULL,
  measure_value FLOAT,
  last_archive_time_utc TIMESTAMP,
  last_archive_value FLOAT,
  PRIMARY KEY(station_id, measure_type));"""


schema_list = [stations_schema,
               temperature_schema,
               meteoTemps_schema, 
               lastUpdates_schema]
    
def clean_db(cur, table_list):
    """ Remove all existing data from listed tables """
    
    for table in table_list:
        cur.execute(f"DROP TABLE IF EXISTS {table}")

    cur.execute("VACUUM;")
        
    return None


def generate_timestamps(start_date, step_size_hrs, steps):
    """ From a start date generate a list of UNIX timestamps
    for a total of 'steps'
    """

    outlist = []
    step_size_hrs = timedelta(hours=step_size_hrs)
    
    for i in range(0, steps):

        time = (start_date + step_size_hrs * i)
        
        outlist.append(time.timestamp())

    return outlist


def generate_temp_samples(cur,
                          stationname,
                          timestamp_list,
                          middle_temp,
                          temp_swing):
    """ Add example data into the temperature table """

    data = []
    
    for count, timestamp in enumerate(timestamps):
        temp = middle_temp + (temp_swing * sin(pi * count * 0.3))
        data.append((timestamp, stationname, round(temp, 2)))

    data = tuple(data)

    cur.executemany("INSERT INTO temperature VALUES (?, ?, ?)", data)

    return None


def generate_weather_temps(cur,
                          stationname,
                          timestamp_list,
                          middle_temp,
                          temp_swing):
    """ Generate sample weather temperature data """

    data = []

    for count, timestamp in enumerate(timestamps):
        temp = temp = middle_temp + (temp_swing * sin(pi * count * 0.3))
        data.append((stationname, round(temp, 2), 1000, 50, timestamp))

    data = tuple(data)

    cur.executemany("INSERT INTO meteoTemps VALUES (?, ?, ?, ?, ?)", data)
    
    return None


if __name__ == "__main__":

    con = sqlite3.connect("example-db.sqlite3")
    cur = con.cursor()

    sample_length = 30 # days
    
    clean_db(cur, table_list)

    #for schema in schema_list:
    creation_script = ("BEGIN;\n" +
                       "\n".join(schema_list) +
                       "\nCOMMIT;")

    cur.executescript(creation_script)

    endtime = datetime.now(timezone.utc)
    endtime = endtime.replace(second=0, microsecond=0)
    starttime = endtime - timedelta(days=sample_length)

    timestamps = generate_timestamps(starttime, 4, (6*sample_length))

    generate_temp_samples(cur, "StationA", timestamps, 20, 10)
    generate_temp_samples(cur, "StationB", timestamps, 20, 5)

    generate_weather_temps(cur, "OutsideStation", timestamps, 10, 10)
    
    statc_endtime = (starttime + timedelta(days=sample_length/2)).timestamp()
    
    station_data = (
        ( 'StationA', 'A Place', 'A Sublocation', 'Station A', starttime.timestamp(), None, True ),
        ( 'StationB', 'B Place', 'B Sublocation', 'Station B', starttime.timestamp(), None, True ),
        ( 'StationC', 'C Place', 'C Sublocation', 'Expired Station', starttime.timestamp(), statc_endtime, False ),
        ( 'OutsideStation', 'Outside', 'Near a tree?', 'Outdoor data', starttime.timestamp(), None, True))

    cur.executemany("INSERT INTO stations VALUES (?, ?, ?, ?, ?, ?, ?)", station_data)

    # make the last update 5 minutes old.
    last_update = (endtime - timedelta(minutes=5)).timestamp()
    
    last_updates = (
        ("StationA", last_update, "temp_c", 20, last_update, 20),
        ("StationB", last_update, "temp_c", 25, last_update, 25),
        ("StationC", statc_endtime, "temp_c", 20, statc_endtime, 20),
        ("StationA", last_update, "humidity_pct", 50, last_update, 50),
        ("StationB", last_update, "humidity_pct", 50, last_update, 50),
        ("StationC", statc_endtime, "humidity_pct", 50, statc_endtime, 50))

    cur.executemany("INSERT INTO lastUpdates VALUES (?, ?, ?, ?, ?, ?)", last_updates)
    
    con.commit()  # Don't forget
    con.close()

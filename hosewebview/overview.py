from flask import (
    Blueprint, flash, g,
    redirect, render_template,
    request, url_for, current_app)

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from werkzeug.exceptions import abort

from hosewebview.db import get_db

def render_local_time(tstamp, dtformat=None, timezone=None):
    """ Given a UTC UNIX Timestamp, formatting string
    and the local timezone, return the local time as
    a string. If format or timezone are incorrect, will
    fall back to UTC and ISO representation.
    """

    tzstump = None

    dt = datetime.fromtimestamp(tstamp, tz=None)
    
    try:
        dt = dt.astimezone(ZoneInfo(timezone))
    except ZoneInfoNotFoundError:
        # Mention it's utc
        tzstump = " UTC"

    if not dtformat:
        dtformat = "%Y-%N-%D %H:%m:%s"

    time_rendered = dt.strftime(dtformat)
    if tzstump:
        time_rendered = time_rendered + tzstump

    return time_rendered


bp = Blueprint("overview", __name__)

@bp.route("/")
def index():
    db = get_db()

    last_readings_query = """
       SELECT location,
       timestamp_utc,
       temp_c,
       humidity_pct FROM
       (SELECT
       s.location,
       ut.timestamp_utc AS timestamp_utc,
       ut.measure_value AS temp_c,
       uh.measure_value AS humidity_pct
       FROM stations s
       LEFT JOIN lastUpdates ut
            ON ut.station_id = s.station_id
            AND ut.measure_type == 'temp_c'
       LEFT JOIN lastUpdates uh
            ON uh.station_id = s.station_id
            AND uh.measure_type == 'humidity_pct'
       WHERE uh.measure_value IS NOT NULL
       AND s.is_current = 1)
       UNION ALL
       SELECT
       s.location,
       mt.timestamp_utc,
       mt.temp_c,
       mt.relative_hum_pct AS humidity_pct
       FROM stations s
       LEFT JOIN meteoTemps mt
            ON s.station_id = mt.station_id
       WHERE mt.ROWID = (SELECT MAX(ROWID) FROM meteoTemps)
       ORDER BY location ASC
    """
    
    summaries = get_db().execute(
         last_readings_query).fetchall()
    
    # make it to a dict and add new entries
    # that we need
    formatted_results = []
    
    for row in summaries:
        new_row = {key: value for key, value in zip(row.keys(), row)}
        
        new_row["localtime"] = render_local_time(row["timestamp_utc"],
                                                 "%H:%m:%S %p",
                                                 "Europe/Berlin")
        formatted_results.append(new_row)

    # Set in global preferences to add automatically
    # to any initial history plot.
    additional_history_locs = current_app.config["DEFAULT_STATIONS"]

    return render_template("overview.html",
                           summaries=formatted_results,
                           add_locs=additional_history_locs)


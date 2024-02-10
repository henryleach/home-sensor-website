from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from hosewebview.db import get_db

import pandas
import plotly.express as px
import hosewebview.plotlythemes  # imports light_temp currently
from datetime import datetime, timezone, timedelta

bp = Blueprint("history", __name__)

@bp.route("/history")
def history():
    """ Plot the history of sensor readings
    for various locations.
    """

    # getlist returns an empty array if no values
    location = request.args.getlist('location', type=str)
    mobile = request.args.get("mobile", default="true", type=str)
    # These should be iso formatted strings.
    in_start_time = request.args.get("start_time", default=None, type=str)
    in_end_time = request.args.get("end_time", default=None, type=str)

    # Check in times for type and value errors, and set defaults.
    
    db = get_db()
    # Need list of currently active locations
    # for various purposes:

    location_query = """SELECT location from stations WHERE is_current=true;"""

    all_locations = pandas.read_sql_query(location_query,
                                          get_db())["location"].to_list()
    # Make sure it's always the same sequence. Quicker to sort in SQlite?
    all_locations.sort()
    
    if location == []:
        locations = tuple(all_locations)
    else:
        locations = tuple(location)

    # default is 'true', e.g. mobile view.
    if mobile == "true":
        mobile = True
        plot_template = "light_mobile"
    else:
        mobile = False
        plot_template = "plotly_white"

    # Set the start and end times, checking that it's
    # a suitable string, and if not, setting a default.
    # This doesn't contain any timezone info.
    
    try:
        start_time = datetime.fromisoformat(in_start_time)
    except (ValueError, TypeError):
        # Set a default, midnight the day before
        start_time = ((datetime.now(timezone.utc) - timedelta(days=1))
                      .replace(hour=0, minute=0, second=0, microsecond=0))

    try:
        end_time = datetime.fromisoformat(in_end_time)
    except (ValueError, TypeError):
        # Set a default, now.
        end_time = datetime.now(timezone.utc)

    if end_time < start_time:
        # In case they're incorrectly entered.
        temp_time = start_time
        start_time = end_time
        end_time = temp_time
       
    loc_placeholders = ", ".join(["?" for _ in locations])
    
    query_string = f"""SELECT t.timestamp_utc,
                              t.temp_c,
                              s.location
                       FROM
                       (SELECT timestamp_utc, station_id, temp_c
                       FROM temperature
                       UNION ALL
                       SELECT timestamp_utc, station_id, temp_c
                       FROM meteoTemps) AS t
                       INNER JOIN stations s
                       ON t.station_id = s.station_id
                       AND s.from_timestamp_utc < t.timestamp_utc
                       AND COALESCE(s.to_timestamp_utc, datetime('now')) >= t.timestamp_utc
                       WHERE location IN ({loc_placeholders})
                       AND t.timestamp_utc BETWEEN ? AND ?
                       AND t.temp_c > -30 """

    # Need the -30 cutoff as there appear to be the occasional misreadings
    # down to super low temperatures. Is the ORDER BY needed?
    # seems to work without, or is that only because the data is naturally
    # ordered that way, when partitioned by location? Saves a lot of query effort.

    query_params = (*locations, start_time.timestamp(), end_time.timestamp())
    
    df = pandas.read_sql_query(query_string,
                               get_db(),
                               parse_dates=["timestamp_utc"],
                               params=query_params)

    # Add timezone info, and then convert to local time.
    df["timestamp_utc"] = (df["timestamp_utc"]
                           .dt.tz_localize("utc")
                           .dt.tz_convert("Europe/Berlin"))

    
    
    fig = px.line(df,
                  x="timestamp_utc",
                  y="temp_c",                  
                  color="location",
                  template=plot_template,
                  title=None)

    if mobile:
        # Doesn't appear possible to disable this in the theme.
        fig.update_layout(yaxis_title=None)
    else:
        fig.update_layout(yaxis_title="Temperature °C")

    fig.update_layout(xaxis_title="Timestamp (UTC)")

    rendered_chart = fig.to_html(include_plotlyjs=False,
                                  full_html=False,
                                  div_id="mainchart",
                                  config={'staticPlot': mobile})
                                  

    datetime_local_value_format = "%Y-%m-%dT%H:%M"

    # create a dict of all locations and if they're already selected.
    location_dict = dict(zip(all_locations, ["checked" if _ in location else None for _ in all_locations]))

    
    checked_view = ["checked", None]
    if not mobile:
       checked_view.reverse() 

    view_type = tuple(zip(["mobile", "desktop"], ["true", "false"], checked_view))
    
    return render_template("history.html",
                           chart=rendered_chart,
                           start_time=start_time.strftime(datetime_local_value_format),
                           end_time=end_time.strftime(datetime_local_value_format),
                           location_dict=location_dict,
                           view_type=view_type)

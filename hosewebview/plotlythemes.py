import plotly.graph_objects as go
import plotly.io as pio

# https://www.nelsontang.com/blog/2021-08-01-build-your-first-plotly-template
# how to do axes: https://plotly.com/python/axes/

# probably need to understand this: https://plotly.com/python/figure-structure/

# Doesn't seem like you can move the yaxis title 'inside' the plot
# so have the cheat and re-create it as an annotation.
pio.templates["light_mobile"] = go.layout.Template(
    layout = {"title": {"font": {"size": 20}},
              "xaxis": {"automargin": "bottom"},
              "legend": {"orientation": "v",
                         "yanchor": "bottom",
                         "y": 0,
                         "yref": "container",
                         "xanchor": "left",
                         "x": 0.01,
                         "title": "Location"},
              "yaxis": {"ticklabelposition": "inside"},
              "margin": {"l": 1,
                          "r": 1},
              "annotations": [{"name": "fake_yaxis_title",
                               "text": "Temperature °C",
                               "xref": "x domain",
                               "yref": "y domain",
                               "textangle": -90,
                               "x":0.05,
                               "y": 0.5,
                               "showarrow": False}]
              },
    data = {"scatter": [go.Scatter(
        marker = {"line": {"color": "red"}})
                        ]}
)
    

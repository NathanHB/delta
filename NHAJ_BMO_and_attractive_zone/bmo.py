import sys
import flask
import json
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import dateutil as du


class Bmo():
    def _make_dataframe_from_csv(filename):
        df = pd.read_csv(filename)
        return df

    def __init__(self, application=None):

        self.main_layout = html.Div([
            html.H4('Polotical candidate voting pool analysis'),
            html.P("Select a candidate:"),
            dcc.RadioItems(
                id='candidate',
                options=["Joly", "Coderre", "Bergeron"],
                value="Coderre",
                inline=True
            ),
            dcc.Graph(id="graph"), ])

        self.bmo_2020 = Bmo._make_dataframe_from_csv("data/MOB_2020.csv")
        self.bmo_2019 = Bmo._make_dataframe_from_csv("data/MOB_2019.csv")

        self.bmos = self.bmo_2019.append(self.bmo_2020)
        self.departements = json.load(
            open("data/departements-avec-outre-mer.geojson"))

        self.app.callback(Output('graph', 'figure'), Input(
            'candidate', 'value'))(self.display_choropleth)

        if application:
            self.app = application
            # application should have its own layout and use self.main_layout as a page or in a component
        else:
            self.app = dash.Dash(__name__)
            self.app.layout = self.main_layout

    def display_choropleth(self, candidate):
        data_grouped = self.bmos.groupby(
            ["Dept", "annee"]).agg({"xmet": np.sum, "met": np.sum})
        data_grouped = data_grouped.reset_index()

        fig = px.choropleth_mapbox(
            data_grouped,
            geojson=self.departements,
            locations="Dept",
            featureidkey="properties.code",  # join keys
            color="met",
            color_continuous_scale="Viridis",
            mapbox_style="carto-positron",
            zoom=4.6,
            center={"lat": 47, "lon": 2},
            opacity=0.5,
            animation_frame="annee")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

        return fig


if __name__ == '__main__':
    nrg = Bmo()
    nrg.app.run_server(debug=True, port=8051)

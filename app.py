# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from datetime import datetime
import mobitools as mobi
import pandas as pd
from credentials import *

from plots import * 
from helpers import *

#######################################################################################
#
#  SETUP
#
#######################################################################################

#load data
df = mobi.system.prep_sys_df('./Mobi_System_Data.csv')




    

#######################################################################################
#
#  LAYOUT
#
#######################################################################################
    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Let's copy https://github.com/plotly/dash-sample-apps/blob/master/apps/dash-oil-and-gas/
app.layout = html.Div(id="mainContainer",children=[
    html.H1(children='Vancouver Bikeshare Explorer'),

    
    
    
    html.Div(children='''
        Click on a day or select a range of days to see details.
    '''),

    

    
    
    html.Div(id='row1_container', className="simple_container", children=[
    
        html.Div(className="pretty_container", children=[

            dcc.Graph(
                id='timeseries-graph',
                figure=make_timeseries_fig(df) 
            )
        ])
    ]),
    
    html.Div(id='row2_container', className="simple_container", children=[
    
        html.Div(id='filter-div', className="pretty_container row", children=[
            html.Button('Reset', id='map-button'),
            
            dcc.Dropdown(id='filter-dropdown',
                options=[
                    {'label': 'Annual Standard', 'value': '365S'},
                    {'label': 'Annual Plus', 'value': '365P'},
                    {'label': 'Daily', 'value': '24h'},
                    {'label': 'Monthly', 'value': '90d'}
                ],
                multi=True,
                value=['365S','365P','24h','90d']
            ),  
        
        html.Button('Filter', id='filter-button')
    ]),
        
        
        
        html.Div(id='map_container', className="pretty_container row", children=[
            
            html.Div(id='map-state', children="stations"),
            
            dcc.Graph(
                id='map-graph',
                figure=make_station_map()  
            )
        ]),

        html.Div(id='daily_container', className="pretty_container row", children=[
            dcc.Graph(
                id='daily-graph',
                figure=make_daily_fig()
                )
        ]),
        
#        html.Div(id='trips_container', className="pretty_container row", children=[
#             dcc.Graph(
#                 id='trips-graph',
#                 figure=make_trips_map()
#                 )
#        ])
    ])
])



#######################################################################################
#
#  CALLBACKS
#
#######################################################################################
@app.callback([Output('timeseries-graph','figure'), Output('map-graph','figure'), 
               Output('daily-graph','figure'), Output('map-state','children')],
              [Input('timeseries-graph','clickData'), 
               Input('timeseries-graph','selectedData'), 
               Input('map-graph','clickData'),
               Input('map-button','n_clicks'),
               Input('filter-button','n_clicks')],
              [State('timeseries-graph','figure'), State('daily-graph','figure'), 
               State('filter-dropdown','value'), State('map-state','children')])
def choose_date_range(clickData, selectedData, map_clickData, map_button_nclicks, filter_button_nclicks,
                      timeseries_graph_figure, daily_graph_figure, filter_dropdown_values, map_state):
    print(dash.callback_context.triggered)  # last triggered
    print(dash.callback_context.inputs)     # all triggered
    #print(dash.callback_context.states)

    if dash.callback_context.triggered[0]['value'] == None:
        raise Exception
    
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        date = clickData['points'][0]['x']
        ddf = filter_ddf(df,date=date, stations=None, cats=filter_dropdown_values)
        return  make_timeseries_fig(df,date), make_station_map(ddf), make_daily_fig(ddf), 'stations'
    
    elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        date = (selectedData['points'][0]['x'],selectedData['points'][-1]['x'])
        ddf = filter_ddf(df,date=date, stations=None, cats=filter_dropdown_values)
        return  make_timeseries_fig(df,date), make_station_map(ddf), make_daily_fig(ddf), 'stations'
    
    elif dash.callback_context.triggered[0]['prop_id'] == 'map-graph.clickData':
        try:
            date = dash.callback_context.inputs['timeseries-graph.clickData']['points'][0]['x']
        except:
            date = (selectedData['points'][0]['x'],selectedData['points'][-1]['x'])
        station = map_clickData['points'][0]['text'].split('<')[0].strip()
        ddf = filter_ddf(df,date=date, stations=[station], cats=filter_dropdown_values)
        return timeseries_graph_figure, make_trips_map(ddf), daily_graph_figure, 'trips'
    
    elif dash.callback_context.triggered[0]['prop_id'] == 'map-button.n_clicks':
        try:
            date = dash.callback_context.inputs['timeseries-graph.clickData']['points'][0]['x']
        except:
            date = (selectedData['points'][0]['x'],selectedData['points'][-1]['x'])
        ddf = filter_ddf(df,date=date, stations=None, cats=filter_dropdown_values)
        return  timeseries_graph_figure, make_station_map(ddf), daily_graph_figure, 'stations'
    
    elif dash.callback_context.triggered[0]['prop_id'] == 'filter-button.n_clicks':
        print(filter_dropdown_values)
        try:
            date = dash.callback_context.inputs['timeseries-graph.clickData']['points'][0]['x']
        except:
            date = (selectedData['points'][0]['x'],selectedData['points'][-1]['x'])
        stations = [dash.callback_context.inputs['map-graph.clickData']['points'][0]['text'].split('<')[0].strip()]
        ddf = filter_ddf(df,date=date, stations=stations, cats=filter_dropdown_values)
        
        return  timeseries_graph_figure, make_map(df=ddf,state=map_state,switch=False), make_daily_fig(ddf), map_state 
  
        
        

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8051)

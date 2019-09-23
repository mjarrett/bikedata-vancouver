# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from datetime import datetime
import mobitools as mobi
import pandas as pd
from credentials import *

from plots import * 
from helpers import *
from callbacks import *

#######################################################################################
#
#  SETUP
#
#######################################################################################

#load data
df = mobi.system.prep_sys_df('./Mobi_System_Data.csv')
thdf = mobi.system.make_thdf(df)

startdate = thdf.index[0]
enddate = thdf.index[-1]

    

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

            
            dcc.DatePickerRange(
                id='datepicker',
                min_date_allowed=startdate,
                max_date_allowed=enddate,
                start_date=datetime(2019,3,15),
                end_date=datetime(2019,3,16)
            ),
            html.Button('Go', id='date-button'),
            
            dcc.Graph(
                id='timeseries-graph',
                figure=make_timeseries_fig(thdf) 
            )
            
        ])
    ]),
    
    html.Div(id='row2_container', className="simple_container", children=[
    
        html.Div(id='filter-div', className="pretty_container row", children=[
            html.Button('Reset', id='reset-button'),
            
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

@app.callback(Output('timeseries-graph','figure'),
              [Input('date-button','n_clicks')],
              [State('timeseries-graph','figure'), 
               State('datepicker','start_date'), 
               State('datepicker','end_date')
              ]
             )
def timeseries_callback(nclicks,ts_graph, start_date, end_date ):
    
    print("trigger: ",dash.callback_context.triggered)  # last triggered
    print("inputs : ",dash.callback_context.inputs)     # all triggered
    #print("states : ",dash.callback_context.states)
    
#     print(start_date, end_date)
    
    if start_date != end_date:
        date = (start_date[:10], end_date[:10])
    else:
        date = start_date[:10]
        
    return make_timeseries_fig(thdf,date)


@app.callback([Output('datepicker','start_date'), Output('datepicker','end_date')],
              [Input('timeseries-graph','clickData'), Input('timeseries-graph','selectedData')]
             )
def update_dates_from_graph(clickData, selectedData):
    if clickData is not None:
        date = clickData['points'][0]['x']
        return date, date
    elif selectedData is not None:
        dates = [x['x'] for x in selectedData['points'] ]
        print(dates)
        return (dates[0], dates[-1])
    
        
    


@app.callback(Output('map-graph','figure'),
              [Input('date-button','n_clicks')],
              [State('datepicker','start_date'), 
               State('datepicker','end_date'),
               State('filter-dropdown','value')
              ]
             )
def map_callback(nclicks,start_date, end_date, filter_values):
    if start_date != end_date:
        date = (start_date[:10], end_date[:10])
    else:
        date = start_date[:10]
        
    ddf = filter_ddf(df,date=date, stations=None, cats=filter_values)
    return  make_station_map(ddf)


@app.callback(Output('daily-graph','figure'),
              [Input('date-button','n_clicks')],
              [State('datepicker','start_date'), 
               State('datepicker','end_date'),
               State('filter-dropdown','value')
              ]
             )
def daily_fig_callback(nclicks,start_date, end_date, filter_values):
    if start_date != end_date:
        date = (start_date[:10], end_date[:10])
    else:
        date = start_date[:10]
        
    ddf = filter_ddf(df,date=date, stations=None, cats=filter_values)

    return make_daily_fig(ddf)
    
    
# @app.callback([Output('timeseries-graph','figure'), Output('map-graph','figure'), 
#                Output('daily-graph','figure'), Output('map-state','children')],
#               [Input('timeseries-graph','clickData'), 
#                Input('timeseries-graph','selectedData'), 
#                Input('map-graph','clickData'),
#                Input('reset-button','n_clicks'),
#                Input('filter-button','n_clicks')],
#               [State('timeseries-graph','figure'), State('daily-graph','figure'), 
#                State('filter-dropdown','value'), State('map-state','children')])
# def main_callback(clickData, selectedData, map_clickData, map_button_nclicks, filter_button_nclicks,
#                       timeseries_graph_figure, daily_graph_figure, filter_dropdown_values, map_state):
#     print("trigger: ",dash.callback_context.triggered)  # last triggered
#     print("inputs : ",dash.callback_context.inputs)     # all triggered
#     #print(dash.callback_context.states)

#     if dash.callback_context.triggered[0]['value'] == None:
#         raise PreventUpdate
    
#     if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
#         return timeseries_clickdata_callback(dash.callback_context, df, thdf)
        
    
#     elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
#         return timeseries_selectdata_callback(dash.callback_context, df, thdf)

    
#     elif dash.callback_context.triggered[0]['prop_id'] == 'map-graph.clickData':
#         return map_click_callback(dash.callback_context, df, thdf)
    
#     elif dash.callback_context.triggered[0]['prop_id'] == 'reset-button.n_clicks':
#         return reset_button_callback(dash.callback_context, df, thdf)
    
#     elif dash.callback_context.triggered[0]['prop_id'] == 'filter-button.n_clicks':
#         return filter_button_callback(dash.callback_context,df, thdf)
  
        
        

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8051)

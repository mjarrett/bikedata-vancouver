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




    
    html.Div(id='row1_container', className="simple_container", children=[
    
        html.Div(className="pretty_container", children=[
            html.Div(children=[
                html.Span("Pick a date or select a range of days to see details."),
                ]),
            dcc.DatePickerRange(
                id='datepicker',
                min_date_allowed=startdate,
                max_date_allowed=enddate,
                initial_visible_month = '2018-01-01'
                #start_date=datetime(2019,3,15),
                #end_date=datetime(2019,3,16)
            ),
            html.Button('Go', id='go-button'),
            
                
                
            dcc.Graph(
                id='timeseries-graph',
                figure=make_timeseries_fig(thdf) 
            ),
            
        ]),
    ]),
    
    html.Div(id='row2_container', className="simple_container", children=[
    
        html.Div(id='filter-div', className="pretty_container row", children=[
#             html.Button('Reset', id='reset-button'),
            
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
            
            dcc.RadioItems(
                id='stations-radio',
                options=[
                    {'label': 'Trip Start', 'value': 'start'},
                    {'label': 'Trip End', 'value': 'stop'},
                    {'label': 'Both', 'value': 'both'}
                ],
                value='start',
                labelStyle={'display': 'inline-block'}
            ),  
        
            html.Button('Filter', id='filter-button')
    ]),
        
        
        
        html.Div(id='map_container', className="pretty_container row", children=[
            
            html.Div(id='map-state', children="stations", style={'display':'none'}),
                
            
            html.Div(id='map-meta-div',style={'display':'none'}, children=[
                html.A(children="<", id='map-return-link', title="Return to station map")
                
            ]),
            
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
        

    ])
])



#######################################################################################
#
#  CALLBACKS
#
#######################################################################################

@app.callback(Output('timeseries-graph','figure'),
              [Input('go-button','n_clicks')],
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
    
    if nclicks is None:
        raise PreventUpdate
        
    if start_date != end_date:
        date = (start_date[:10], end_date[:10])
    else:
        date = start_date[:10]
        
    return make_timeseries_fig(thdf,date)


@app.callback([Output('datepicker','start_date'), Output('datepicker','end_date'),
               Output('datepicker','initial_visible_month'), Output('go-button','style')],
              [Input('timeseries-graph','clickData'), Input('timeseries-graph','selectedData')]
             )
def update_datepicker_from_graph(clickData, selectedData):
    
    buttonstyle = {'background-color':maincolor,
                   'color':'white'
                  }
    
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        date = clickData['points'][0]['x']
        return (date, date, date,buttonstyle)
    elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        dates = [x['x'] for x in selectedData['points'] ]
        print(dates)
        return (dates[0], dates[-1],dates[0],buttonstyle)
    
    else:
        raise PreventUpdate    
    
    

# Map and daily plot go together
@app.callback([Output('map-graph','figure'), Output('daily-graph','figure'),
               Output('map-state','children'), Output('map-meta-div','style')],
              [Input('go-button','n_clicks'),
               Input('map-graph','clickData'), 
               Input('map-return-link','n_clicks'),
               Input('filter-button','n_clicks')],
              [State('datepicker','start_date'), 
               State('datepicker','end_date'),
               State('filter-dropdown','value'),
               State('stations-radio','value'),
               State('map-state','children')]
             )
def map_daily_callback(go_nclicks, map_clickData, link_nclicks, filter_nclicks, start_date, end_date, filter_values, radio_value, map_state):
    
    print("trigger: ",dash.callback_context.triggered)  # last triggered
    print("inputs : ",dash.callback_context.inputs)     # all triggered
    print("states : ",dash.callback_context.states)

    
    link_style_show = {'display':'inline'}
    link_style_hide = {'display':'none'}
    
    if go_nclicks is None and map_clickData is None and link_nclicks is None:
        raise PreventUpdate
    
    if start_date != end_date:
        date = (start_date[:10], end_date[:10])
    else:
        date = start_date[:10]
        
    
    
    
    if dash.callback_context.triggered[0]['prop_id'] == 'go-button.n_clicks':    
        ddf = filter_ddf(df,date=date, stations=None, cats=filter_values, direction=radio_value)
        return  make_station_map(ddf,direction=radio_value), make_daily_fig(ddf),'stations', link_style_hide
    
    elif dash.callback_context.triggered[0]['prop_id'] == 'map-graph.clickData':
        station = map_clickData['points'][0]['text'].split('<')[0].strip()
        ddf = filter_ddf(df,date=date, stations=[station], cats=filter_values, direction=radio_value)
        return  make_trips_map(ddf,direction=radio_value), make_daily_fig(ddf), 'trips', link_style_show
    
    elif dash.callback_context.triggered[0]['prop_id'] == 'map-return-link.n_clicks':
        ddf = filter_ddf(df,date=date, stations=None, cats=filter_values, direction=radio_value)
        return  make_station_map(ddf,direction=radio_value), make_daily_fig(ddf), 'stations', link_style_hide
    
    elif dash.callback_context.triggered[0]['prop_id'] == 'filter-button.n_clicks':
        if map_state == 'stations':
            ddf = filter_ddf(df,date=date, stations=None, cats=filter_values, direction=radio_value)
            return  make_station_map(ddf,direction=radio_value), make_daily_fig(ddf), 'stations', link_style_hide
        elif map_state == 'trips':
            station = dash.callback_context.inputs['map-graph.clickData']['points'][0]['text'].split('<')[0].strip()
            ddf = filter_ddf(df,date=date, stations=[station], cats=filter_values, direction=radio_value)
            return make_trips_map(ddf,direction=radio_value), make_daily_fig(ddf), 'trips', link_style_show
    
    else:
        raise PreventUpdate
        


    
    
    
    

        
        

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8051)

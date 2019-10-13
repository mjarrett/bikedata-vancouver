# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from datetime import datetime
import mobisys as mobi
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
df = mobi.prep_sys_df('./Mobi_System_Data.csv')
thdf = mobi.make_thdf(df)

startdate = thdf.index[0]
enddate = thdf.index[-1]

startdate_str = startdate.strftime('%b %-d %Y')
enddate_str = enddate.strftime('%b %-d %Y')

    
wdf = pd.read_csv('weather.csv',index_col=0)
wdf.index = pd.to_datetime(wdf.index)
 
n_trips = len(df)
tot_dist = df['Covered distance (m)'].sum()/1000
tot_usrs = len(set(df['Account']))

#######################################################################################
#
#  LAYOUT
#
#######################################################################################
    
external_stylesheets=[dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


header = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Link", href="#")),
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="Menu",
            children=[
                dbc.DropdownMenuItem("Entry 1"),
                dbc.DropdownMenuItem("Entry 2"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Entry 3"),
            ],
        ),
    ],
    brand="Vancouver Bikeshare Explorer",
    brand_href="#",
    sticky="top",
    color='#1e5359',
    dark=True
    )


summary_cards = dbc.Row(children=[
        
        dbc.Col([
            dbc.Row([
                
                dbc.CardDeck(style={'width':'100%'},children=[
        
                    make_card("Total Trips",f"{n_trips:,}"),
                    make_card("Total Distance Travelled",f"{int(tot_dist):,} km"),
                    make_card("Total Riders",f"{tot_usrs:,}")

                ]),
            ]),
        ]),
        
        
    ]) 


main_div = dbc.Row(className="py-5", children=[
    
         dbc.Col(className="border rounded col-2", children=[
            dbc.FormGroup([
#                 html.H4("Filter"),
                html.Strong("Filter"),
                dcc.DatePickerRange(
                    id='datepicker',
                    min_date_allowed=startdate,
                    max_date_allowed=enddate,
                    initial_visible_month = '2018-01-01',
                    minimum_nights = 0,
                    #start_date=datetime(2019,3,15),
                    #end_date=datetime(2019,3,16)
                    ),

                dbc.Tooltip("Pick a date or select a range of days to see details.",
                            target="go-button"),


    #             html.H5("Member type"),
                html.Strong("Membership Type"),
                dbc.Checklist(id='filter-dropdown',
                    options=[
                        {'label': 'Annual Standard', 'value': '365S'},
                        {'label': 'Annual Plus', 'value': '365P'},
                        {'label': 'Daily', 'value': '24h'},
                        {'label': 'Monthly', 'value': '90d'}
                    ],

                    value=['365S','365P','24h','90d']
                ),



                dbc.Button("Go    ", id='go-button', color="primary", outline=True, block=True),
            ]),
        ]),   
    
    
        
        dbc.Col(children=[
            
            html.Span(html.Em(f"Data available from {startdate_str} to {enddate_str}")),
            dcc.Graph(
                id='timeseries-graph',
                figure=make_timeseries_fig(thdf),
                style={'height':'100%','width':'100%'}
            ),        
        ]),
        

                
                

    ]) 

detail_div = dbc.Row(id='detail_div', className="border", children=make_detail_div(df,wdf,df) ) 



body = dbc.Container(id="mainContainer",children=[
    
    summary_cards,
    
    main_div,
    
    detail_div
    
])  

app.layout = html.Div([header,body])
                                             
#######################################################################################
#
#  CALLBACKS
#
#######################################################################################

# @app.callback(Output('timeseries-graph','figure'),
#               [Input('go-button','n_clicks')],
#               [State('timeseries-graph','figure'), 
#                State('datepicker','start_date'), 
#                State('datepicker','end_date')
#               ]
#              )
# def timeseries_callback(nclicks,ts_graph, start_date, end_date ):
    
#     print("trigger: ",dash.callback_context.triggered)  # last triggered
#     print("inputs : ",dash.callback_context.inputs)     # all triggered
#     #print("states : ",dash.callback_context.states)
    
# #     print(start_date, end_date)
    
#     if nclicks is None:
#         raise PreventUpdate
    
#     if end_date is None:
#         date = start_date[:10] 
#     if start_date != end_date:
#         date = (start_date[:10], end_date[:10])
#     else:
#         date = start_date[:10]
        
#     return make_timeseries_fig(thdf,date)


# @app.callback([Output('datepicker','start_date'), Output('datepicker','end_date'),
#                Output('datepicker','initial_visible_month')],
#               [Input('timeseries-graph','clickData'), Input('timeseries-graph','selectedData')]
#              )
# def update_datepicker_from_graph(clickData, selectedData):
    
#     if clickData is None and selectedData is None:
#         raise PreventUpdate
    
#     if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
#         date = clickData['points'][0]['x']
#         return (date, date, date)
#     elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
#         dates = [x['x'] for x in selectedData['points'] ]
#         print(dates)
#         return (dates[0], dates[-1],dates[0])
    
#     else:
#         raise PreventUpdate    
    

# @app.callback(Output('go-button','outline'),
#               [Input('datepicker','start_date'), Input('datepicker','end_date')]
#              )
# def activate_go_button(a,b):
#     if a is None and b is None:
#         raise PreventUpdate
#     return False




        
# # Map and daily plot go together
# @app.callback([Output('map-graph','figure'), Output('daily-graph','figure'),
#                Output('map-state','children'), Output('map-meta-div','style'),
#                Output('detail-cards','children')],
#               [Input('go-button','n_clicks'),
#                Input('map-graph','clickData'), 
#                Input('map-return-link','n_clicks'),
#                Input('go-button','n_clicks'),
#                Input('stations-radio','value')],
#               [State('datepicker','start_date'), 
#                State('datepicker','end_date'),
#                State('filter-dropdown','value'),
#                State('map-state','children')]
#              )
# def map_daily_callback(go_nclicks, map_clickData, link_nclicks, filter_nclicks, radio_value, start_date, end_date, filter_values, map_state):
    
#     print("trigger: ",dash.callback_context.triggered)  # last triggered
#     print("inputs : ",dash.callback_context.inputs)     # all triggered
#     print("states : ",dash.callback_context.states)

    
#     link_style_show = {'display':'inline'}
#     link_style_hide = {'display':'none'}
    
#     if go_nclicks is None and map_clickData is None and link_nclicks is None:
#         raise PreventUpdate
    
#     if start_date != end_date:
#         date = (start_date[:10], end_date[:10])
#     else:
#         date = start_date[:10]
        
    
    
    
#     if dash.callback_context.triggered[0]['prop_id'] == 'go-button.n_clicks':    
#         ddf = filter_ddf(df,date=date, stations=None, cats=filter_values, direction=radio_value)
#         return  make_station_map(ddf,direction=radio_value), make_daily_fig(ddf),'stations', link_style_hide, make_detail_cards(ddf,wdf)
    
#     elif dash.callback_context.triggered[0]['prop_id'] == 'stations-radio.value':   
#         if map_state == 'stations':
#             ddf = filter_ddf(df,date=date, stations=None, cats=filter_values, direction=radio_value)
#             return  make_station_map(ddf,direction=radio_value), make_daily_fig(ddf), 'stations', link_style_show, make_detail_cards(ddf,wdf)
#         elif map_state == 'trips':
#             station = map_clickData['points'][0]['text'].split('<')[0].strip()
#             ddf = filter_ddf(df,date=date, stations=[station], cats=filter_values, direction=radio_value)
#             return  make_trips_map(ddf,direction=radio_value), make_daily_fig(ddf), 'trips', link_style_show, make_detail_cards(ddf,wdf)
    
#     elif dash.callback_context.triggered[0]['prop_id'] == 'map-graph.clickData':
#         station = map_clickData['points'][0]['text'].split('<')[0].strip()
#         ddf = filter_ddf(df,date=date, stations=[station], cats=filter_values, direction=radio_value)
#         return  make_trips_map(ddf,direction=radio_value), make_daily_fig(ddf), 'trips', link_style_show, make_detail_cards(ddf,wdf)
    
#     elif dash.callback_context.triggered[0]['prop_id'] == 'map-return-link.n_clicks':
#         ddf = filter_ddf(df,date=date, stations=None, cats=filter_values, direction=radio_value)
#         return  make_station_map(ddf,direction=radio_value), make_daily_fig(ddf), 'stations', link_style_hide, make_detail_cards(ddf,wdf)
    
#     elif dash.callback_context.triggered[0]['prop_id'] == 'go-button.n_clicks':
#         if map_state == 'stations':
#             ddf = filter_ddf(df,date=date, stations=None, cats=filter_values, direction=radio_value)
#             return  make_station_map(ddf,direction=radio_value), make_daily_fig(ddf), 'stations', link_style_hide, make_detail_cards(ddf,wdf)
#         elif map_state == 'trips':
#             station = dash.callback_context.inputs['map-graph.clickData']['points'][0]['text'].split('<')[0].strip()
#             ddf = filter_ddf(df,date=date, stations=[station], cats=filter_values, direction=radio_value)
#             return make_trips_map(ddf,direction=radio_value), make_daily_fig(ddf), 'trips', link_style_show, make_detail_cards(ddf,wdf)
    
#     else:
#         raise PreventUpdate
        


    
    
    
    

        
        

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8051)

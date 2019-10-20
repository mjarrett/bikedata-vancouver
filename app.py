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
import urllib
import json

from credentials import *
from plots import * 
from helpers import *
from layouts import *

#######################################################################################
#
#  SETUP
#
#######################################################################################

#load data
#df = prep_sys_df('./Mobi_System_Data.csv')
log("==================")
log("Loading data")
df = pd.read_csv('./data/Mobi_System_Data_Prepped.csv')
memtypes = set(df['Membership Simple'])
df.Departure = pd.to_datetime(df.Departure)
df.Return = pd.to_datetime(df.Return)
  
thdf = mobi.make_thdf(df)

startdate = thdf.index[0]
enddate = thdf.index[-1]

startdate_str = startdate.strftime('%b %-d %Y')
enddate_str = enddate.strftime('%b %-d %Y')

log("Loading weather")  
wdf = pd.read_csv('weather.csv',index_col=0)
wdf.index = pd.to_datetime(wdf.index)
 
n_days = (enddate-startdate).days
n_trips = len(df)
n_trips_per_day = n_trips / n_days
tot_dist = df['Covered distance (m)'].sum()/1000
dist_per_trip = tot_dist/n_trips
tot_usrs = len(set(df['Account']))
tot_usrs_per_day = tot_usrs / n_days
tot_time = df['Duration (sec.)'].sum() - df['Stopover duration (sec.)'].sum()

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

footer = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Link", href="#")),
        
    ],
    brand="Vancouver Bikeshare Explorer",
    brand_href="#",
    sticky="bottom",
    color='#1e5359',
    dark=False
    )

summary_cards = dbc.Row(className='p-3 justify-content-center', children=[
        
        dbc.Col([
            dbc.Row(children=[
                
                
                dbc.CardDeck(className="justify-content-center", style={'width':'100%'},children=[
                    make_card("Total Trips",f"{n_trips:,}",color='primary'),
                    make_card("Total Distance Travelled",f"{int(tot_dist):,} km",color='info'),
                    make_card("Total Members",f"{tot_usrs:,}",color='success'),
                    make_card("Total Trip Time",f"{int(tot_time/(60*60)):,} hours",color='warning')

                ]),
            ]),
        ]),
        
        
    ]) 

summary_jumbo = dbc.Jumbotron(
    [
        html.H1("BikeData BC", className="display-3"),
        html.P(
            "This tool makes Mobi's trip data available for analysis",
            className="lead",
        ),
        html.Hr(className="my-2"),
        html.P(
            f"Data available from {startdate_str} to {enddate_str}"
        ),
        html.P(dbc.Button("Learn more", color="primary"), className="lead"),
    ]
)

filter_data = json.dumps({'date':None, 'cats':None, 'stations':None, 'direction':'start',
                          'date2':None,'cats2':None,'stations2':None,'direction2':'start'})

main_div = dbc.Row(children=[
    dbc.Col([
        
        
        dbc.Row(className='py-2',children=[

            dbc.Col(children=[

                dbc.Card(className="shadow justify-content-center",children=[
                    dbc.CardHeader(),
                    dbc.CardBody([
                        dcc.Graph(
                            id='timeseries-graph',
                            figure=make_timeseries_fig(thdf),
                            style={'height':'100%','width':'100%'}
                        ),   
                        dbc.Button("Explore Data", id='date-button',size='lg',color="primary", className="mr-1")
                    ]),
                ]),
            ]),
        ]),        
        
        #dbc.Row(className="justify-content-center", children=[
        #    dbc.Button("Explore Data", id='date-button',size='lg',color="primary", className="mr-1")
        #]),
        

        dbc.Modal(size='md', id='date-modal', children=[
            dbc.ModalHeader("Pick a date or date range"),
            dbc.ModalBody([
                html.Div(id="filter-meta-div", children=filter_data, className='d-none'),

                    dbc.FormGroup([
                                dcc.DatePickerRange(
                                    id='datepicker',
                                    min_date_allowed=startdate,
                                    max_date_allowed=enddate,
                                    #initial_visible_month = '2018-01-01',
                                    minimum_nights = 0,
                                    clearable = True,
                                ),


                                dbc.Checklist(id='filter-dropdown',

                                    options=[{'label':memtype,'value':memtype} for memtype in memtypes],
                                    value=list(memtypes)
                                ),

                    ]),
                    dbc.Tooltip("Pick a date or select a range of days to see details.",
                                            target="go-button"),
                    dbc.Button("Go    ", id='go-button', color="primary", outline=True, block=True),
            ])
        ]),
        
        
        dbc.Modal(size='md', id='date-modal2', children=[
            dbc.ModalHeader("Pick a date or date range"),
            dbc.ModalBody([
                    dbc.FormGroup(children=[
                        dcc.DatePickerRange(
                            id='datepicker2',
                            min_date_allowed=startdate,
                            max_date_allowed=enddate,
                            initial_visible_month = '2018-01-01',
                            minimum_nights = 0,
                            clearable = True,
                            ),

                        dbc.Checklist(id='filter-dropdown2',

                            options=[{'label':memtype,'value':memtype} for memtype in memtypes],
                            value=list(memtypes)
                        ),
                    ]),
                    dbc.Tooltip("Pick a date or select a range of days to see details.",
                                            target="go-button2"),
                    dbc.Button("Go    ", id='go-button2', color="success", outline=True, block=True),
                ]) 
        ])
    ])
])

detail_div = dbc.Row(id='detail-div', className="border", children=make_detail_div(None,None) ) 
# detail_div = dbc.Row(id='detail-div', className="border", children="" )



body = dbc.Container(id="mainContainer",children=[
    
    summary_jumbo,
    
    summary_cards,
    
    main_div,
    
    detail_div,
        
])  

app.layout = html.Div([header,body,footer])
                                             
#######################################################################################
#
#  CALLBACKS
#
#######################################################################################



@app.callback(Output('timeseries-graph','figure'),
             [Input('filter-meta-div','children')]
             ) 
def timeseries_callback(filter_data):
    log('timeseries_callback')
    
    filter_data = json.loads(filter_data)
 
    return make_timeseries_fig(thdf,filter_data['date'],filter_data['date2'])


@app.callback([Output('datepicker','start_date'), Output('datepicker','end_date'),
               Output('datepicker','initial_visible_month')],
              [Input('timeseries-graph','clickData'), Input('timeseries-graph','selectedData')],
              [State("filter-meta-div",'children')]
             )
def update_datepicker_from_graph(clickData, selectedData, filter_data):
    
    if clickData is None and selectedData is None:
        raise PreventUpdate
        
    filter_data = json.loads(filter_data)
    
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        date = clickData['points'][0]['x']
        return (date, date, date)
    elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        dates = [x['x'] for x in selectedData['points'] ]
        log(dates)
        return (dates[0], dates[-1],dates[0])
    
    else:
        raise PreventUpdate    
    

@app.callback(Output('go-button','outline'),
              [Input('datepicker','start_date'), Input('datepicker','end_date')]
             )
def activate_go_button(a,b):
    if a is None and b is None:
        raise PreventUpdate
    return False



        
# Keep track of filter
@app.callback(Output("filter-meta-div",'children'),
              [Input('go-button','n_clicks'),Input('go-button2','n_clicks'),
               Input('map-graph','clickData'),Input('map-graph2','clickData'),
               Input('stations-radio','value'),Input('stations-radio2','value')],
              [State("filter-meta-div",'children'),
               State('datepicker','start_date'), 
               State('datepicker','end_date'),
               State('filter-dropdown','value'),
               State('datepicker2','start_date'), 
               State('datepicker2','end_date'),
               State('filter-dropdown2','value')]
             )
def update_filter_meta_div(n_clicks,n_clicks2,clickData,clickData2,radio_value,radio_value2, 
                           filter_data,
                           start_date,end_date,filter_values,
                           start_date2,end_date2,filter_values2):
    if clickData is None and clickData2 is None and n_clicks is None:
        raise PreventUpdate
    
    log("update_filter_meta_div")
    log("trigger: ",dash.callback_context.triggered)  # last triggered
    filter_data = json.loads(filter_data)
    
    # IF go-button is triggered, update all values
    if  dash.callback_context.triggered[0]['prop_id'] == 'go-button.n_clicks':
        date,date2 = convert_dates(start_date,end_date,start_date2,end_date2)
        
        filter_data = {'date':date, 'cats':filter_values, 'stations':None, 'direction':'start',
                          'date2':None,'cats2':filter_values2,'stations2':None,'direction2':'start'}

    # IF go-button2 is triggered, update all values
    if  dash.callback_context.triggered[0]['prop_id'] == 'go-button2.n_clicks':
        date,date2 = convert_dates(start_date,end_date,start_date2,end_date2)
        
        filter_data = {'date':date, 'cats':filter_values, 'stations':None, 'direction':'start',
                          'date2':date2,'cats2':filter_values2,'stations2':None,'direction2':'start'}

        
    # If map #1 is clicked           
    if clickData is not None:
        station = clickData['points'][0]['text'].split('<')[0].strip()
        filter_data['stations'] = [station]
        
    # If map #2 is clicked
    if clickData2 is not None:
        station2 = clickData2['points'][0]['text'].split('<')[0].strip()
        filter_data['stations2'] = [station2]
        
    # If radio1 is clicked
    if  dash.callback_context.triggered[0]['prop_id'] == 'stations-radio.value':
        if radio_value == filter_data['direction']:
            raise PreventUpdate
        else:
            filter_data['direction'] = radio_value
            
    # If radio2 is clicked
    if  dash.callback_context.triggered[0]['prop_id'] == 'stations-radio2.value':
        if radio_value2 == filter_data['direction2']:
            raise PreventUpdate
        else:
            filter_data['direction2'] = radio_value2
        
    return json.dumps(filter_data)
    
        
# Update details div
@app.callback([Output('detail-div','children'), Output('detail-div','className')],
              [Input("filter-meta-div",'children')],
             )
def daily_div_callback(filter_data):
    filter_data = json.loads(filter_data)
    
    if filter_data['date'] is None:
        raise PreventUpdate
        
    log("daily_div_callback")
    
    
    ddf = filter_ddf(df,date=filter_data['date'], 
                     stations=filter_data['stations'], 
                     cats=filter_data['cats'], 
                     direction=filter_data['direction'])
    if filter_data['date2'] is not None:
        ddf2 = filter_ddf(df,date=filter_data['date2'], 
                         stations=filter_data['stations2'], 
                         cats=filter_data['cats2'], 
                         direction=filter_data['direction2'])
    else:
        ddf2 = None
        
    trips = False if filter_data['stations'] is None else True
    trips2 = False if filter_data['stations2'] is None else True
    
    return [make_detail_div(ddf,wdf=wdf,df2=ddf2,trips=trips,trips2=trips2,
                            direction=filter_data['direction'],direction2=filter_data['direction2']),
            "border"]


  
@app.callback(Output('date-modal','is_open'),
               [Input('date-button','n_clicks'),Input('go-button','n_clicks'),
                Input('timeseries-graph','clickData'),Input('timeseries-graph','selectedData')]
              )
def toggle_date_modal(n_clicks,go_n_clicks,clickData,selectedData):

    if dash.callback_context.triggered[0]['prop_id'] == 'date-button.n_clicks':
        return True if n_clicks is not None else False
    if dash.callback_context.triggered[0]['prop_id'] == 'go-button.n_clicks':
        return False
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        return True
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        return True
        
    
@app.callback(Output('date-modal2','is_open'),
               [Input('compare-button','n_clicks'),Input('go-button2','n_clicks')]
              )
def toggle_date_modal2(n_clicks,go_n_clicks):

    if n_clicks is None and go_n_clicks is None:
        raise PreventUpdate
    if dash.callback_context.triggered[0]['prop_id'] == 'compare-button.n_clicks':
        return True
    if dash.callback_context.triggered[0]['prop_id'] == 'go-button2.n_clicks':
        return False
    
    
@app.callback(Output('data-modal','is_open'),
              [Input('data-button','n_clicks')]
             )
def open_data_modal(n_clicks):
    if n_clicks is not None:
        return True

    
    
@app.callback(Output('data-modal2','is_open'),
              [Input('data-button2','n_clicks')]
             )
def open_data_modal(n_clicks):
    if n_clicks is not None:
        return True


    
    
@app.callback(Output("download-data-button",'href'),
              [Input("download-data-button",'n_clicks')],
              [State("data-table","data")]
             )
def download_data(n_clicks,data):
    ddf = pd.DataFrame(data)
    csv_string = ddf.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string





@app.callback(Output("download-data-button2",'href'),
              [Input("download-data-button2",'n_clicks')],
              [State("data-table2","data")]
             )
def download_data2(n_clicks,data):
    ddf = pd.DataFrame(data)
    csv_string = ddf.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

        


    
    
    
    

        
        

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8051)

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
wdf = pd.read_csv('./data/weather.csv',index_col=0)
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
        html.P(dbc.Button("Learn more", id='jumbo-button', color="primary"), className="lead"),
    ]
)

filter_data = json.dumps({'date':None, 'cats':None, 'stations':None, 'direction':'start'})                          
filter_data2 = json.dumps({'date':None,'cats':None,'stations':None,'direction':'start'})

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
                html.Div(id="filter-meta-div2", children=filter_data2, className='d-none'),
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


detail_div = dbc.Row(id='detail-div', className='', children=make_detail_div())
            




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


@app.callback(Output('detail-div-status','children'),
              [Input('go-button','n_clicks')],
             )
def update_detail_status(n_clicks):
    log("**update_detail_status callback")
    log(f"n clicks: {n_clicks}")
    if n_clicks is None:
        log("d-none")
        return "d-none"
    else:
        log("")
        return ""

@app.callback(Output('detail-div-status2','children'),
              [Input('go-button2','n_clicks')]
             )
def update_detail_status2(n_clicks):
    log("**update_detail_status callback2")
    log(f"n clicks: {n_clicks}")
    if n_clicks is None:
        log("d-none")
        return "d-none"
    else:
        log("")
        return ""
    
@app.callback([Output('header-div','className'), Output('detail-cards-div','className'),
               Output('daily-div','className'), Output('map-div','className'),
               Output('memb-div','className'), Output('explore-div','className'),
               Output('header-div2','className'), Output('detail-cards-div2','className'),
               Output('daily-div2','className'), Output('map-div2','className'),
               Output('memb-div2','className'), Output('explore-div2','className')],
               #[Input('go-button','n_clicks'), Input('filter-meta-div','children'), Input('filter-meta-div2','children')]
#                [Input('go-button','n_clicks'), Input('go-button2','n_clicks')],
               [Input('detail-div-status','children'), Input('detail-div-status2','children')]
             ) 
# def toggle_div_visibility(n_clicks, filter_data, filter_data2):
def toggle_div_visibility(status, status2):

    log('**toggle_div_visibility callback')
    log(status, status2)
    
    if status == 'd-none':
        log("Hidding both")
        date_1_divs = ["d-none"]*6
        date_2_divs = ["d-none"]*6       
        
    elif status2 == 'd-none':
        log("show date1")
        date_1_divs = [""]*6
        date_2_divs = ["d-none"]*6
    else:
        log("show both")
        date_1_divs = [""]*6
        date_2_divs = [""]*6
        
    return date_1_divs + date_2_divs


@app.callback(Output('timeseries-graph','figure'),
             [Input('filter-meta-div','children'),Input('filter-meta-div2','children')]
             ) 
def timeseries_callback(filter_data,filter_data2):
    log('timeseries_callback')
    
    filter_data = json.loads(filter_data)
    filter_data2 = json.loads(filter_data2)

    return make_timeseries_fig(thdf,filter_data['date'],filter_data2['date'])


@app.callback([Output('datepicker','start_date'), Output('datepicker','end_date'),
               Output('datepicker','initial_visible_month')],
              [Input('timeseries-graph','clickData'), Input('timeseries-graph','selectedData')],
              [State("filter-meta-div",'children'),State("filter-meta-div2",'children')]
             )
def update_datepicker_from_graph(clickData, selectedData, filter_data, filter_data2):
    
    if clickData is None and selectedData is None:
        raise PreventUpdate
        
#     filter_data = json.loads(filter_data)
#     filter_data2 = json.loads(filter_data2)
    
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        date = clickData['points'][0]['x']
        return (date, date, date)
    elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        dates = [x['x'] for x in selectedData['points'] ]
        return (dates[0], dates[-1],dates[0])
    
    else:
        raise PreventUpdate    
    




        
# Keep track of filter
@app.callback(Output("filter-meta-div",'children'),
              [Input('go-button','n_clicks'),
               Input('map-graph','clickData'),
               Input('stations-radio','value')],
              [State("filter-meta-div",'children'),
               State('datepicker','start_date'), 
               State('datepicker','end_date'),
               State('filter-dropdown','value')]
             )
def update_filter_meta_div(n_clicks,clickData,radio_value, 
                           filter_data,
                           start_date,end_date,filter_values):
    if clickData is None and n_clicks is None:
        raise PreventUpdate
    
    log("update_filter_meta_div")
    log("trigger: ",dash.callback_context.triggered)  # last triggered
    filter_data = json.loads(filter_data)
    
    # IF go-button is triggered, update all values
    if  dash.callback_context.triggered[0]['prop_id'] == 'go-button.n_clicks':
        date = convert_dates(start_date,end_date)
         
        filter_data = {'date':date, 'cats':filter_values, 'stations':None, 'direction':'start'}

      
    # If map #1 is clicked           
    if clickData is not None:
        station = clickData['points'][0]['text'].split('<')[0].strip()
        filter_data['stations'] = [station]
       
        
    # If radio1 is clicked
    if  dash.callback_context.triggered[0]['prop_id'] == 'stations-radio.value':
        if radio_value == filter_data['direction']:
            raise PreventUpdate
        else:
            filter_data['direction'] = radio_value
            
        
    return json.dumps(filter_data)


# Keep track of filter2
@app.callback(Output("filter-meta-div2",'children'),
              [Input('go-button2','n_clicks'),
               Input('map-graph2','clickData'),
               Input('stations-radio2','value')],
              [State("filter-meta-div2",'children'),
               State('datepicker2','start_date'), 
               State('datepicker2','end_date'),
               State('filter-dropdown2','value')]
             )
def update_filter_meta_div2(n_clicks,clickData,radio_value, 
                           filter_data,
                           start_date,end_date,filter_values):
    if clickData is None and n_clicks is None:
        raise PreventUpdate
    
    log("update_filter_meta_div2")
    log("trigger: ",dash.callback_context.triggered)  # last triggered
    filter_data = json.loads(filter_data)
    
    # If go-butto2 is triggered, update all values
    if  dash.callback_context.triggered[0]['prop_id'] == 'go-button2.n_clicks':
        date = convert_dates(start_date,end_date)
        
        filter_data = {'date':date, 'cats':filter_values, 'stations':None, 'direction':'start'}

      
    # If map2 is clicked           
    if clickData is not None:
        station = clickData['points'][0]['text'].split('<')[0].strip()
        filter_data['stations'] = [station]
       
        
    # If radio2 is clicked
    if  dash.callback_context.triggered[0]['prop_id'] == 'stations-radio2.value':
        if radio_value == filter_data['direction']:
            raise PreventUpdate
        else:
            filter_data['direction'] = radio_value
            
        
    return json.dumps(filter_data)
        
# Update details div
@app.callback([Output("date-header", 'children'), Output('modal-div','children'),
               Output('detail-cards-div','children'),Output('daily-graph','figure'),
               Output('map-div','children'),Output('memb-graph','figure')],
              [Input("filter-meta-div",'children')],
             )
def daily_div_callback(filter_data):
    filter_data = json.loads(filter_data)
    suff = ""
    
    if filter_data['date'] is None:
        raise PreventUpdate
        
    log("daily_div_callback")
    
    ddf = filter_ddf(df,date=filter_data['date'], 
                     stations=filter_data['stations'], 
                     cats=filter_data['cats'], 
                     direction=filter_data['direction'])

        
    trips = False if filter_data['stations'] is None else True
    direction = filter_data['direction']
    date = date_2_str(filter_data['date'])
    
    data_modal = make_data_modal(ddf, suff=suff)
    detail_cards_div_children=make_detail_cards(ddf,wdf,suff=suff)
    daily_fig = make_daily_fig(ddf,suff=suff)
    map_div = make_map_div(ddf,trips,direction,suff)
    memb_fig = make_memb_fig(ddf,suff=suff)
    
    return [date,data_modal,detail_cards_div_children,daily_fig,map_div,memb_fig]


# Update details div2
@app.callback([Output('date-header2','children'),Output('modal-div2','children'),
               Output('detail-cards-div2','children'),Output('daily-graph2','figure'),
               Output('map-div2','children'),Output('memb-graph2','figure')],
              [Input("filter-meta-div2",'children')],
             )
def daily_div_callback2(filter_data):
    filter_data = json.loads(filter_data)
    suff = "2"
    
    if filter_data['date'] is None:
        raise PreventUpdate
        
    log("daily_div_callback2")
    
    ddf = filter_ddf(df,date=filter_data['date'], 
                     stations=filter_data['stations'], 
                     cats=filter_data['cats'], 
                     direction=filter_data['direction'])

        
    trips = False if filter_data['stations'] is None else True
    direction = filter_data['direction']
    date = date_2_str(filter_data['date'])
    
    data_modal = make_data_modal(ddf, suff=suff)
    detail_cards_div_children=make_detail_cards(ddf,wdf,suff=suff)
    daily_fig = make_daily_fig(ddf,suff=suff)
    map_div = make_map_div(ddf,trips,direction,suff)
    memb_fig = make_memb_fig(ddf,suff=suff)
    return [date,data_modal,detail_cards_div_children,daily_fig,map_div,memb_fig]


  
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
               [Input('date-button2','n_clicks'),Input('go-button2','n_clicks')]
              )
def toggle_date_modal2(n_clicks,go_n_clicks):

    if n_clicks is None and go_n_clicks is None:
        raise PreventUpdate
    if dash.callback_context.triggered[0]['prop_id'] == 'date-button2.n_clicks':
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

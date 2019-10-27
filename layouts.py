import mobisys as mobi
import numpy as np
import pandas as pd
import geopandas
import json

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

from helpers import *
from plots import *



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
#  LAYOUT FUNCTIONS
#
#######################################################################################

def make_card(title,content,subcontent=None,color='primary'):
    return dbc.Card(style={'border':'none'},className=f"justify-content-center h-100 py-2", children=[
            #dbc.CardHeader(title,style={'color':color}),
            dbc.CardBody([
                
                dbc.Row(title, className=f"text-xs font-weight-bold text-{color} text-uppercase mb-1"),
                dbc.Row(content, className=f"h5 mb-0 font-weight-bold"),
                dbc.Row(subcontent, className=f"h5 mb-0 font-weight-bold text-muted"),
                
            ])

        ])  # Card
        
def make_detail_cards(df=None,wdf=None,suff=''):
    if df is None:
        return None
    
    if suff == '':
        color = 'primary'
    elif suff == '2':
        color = 'success'
        
    start_date = df['Departure'].iloc[0].strftime('%Y-%m-%d')
    stop_date  = df['Departure'].iloc[-1].strftime('%Y-%m-%d')
    
    log(start_date,stop_date)
    
    start_date_str = df['Departure'].iloc[0].strftime('%b %d, %Y')
    stop_date_str = df['Departure'].iloc[-1].strftime('%b %d, %Y')
    
    wdf = wdf[start_date:stop_date]
    
    n_days = (df['Departure'].iloc[-1] - df['Departure'].iloc[0]).days + 1
    n_days = n_days if (n_days > 1) else 1
    
    
    n_trips = len(df)
    tot_dist = df['Covered distance (m)'].sum()/1000
    tot_usrs = len(set(df['Account']))
    avg_dist = tot_dist/n_trips
    avg_trips = n_trips/n_days
    busiest_dep = df.groupby('Departure station').size().sort_values(ascending=False).index[0]
    busiest_dep_n = df.groupby('Departure station').size().sort_values(ascending=False)[0]
    busiest_ret = df.groupby('Return station').size().sort_values(ascending=False).index[0]
    busiest_ret_n = df.groupby('Return station').size().sort_values(ascending=False)[0]
    
    avg_daily_high = wdf['Max Temp'].mean()
    avg_daily_pricip = wdf['Total Precipmm'].mean()
    

    output =  dbc.Col(style={'width':'100%'},children=[


        dbc.CardColumns([
            make_card("Total trips", f"{n_trips:,}",color=color),
            make_card("Average trip distance",f"{int(avg_dist):,} km",color=color),
            make_card("Daily high temp",f"{avg_daily_high:.1f} °C",color=color),
            make_card("Daily precipitation",f"{avg_daily_pricip:.1f} mm",color=color),


        ]),

        dbc.CardColumns([
            make_card("Busiest departure station",f"{busiest_dep}",color=color),
            make_card("Busiest return station",f"{busiest_ret}",color=color)

        ])
    ])
    
    return output


def make_data_modal(df=None, suff=""):
    if df is None:
        df = pd.DataFrame()
        outfields = []
    else:
        outfields = ['Departure','Return','Departure station','Return station','Membership Type','Covered distance (m)','Duration (sec.)']
    
    modal = dbc.Modal([
                dbc.ModalHeader("Raw Data"),
                dbc.ModalBody(children=[
                    dash_table.DataTable(
                        id=f'data-table{suff}',
                        columns=[{"name": i, "id": i} for i in outfields],
                        data=df[outfields].to_dict('records'),
                        style_table={'overflowX': 'scroll',
                                     'maxHeight': '300px'
                                    },
                    )    
                    
                ]),
                dbc.ModalFooter(
                    html.A(id=f"download-data-button{suff}", className="btn btn-primary", href="#", children=[
                        html.Span(className="fa fa-download"),
                        " Download CSV",
                    ])
                ),
            ],
            id=f"data-modal{suff}",
            size="xl",
            )
    return modal



def make_map_div(df=None,trips=False,direction='start',suff=""):
    
    return_but_class = "pull-right" if trips else "d-none pull-right"
    if suff == "":
        return_but_class = return_but_class + " " + "color-primary"
    elif suff == "2":
        return_but_class = return_but_class + " " + "color-success"
        
    return html.Div([
                html.Div(id=f'map-state{suff}', children="trips" if trips else "stations", style={'display':'none'}),
                        
        
                dbc.Row(children=[
                    dbc.Col([
                        dbc.RadioItems(
                            id=f'stations-radio{suff}',
                            options=[
                                {'label': 'Trip Start', 'value': 'start'},
                                {'label': 'Trip End', 'value': 'stop'},
                                {'label': 'Both', 'value': 'both'}
                            ],
                            value=direction,
                            inline=True
                        ),  
                    ]),
                    dbc.Col(width=4, children=[
                        dbc.Tooltip("Go back to all stations",
                                        target=f'map-return-link{suff}'),
                        dbc.Button(children="All stations", className=return_but_class, id=f'map-return-link{suff}')
                    ]),
                ]),



                dcc.Graph(
                    id=f'map-graph{suff}',
                    figure=make_trips_map(df,direction=direction,suff=suff) if trips else make_station_map(df,direction=direction,suff=suff)

                )
            ])


#######################################################################################
#
#  LAYOUT
#
#######################################################################################

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

                dbc.Card(className="justify-content-center",children=[
                    #dbc.CardHeader(),
                    dbc.CardBody([
                        dcc.Graph(
                            id='timeseries-graph',
                            figure=make_timeseries_fig(thdf),
                            style={'height':'100%','width':'100%'}
                        ),   
                        dbc.Button("Explore Data", id='date-button',size='lg',color="primary", className="mr-1"),
                        dbc.Button("Compare date", id='date-button2',size='lg',color="success", className="mr-1 d-none"),
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











startclass = ''
detail_div = dbc.Row(id='detail-div', className='', children=[
        
        html.Div(id='detail-div-status', className='d-none', children=startclass),
        html.Div(id='detail-div-status2', className='d-none', children=startclass),
        
        dbc.Col(width=12, children=[
            dbc.Row([
                dbc.Col(width=6, id="header-div", className=startclass, children=[

                    dbc.Row([
                        dbc.Col([
                            html.H3("",id="date-header", className=""),
                        ]),
                        dbc.Col(width=2, children=[
                            dbc.Button(id="date-update-btn", color='primary', children=[
                                html.Span(className="fa fa-calendar")
                            ]),
                        ]),

                        dbc.Col(width=12, children=[
                            dbc.Alert(id="filter_output",className="border-rounded",color='primary',children="")
                        ]),
                    ]),
                ]),
                
                dbc.Col(width=6, id="header-div2", className=startclass, children=[

                    dbc.Row([
                        dbc.Col([
                            html.H3("",id="date-header2", className=""),
                        ]),
                        dbc.Col(width=2, children=[
                            dbc.Button(id="date-update-btn2", color='success', children=[
                                html.Span(className="fa fa-calendar")
                            ]),
                        ]),

                        dbc.Col(width=12, children=[
                            dbc.Alert(id="filter_output2",className="border-rounded",color='success',children="")
                        ]),
                    ]),
                ]),
  
            ]),
        ]),
                            
            dbc.Col(width=6, id=f'detail-cards-div', className=startclass, children=make_detail_cards(suff="")),
            dbc.Col(width=6, id=f'detail-cards-div2', className=startclass, children=make_detail_cards(suff="2")),

            dbc.Col(width=6, id='daily-div', className=startclass, children=[
                dcc.Graph(
                    id=f'daily-graph',
                    figure=make_daily_fig(suff="")
                ), 
            ]),
        
            dbc.Col(width=6, id='daily-div2', className=startclass, children=[
                dcc.Graph(
                    id=f'daily-graph2',
                    figure=make_daily_fig(suff="2")
                ), 
            ]),
        
                
            dbc.Col(width=6,id=f'map-div', className=startclass, children=make_map_div(suff="")), #Col
            dbc.Col(width=6,id=f'map-div2',className=startclass,children=make_map_div(suff="2")), #Col

            dbc.Col(width=6, id='memb-div', className=startclass, children=[
                dcc.Graph(
                    id=f'memb-graph',
                    figure=make_memb_fig(suff="")
                )
            ]),
            dbc.Col(width=6, id='memb-div2', className=startclass, children=[
                dcc.Graph(
                    id=f'memb-graph2',
                    figure=make_memb_fig(suff="2")
                )
            ]),
        
            dbc.Col(width=6, id="explore-div", className=startclass, children=[
                dbc.Button("Explore Data", id=f'data-button'),
                html.Div(id="modal-div", children=make_data_modal(suff="")),
            ]),
        
            dbc.Col(width=6, id="explore-div2", className=startclass, children=[
                dbc.Button("Explore Data", id=f'data-button2'),
                html.Div(id="modal-div2", children=make_data_modal(suff="2")),
            ]),
            

        ]) 
    
        







          
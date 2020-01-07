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
from credentials import *


#######################################################################################
#
#  SETUP
#
#######################################################################################

#load data
#df = prep_sys_df('./Mobi_System_Data.csv')
log("==================")
log("Loading data")
df = pd.read_csv(f'{datapath}/Mobi_System_Data_Prepped.csv')


memtypes = set(df['Membership Simple'])
memtypes_member = ['Annual Standard','Annual Plus','Monthly','90 Day']
memtypes_casual = ['Daily','Single Trip']
memtypes_other = [x for x in memtypes if (x not in memtypes_member) and (x not in memtypes_casual)]


df.Departure = pd.to_datetime(df.Departure)
df.Return = pd.to_datetime(df.Return)
  

startdate = df.iloc[0].loc['Departure'] 
enddate = df.iloc[-1].loc['Departure']

startdate_iso = startdate.strftime('%Y-%m-%d')
enddate_iso = enddate.strftime('%Y-%m-%d')

startdate_str = startdate.strftime('%b %-d %Y')
enddate_str = enddate.strftime('%b %-d %Y')

years = set(df.Year)

log("Loading weather")  
wdf = pd.read_csv(f'{datapath}/weather.csv',index_col=0)
wdf.index = pd.to_datetime(wdf.index,utc=True).tz_convert('America/Vancouver').tz_localize(None)
 
filter_data = json.dumps({'date':[startdate_iso,enddate_iso], 'cats':None, 'stations':None, 'direction':'start'})                          
filter_data2 = json.dumps({'date':None,'cats':None,'stations':None,'direction':'start'})



#######################################################################################
#
#  LAYOUT FUNCTIONS
#
#######################################################################################


def make_card(title,content,subcontent=None,color='primary'):
    log("make_card")
    return dbc.Card(style={'border':'none'},className=f"justify-content-center h-100 py-2", children=[
            #dbc.CardHeader(title,style={'color':color}),
            dbc.CardBody([
                
                dbc.Row(title, className=f"text-xs font-weight-bold text-{color} text-uppercase mb-1"),
                dbc.Row(content, className=f"h5 mb-0 font-weight-bold"),
                dbc.Row(subcontent, className=f"h5 mb-0 font-weight-bold text-muted"),
                
            ])

        ])  

    
    
def make_summary_cards(df):

    n_days = (df.iloc[-1].loc['Departure'] - df.iloc[0].loc['Departure']).days
    n_trips = len(df)
    n_trips_per_day = n_trips / n_days
    tot_dist = df['Covered distance (m)'].sum()/1000
    dist_per_trip = tot_dist/n_trips

    tot_time = df['Duration (sec.)'].sum() - df['Stopover duration (sec.)'].sum()

    tot_bikes = len(set(df['Bike'].fillna(0)))
    
    output = [
        
    
    
        dbc.Col(width=12, children=[                
                
            dbc.CardDeck(className="justify-content-center", style={'width':'100%'},children=[
                make_card("Total Trips",f"{n_trips:,}",color='primary'),
                make_card("Total Distance Travelled",f"{int(tot_dist):,} km",color='info'),
                make_card("Unique bikes",f"{tot_bikes:,}",color='success'),
                make_card("Total Trip Time",f"{int(tot_time/(60*60)):,} hours",color='warning')

            ]),
        ]),
    
        dbc.Col(width=12, children=[                
                
            dbc.CardDeck(className="justify-content-center", style={'width':'100%'},children=[
                make_card("Trips/day",f"{int(n_trips/n_days):,}",color='primary'),
                make_card("Avg trip distance",f"{int(tot_dist/n_trips):,} km",color='info'),
                make_card("Avg distance per bike",f"{int(tot_dist/tot_bikes):,} km",color='success'),
                make_card("Avg trip time",f"{int((tot_time/(60))/n_trips):,} minutes",color='warning')

            ]),
        ]),
    
    
        #dbc.Col(html.Em(f"Data available from {startdate_str} to {enddate_str}",className="text-secondary"),width=12),

    ]
    
    return output
    
    
    
def make_detail_cards(df=None,wdf=None,suff=''):
    log("make_detail_cards")
    if df is None:
        return None
    
    if suff == '':
        color = 'primary'
    elif suff == '2':
        color = 'success'
        
    start_date = df['Departure'].iloc[0].strftime('%Y-%m-%d')
    stop_date  = df['Departure'].iloc[-1].strftime('%Y-%m-%d')
    
    
    start_date_str = df['Departure'].iloc[0].strftime('%b %d, %Y')
    stop_date_str = df['Departure'].iloc[-1].strftime('%b %d, %Y')
    
    if wdf is not None:
        wdf = wdf[start_date:stop_date]
    
    n_days = (df['Departure'].iloc[-1] - df['Departure'].iloc[0]).days + 1
    n_days = n_days if (n_days > 1) else 1
    
    
    n_trips = len(df)
    tot_dist = df['Covered distance (m)'].sum()/1000
    avg_dist = tot_dist/n_trips
    avg_trips = n_trips/n_days
    
    tot_time = df['Duration (sec.)'].sum() - df['Stopover duration (sec.)'].sum()
    tot_bikes = len(set(df['Bike'].fillna(0)))
    
    busiest_dep = df.groupby('Departure station').size().sort_values(ascending=False).index[0]
    busiest_dep_n = df.groupby('Departure station').size().sort_values(ascending=False)[0]
    busiest_ret = df.groupby('Return station').size().sort_values(ascending=False).index[0]
    busiest_ret_n = df.groupby('Return station').size().sort_values(ascending=False)[0]
    
    
    
#     avg_daily_high = wdf['Max Temp'].mean()
#     avg_daily_pricip = wdf['Total Precipmm'].mean()
    
#     avg_daily_high = "Data missing" if np.isnan(avg_daily_high) else f"{avg_daily_high:.1f} °C"
#     avg_daily_pricip = "Data missing" if np.isnan(avg_daily_pricip) else f"{avg_daily_pricip:.1f} mm"
    titleclass = f"text-xs font-weight-bold text-{color} text-uppercase mb-1"
    row1 = html.Tr([html.Td("Total trips",className=titleclass), html.Td(f"{n_trips:,}")])
    row2 = html.Tr([html.Td("Average trip distance",className=titleclass), html.Td(f"{int(avg_dist):,} km")])
    row3 = html.Tr([html.Td("Average trip time",className=titleclass), html.Td(f"{int(tot_time/(60*n_trips)):,} minutes")])
    row4 = html.Tr([html.Td("Unique bikes used",className=titleclass), html.Td(f"{int(tot_bikes):,}")])
    table_body = [html.Tbody([row1, row2,row3, row4])]
    table = dbc.Table(table_body,bordered=False)    
   
    output =  dbc.Col(style={'width':'100%'},children=[
           html.H4("Summary"),
           table 

#         dbc.CardColumns([
#             make_card("Total trips", f"{n_trips:,}",color=color),
#             #make_card("Total trip distance",f"{int(tot_dist):,} km",color=color),
#             make_card("Average trip distance",f"{int(avg_dist):,} km",color=color),
#             make_card("Average trip time",f"{int(tot_time/(60*n_trips)):,} minutes",color=color),
#             make_card("Unique bikes used", f"{int(tot_bikes):,}", color=color),
            
            
# #             make_card("Daily high temp",avg_daily_high,color=color),
# #             make_card("Daily precipitation",avg_daily_pricip,color=color),
            
            
#             make_card("Busiest departure station",f"{busiest_dep}",color=color),
#             make_card("Busiest return station",f"{busiest_ret}",color=color)

#         ])
    ])
    log("make_detail_cards finished")
    return output


def make_data_modal(df=None, suff=""):
    log("Make_data_modal")
    max_records = 100000 # Only allow downloads up to limit
    max_rows    = 10000   # Only show first N rows in data_table
    
    if df is None:
        df = pd.DataFrame()
        outfields = []
    else:
        outfields = ['Departure','Return','Departure station','Return station','Membership Type','Covered distance (m)','Duration (sec.)']
    
    if len(df) > max_records:
        tooltip = dbc.Tooltip("Your selection is too large to download. Try a smaller date range.",
                                        target=f"download-data-button{suff}")
        
    else:
        tooltip = dbc.Tooltip("Download the records for the selected trips",
                                        target=f"download-data-button{suff}")
    
    
    if len(df) > max_rows:
        warning_txt = "Your selection produced too many results and may be truncated"
    else:
        warning_txt = ""
    
    
    
    button =  html.A(id=f"download-data-button{suff}", className="btn btn-primary", href="#", children=[
                        html.Span(className="fa fa-download"),
                        " Download CSV",
                    ])
    
    
    modal = dbc.Modal([
                dbc.ModalHeader("Raw Data"),
                dbc.ModalBody(children=[
                    html.Span(warning_txt),
                    dash_table.DataTable(
                        id=f'data-table{suff}',
                        columns=[{"name": i, "id": i} for i in outfields],
                        data=df.head(max_rows)[outfields].to_dict('records'),
                        style_table={'overflowX': 'scroll',
                                     'maxHeight': '300px'
                                    },
                    )    
                    
                ]),
                tooltip,
                dbc.ModalFooter(button),
            ],
            id=f"data-modal{suff}",
            size="xl",
            )
    log("make_data_modal finished")
    return modal



def make_map_div(df=None,trips=False,direction='start',suff=""):
    log("make_map_div")
        
    output = html.Div([
                html.Div(id=f'map-state{suff}', children="trips" if trips else "stations", style={'display':'none'}),

                dcc.Graph(
                    id=f'map-graph{suff}',
                    figure=make_trips_map(df,direction=direction,suff=suff) if trips else make_station_map(df,direction=direction,suff=suff)

                )
            ])
    log("make_map_div finished")
    return output


def make_detail_header(filter_data, suff=""):
    log("make_detail_header")
    if suff == "":
        color='primary'
    elif suff == "2":
        color='success'
    
    direction = filter_data['direction']
    stations = "All" if filter_data['stations'] is None else ", ".join(filter_data['stations'])
    
    if (filter_data['cats'] is None) or (set(filter_data['cats']) == set(memtypes)): 
        cats = "All"
    else: cats = ", ".join(filter_data['cats'])
        
        
    date = ' ' if filter_data['date'] is None else filter_data['date']

        
    date_button = dbc.Button(id=f"date-update-btn{suff}", color=color, children=[
       html.Span(className="fa fa-calendar")
        ])
    date_button_tt = dbc.Tooltip(target=f"date-update-btn{suff}",children="Change the current date range")
   
    
    close_button = dbc.Button(id=f"close-btn{suff}", color=color, children=[
        html.Span(className="fa fa-times-circle")
        ])
    close_button_tt = dbc.Tooltip(target=f"close-btn{suff}", children="Close")

    if suff == "":
        date_button2 = dbc.Button(id='date-button2', color=color,children=[
            html.Span(className="fa fa-plus" )
            ])
        date_button2_tt = dbc.Tooltip(target='date-button2',children="Compare a second date range")
        close_button = dbc.Button(id=f"close-btn{suff}", className='d-none',color=color, children=[
            html.Span(className="fa fa-times-circle")
            ])
    else:
        date_button2 = ""
        date_button2_tt = ""
        
    data_button = dbc.Button(id=f'data-button{suff}', color=color, children=[
        html.Span(className="fa fa-table" )
    ])               
    data_button_tt = dbc.Tooltip(target=f'data-button{suff}', children="View raw data")
        
    button_col = dbc.Col(className="d-flex justify-content-end",children=[date_button,date_button_tt,
                                            data_button,data_button_tt,
                                            date_button2,date_button2_tt,
                                            close_button,close_button_tt])
        
        
    if len(date) == 2:
        try:
            d1 = datetime.strptime(date[0],'%Y-%m-%d').strftime('%A, %B %-d %Y')
            d2 = datetime.strptime(date[1],'%Y-%m-%d').strftime('%A, %B %-d %Y')
        except:
            d1 = " "
            d2 = " "
        header_txt = dbc.Col([d1," ",html.Span(className="fa fa-arrow-right")," ", d2])
    else:
        try:
            d1 = datetime.strptime(date,'%Y-%m-%d').strftime('%A, %B %-d %Y')
        except:
            d1 = " "
        header_txt = dbc.Col(children=[d1])
        
    header = dbc.Row(className='d-flex',children=[header_txt,button_col])
                

    radio = dbc.RadioItems(
                id=f'stations-radio{suff}',
                options=[
                    {'label': 'Trip Start', 'value': 'start'},
                    {'label': 'Trip End', 'value': 'stop'},
                    {'label': 'Both', 'value': 'both'}
                ],
                value=direction,
                inline=True
            )

       
    return_btn_class = 'd-none' if stations=='All' else ''
    return_btn_tt = dbc.Tooltip("Go back to all stations", target=f'map-return-btn{suff}')
    return_btn    = dbc.Button(size="sm", className=return_btn_class,id=f'map-return-btn{suff}',color='white', children=[
                        html.Span(className=f"fa fa-times-circle text-{color}")
                    ])    
        
    row2 = html.Tr([html.Td("Direction"), html.Td(radio)])
    row3 = html.Tr([html.Td("Stations"), html.Td(html.Em(stations)),return_btn_tt,return_btn])
    row4 = html.Tr([html.Td("Membership Types"), html.Td(html.Em(cats))])
    table_body = [html.Tbody([row3,row2, row4])]
    table = dbc.Table(table_body, size='sm',bordered=False)

    card = dbc.Card(className='mb-3',children=[
            dbc.CardHeader(className=f"text-strong text-white bg-{color}",children=header),
            table,
        ])
    log("make_detail_header finished")
    return card
 


def make_date_modal(suff=""):
    output = dbc.Modal(size='md', id=f'date-modal{suff}', children=[
            #dbc.ModalHeader("Explore trip data"),
            dbc.ModalBody([
                html.Div(id=f"filter-meta-div{suff}", children=filter_data, className='d-none'),
                    dbc.Row(className='pb-2', children=[
                        dbc.Col(width=12, className='m-2 px-2 pt-2', children=html.H3("Select a date range")),
                        dbc.Col(width=12, className='m-2 p-2', children=[
   
                            dcc.DatePickerRange(
                                id=f'datepicker{suff}',
                                min_date_allowed=startdate,
                                max_date_allowed=enddate,
                                #initial_visible_month = '2018-01-01',
                                display_format='YYYY-MM-DD',
                                start_date=startdate_iso,
                                end_date=enddate_iso,
                                #end_date_placeholder_text="(Optional)",
                                minimum_nights = 0,
                                clearable = True,
                            ),
 
                        ]),

                        dbc.Col(width=10, className='m-2 px-2 pt-2 border-top', children=html.H3("Filter by membership type")),
                        dbc.Col(width=4, children=[
                            dbc.Checklist(id=f'checklist-member-header{suff}', 
                                options=[{'label':'Regular','value':'Member'}],
                                value=['Member']
                            ),
                                          
                            dbc.Checklist(id=f'checklist-member{suff}',className="checklist-faded-custom",
                                options=[{'label':memtype,'value':memtype} for memtype in memtypes_member],
                                value=memtypes_member,
                                labelStyle={'color':c_gray_600},
                            ),
                        ]),
                        dbc.Col(width=4, className='border-left border-right', children=[
                            dbc.Checklist(id=f'checklist-casual-header{suff}',
                                options=[{'label':'Casual','value':'Casual'}],
                                value=['Casual']
                            ),
                            dbc.Checklist(id=f'checklist-casual{suff}', className="checklist-faded-custom",
                                options=[{'label':memtype,'value':memtype} for memtype in memtypes_casual],
                                value=memtypes_casual,
                                labelStyle={'color':c_gray_600}, 
                            ),
                        ]),
                        
                        dbc.Col(width=4, children=[
                            dbc.Checklist(id=f'checklist-other-header{suff}',
                                options=[{'label':'Other','value':'Other'}],
                                value=['Other']
                            ),
                            dbc.Checklist(id=f'checklist-other{suff}', className="checklist-faded-custom",
                                options=[{'label':memtype,'value':memtype} for memtype in memtypes_other],
                                value=memtypes_other,
                                labelStyle={'color':c_gray_600},
                            ),
                        ]),
                        
                        
                    ]),
                dbc.Tooltip("Pick a date or select a range of days to see details.",
                                        target=f"go-button{suff}"),
                dbc.Button("Go    ", id=f'go-button{suff}', color="primary", disabled=True, outline=False, block=True),
            ])
        ])
    return output

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
    brand="BikeDataBC",
    brand_href="#",
#     sticky="top",
    color='#1e5359',
    dark=True
    )

footer = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Link", href="#")),
        
    ],
    brand="BikeDataBC",
    brand_href="#",
    sticky="bottom",
    color='#1e5359',
    dark=True
    )


summary_jumbo = dbc.Jumbotron(className="bg-white", children=[
        html.H1("BikeData BC", className="display-3"),

        html.P(
            "Explore trip data from Mobi, Vancouver's bike share company",
            className="lead",
        ),
        html.Hr(className="my-2"),
    
        dbc.Row([
            dbc.Col(width=4, children=[
                dbc.Select(
                    id="summary-year-select",
                    options=[{'label': f"{min(years)} - {max(years)}", 'value':'All' }] + 
                       [ {'label': f'{x}', 'value':f'{x}' } 
                       for x in set(years) ],
                    value='All'
                ),
            ]),
        ]),
        dbc.Row(id="summary-card-row", className='p-3 justify-content-center', children=make_summary_cards(df))
            
    ]
)




main_div = dbc.Row(className="pb-2",children=[
    dbc.Col(width=12, className='d-none',children=[
        dbc.Row(justify='center', children=[
            dbc.Button("Explore Data", size='lg', id='date-button',color="primary") 
        ]),
    ]),
    
    dbc.Col(width=12, children=[
        dbc.Card(style={'border':'none'}, children=[
            
            dcc.Graph(
                id='timeseries-graph',
                figure=make_timeseries_fig([startdate_iso,enddate_iso],None),
                style={'height':'200px','width':'100%'}
            ),   

            
        ]),
        

        

        

        make_date_modal(suff=""),
        
        make_date_modal(suff="2")
    ])
])










startclass = ''
detail_div = dbc.Row(id='detail-div', className='', children=[
        
        html.Div(id='detail-div-status', className='d-none', children=startclass),
        html.Div(id='detail-div-status2', className='d-none', children=startclass),
        
        dbc.Col(className='sticky-top', width=12, children=[
            dbc.Row(children=[
                dbc.Col(width=True, id="header-div", className=startclass, children=[

                    dbc.Row([
                        dbc.Col(id="date-header", children=make_detail_header(json.loads(filter_data), suff="")),
                    ]),
                ]),
                
                dbc.Col(width=6, id="header-div2", className=startclass, children=[

                    dbc.Row([
                        dbc.Col(id="date-header2", children=make_detail_header(json.loads(filter_data), suff="2")),
                    ]),
                ]),
  
            ]),
        ]),
                            
            dbc.Col(width=6, id=f'detail-cards-div', className=startclass, children=make_detail_cards(df,suff="")),
            dbc.Col(width=6, id=f'detail-cards-div2', className=startclass, children=make_detail_cards(suff="2")),

            dbc.Col(width=6, id='daily-div', className=startclass, children=[
                dcc.Graph(
                    id=f'daily-graph',
                    figure=make_daily_fig(df,wdf,suff="")
                ), 
            ]),
        
            dbc.Col(width=6, id='daily-div2', className=startclass, children=[
                dcc.Graph(
                    id=f'daily-graph2',
                    figure=make_daily_fig(suff="2")
                ), 
            ]),
        
                
            dbc.Col(width=6,id=f'map-div', className=startclass, children=make_map_div(df,suff="")), #Col
            dbc.Col(width=6,id=f'map-div2',className=startclass,children=make_map_div(suff="2")), #Col

            dbc.Col(width=6, id='memb-div', className=startclass, children=[
                dcc.Graph(
                    id=f'memb-graph',
                    figure=make_memb_fig(df,suff="")
                )
            ]),
            dbc.Col(width=6, id='memb-div2', className=startclass, children=[
                dcc.Graph(
                    id=f'memb-graph2',
                    figure=make_memb_fig(df,suff="2")
                )
            ]),
        
            dbc.Col(width=6, id="explore-div", className=startclass, children=[
                html.Div(id="modal-div", children=make_data_modal(df,suff="")),
            ]),
        
            dbc.Col(width=6, id="explore-div2", className=startclass, children=[
                html.Div(id="modal-div2", children=make_data_modal(suff="2")),
            ]),
            

        ]) 
    
        







          
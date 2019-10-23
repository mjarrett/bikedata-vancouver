import mobisys as mobi
import numpy as np
import pandas as pd
import geopandas

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

from plots import *

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



def make_detail_div():
    log(f"make_detail_div")
    startclass = ''
   
    output =  [
        
        html.Div(id='detail-div-status', className='d-none', children=startclass),
        html.Div(id='detail-div-status2', className='d-none', children=startclass),
        
        dbc.Col(width=12, children=[
            dbc.Row([
                dbc.Col(width=6, id="header-div", className=startclass, children=[

                        html.H3("",id="date-header", className=""),
                        dbc.Tooltip("Pick a date or select a range of days to see comparison.",
                                                target="date-button2"),
                        dbc.Button("Compare", id=f'date-button2', color="success"),
                ]),

                dbc.Col(width=6, id="header-div2", className=startclass, children=[

                        html.H3("",id="date-header2", className=""),
                        #dbc.Tooltip("Pick a date or select a range of days to see comparison.",
                        #                        target="compare-button"),
                        #dbc.Button("Compare", id=f'compare-button2', color="success"),
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
                make_data_modal(suff=""),
            ]),
        
            dbc.Col(width=6, id="explore-div2", className=startclass, children=[
                dbc.Button("Explore Data", id=f'data-button2'),
                make_data_modal(suff="2"),
            ]),
            

        ] # Col
    
    #print(output)
    return output
    
# def make_detail_div(df, wdf, df2=None,trips=False, trips2=False,direction='start',direction2='start'):
#     if df2 is None:
#         return make_detail_col(df,wdf,trips,direction)
#     if df2 is not None:
#         return make_detail_cols(df,df2,wdf,trips,trips2,direction,direction2)
        
def make_map_div(df=None,trips=False,direction='start',suff=""):
    
    return html.Div([
                html.Div(id=f'map-state{suff}', children="trips" if trips else "stations", style={'display':'none'}),
                        
        
                html.Div(children=[
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
                html.Div(id=f'map-meta-div{suff}',style={'display':'none'}, children=[
                    html.A(children="<", id=f'map-return-link{suff}', title="Return to station map") 
                ]),


                dcc.Graph(
                    id=f'map-graph{suff}',
                    figure=make_trips_map(df,direction=direction) if trips else make_station_map(df,direction=direction,suff=suff)

                )
            ])

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
                    html.A(id=f"download-data-button{suff}", className="btn btn-primary", href="#", children="Download CSV")
                ),
            ],
            id=f"data-modal{suff}",
            size="xl",
            )
    return modal




          
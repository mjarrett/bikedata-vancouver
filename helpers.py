import mobisys as mobi
import numpy as np
import pandas as pd
import geopandas

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

from plots import *


    
def filter_ddf(df, date=None, cats=None, stations=None, direction='both'):

    if (date is None) and (cats is None) and (stations is None):
        return df
    
    if stations is not None:
        if direction == 'both':
            df = df.loc[df['Departure station'].isin(stations) | df['Return station'].isin(stations),:]
        elif direction == 'start':
            df = df.loc[df['Departure station'].isin(stations),:]
        elif direction == 'stop':
            df = df.loc[df['Return station'].isin(stations),:]
            
    
    if date is not None:
        if len(date) == 2:
            df = df.set_index('Departure')[date[0]:date[1]].reset_index()
        else:
            df = df.set_index('Departure')[date].reset_index()
   
            
    if cats is not None:
      
        if 'all' in cats:
            pass
        
        else:
            idx = np.array([False for x in range(len(df))])
            
            if '24h' in cats:
                idx24 = np.array((df['Membership Type']=='24 Hour'))
                idx = idx | idx24
            if '365S' in cats:
                idx365s = np.array(df['Membership Type'].str.contains('365.+Standard'))
                idx = idx | idx365s
            if '365P' in cats:
                idx365p = np.array(df['Membership Type'].str.contains('365.+Plus'))
                idx = idx | idx365p                
            if '90d' in cats:
                idx90 = np.array(df['Membership Type'].str.contains('90')) 
                idx = idx | idx90
                
            df = df.iloc[idx]
    sdf = geopandas.read_file(f'./data/stations_df.geojson')
    df = mobi.add_station_coords(df,sdf)
    df = df.sort_values('Departure')
    return df

def make_card(title,content):
    return dbc.Card(className="justify-content-center", children=[
            dbc.CardBody(
                    [
                    html.P(
                        title,
                        className="card-text"),
                    html.H2(content, className="card-title"),

                ]) # Card body

            ])  # Card

def make_detail_cards(df,wdf):
    if df is None:
        return None
    
    
    start_date = df['Departure'].iloc[0].strftime('%Y-%m-%d')
    stop_date  = df['Departure'].iloc[-1].strftime('%Y-%m-%d')
    
    print(start_date,stop_date)
    
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
    

    if start_date != stop_date:
        output =  dbc.Col(style={'width':'100%'},children=[
                html.H2(f"{start_date_str} to {stop_date_str}"),
                dbc.CardColumns([

                    make_card("Total trips", f"{n_trips:,}"),
                    make_card("Average trip distance",f"{int(avg_dist):,} km"),
                    make_card("Average trips per day",f"{int(avg_trips):,}"),
                    make_card("Daily high temp",f"{avg_daily_high:.1f} °C"),
                    make_card("Daily precipitation",f"{avg_daily_pricip:.1f} mm"),


                ]),

                dbc.CardColumns([
                    make_card("Busiest departure station",f"{busiest_dep}"),
                    make_card("Busiest return station",f"{busiest_ret}")

                ])
            ])
    else:
        output =  dbc.Col(style={'width':'100%'},children=[
            html.H2(f"{start_date_str}"),
            dbc.CardColumns([
                make_card("Total trips", f"{n_trips:,}"),
                make_card("Average trip distance",f"{int(avg_dist):,} km"),
                make_card("Daily high temp",f"{avg_daily_high:.1f} °C"),
                make_card("Daily precipitation",f"{avg_daily_pricip:.1f} mm"),


            ]),

            dbc.CardColumns([
                make_card("Busiest departure station",f"{busiest_dep}"),
                make_card("Busiest return station",f"{busiest_ret}")

            ])
        ])
    
    return output

def make_detail_cols(df,df2,wdf):
    
    res_row = dbc.Row([
                    dbc.Col(width=6,children=[
                        make_detail_cards(df,wdf)
                    ]),
                    dbc.Col(width=6,children=[
                        make_detail_cards(df2,wdf)
                    ])
                ])
        
    daily_row = dbc.Row([
                    dbc.Col(width=6,children=[
                        dcc.Graph(
                            id=f'daily-graph',
                            figure=make_daily_fig(df)
                            )
                    ]),
                    dbc.Col(width=6,children=[
                       dcc.Graph(
                            id=f'daily-graph2',
                            figure=make_daily_fig(df2)
                           )
                    ])
                ])
    map_row = dbc.Row([
                dbc.Col([make_map_div(df)]), 
                dbc.Col([make_map_div(df2,suff='2')])
              ])
    
    memb_row = dbc.Row([
                  dbc.Col(children=[
                    dcc.Graph(
                        id=f'memb-graph',
                        figure=make_memb_fig(df)
                    )
                  ]),
                  dbc.Col(children=[
                    dcc.Graph(
                        id=f'memb-graph2',
                        figure=make_memb_fig(df2)
                    )
                  ])
                ])
    
    button_row = dbc.Row(children=[
                    dbc.Col(width=6, children=[
                        dbc.Button("Raw Data", id='data-button'),
                        make_data_modal(df)
                    ]),
                    dbc.Col(width=6, children=[
                        dbc.Button("Raw Data", id='data-button2'),
                        make_data_modal(df,suff='2')
                    ])
            ])
    
    return dbc.Col([res_row, daily_row, map_row, memb_row, button_row])

def make_detail_col(df,wdf):
        
    return dbc.Col(children=[
            
            dbc.Row(id=f'detail-cards',children=make_detail_cards(df,wdf)),
            
            dbc.Row([

                dcc.Graph(
                    id=f'daily-graph',
                    figure=make_daily_fig(df)
                ), 
            ]), #Row
        
            dbc.Row(children=[
                
                dbc.Col(id=f'map_container', children=make_map_div(df)), #Col
                
                dbc.Col(children=[
                    dcc.Graph(
                        id=f'memb-graph',
                        figure=make_memb_fig(df)
                    )
                ]),
            ]),
        
            dbc.Row(children=[
                dbc.Button("Explore Data", id='data-button'),
                make_data_modal(df),
            ])
            

        ]) # Col

def make_detail_div(df, wdf, df2=None):
    if df2 is None:
        return make_detail_col(df,wdf)
    if df2 is not None:
        return make_detail_cols(df,df2,wdf)
        
def make_map_div(df,suff=""):
    
    return html.Div([
                html.Div(id=f'map-state{suff}', children="stations", style={'display':'none'}),
                
                html.Div(children=[
                    dbc.RadioItems(
                        id=f'stations-radio{suff}',
                        options=[
                            {'label': 'Trip Start', 'value': 'start'},
                            {'label': 'Trip End', 'value': 'stop'},
                            {'label': 'Both', 'value': 'both'}
                        ],
                        value='start',
                        inline=True
                    ),  
                ]),
                html.Div(id=f'map-meta-div{suff}',style={'display':'none'}, children=[
                    html.A(children="<", id=f'map-return-link{suff}', title="Return to station map") 
                ]),

                dcc.Graph(
                    id=f'map-graph{suff}',
                    figure=make_station_map(df)

                )
            ])

def make_data_modal(df, suff=""):
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




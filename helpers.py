import mobisys as mobi
import numpy as np
import pandas as pd
import geopandas

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from plots import *

def get_prepped_data():
    df = pd.read_csv('./data/Mobi_System_Data_Prepped.csv')
    df['Departure'] = pd.to_datetime(df['Departure'])
    df['Return'] = pd.to_datetime(df['Return'])

    return df
    
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
    
    start_date = df['Departure'].iloc[0].strftime('%Y-%m-%d')
    stop_date  = df['Departure'].iloc[-1].strftime('%Y-%m-%d')
    
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
    
    return dbc.Col([res_row, daily_row, map_row])

def make_detail_col(df,wdf):
        
    return dbc.Col(children=[
            
            dbc.Row(id=f'detail-cards',children=make_detail_cards(df,wdf)),
            
            dbc.Row([
                dbc.Col([

                    dbc.Row([
                        dcc.Graph(
                            id=f'daily-graph',
                            figure=make_daily_fig()
                        )
                    ]),
                ]),
        
        
        
        
                dbc.Col(id=f'map_container', children=make_map_div(df)), #Col
            ]), #Row

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
                    figure=make_station_map()

                )
            ])
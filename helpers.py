import mobisys as mobi
import numpy as np
import pandas as pd
import geopandas

import dash_core_components as dcc
import dash_html_components as html

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



def get_stats(df,wdf):
    
    start_date = df['Departure'].iloc[0].strftime('%Y-%m-%d')
    stop_date  = df['Departure'].iloc[-1].strftime('%Y-%m-%d')
    
    n_trips = len(df)
    busiest_dep = df.groupby('Departure station').size().sort_values(ascending=False).index[0]
    busiest_dep_n = df.groupby('Departure station').size().sort_values(ascending=False)[0]
    busiest_ret = df.groupby('Return station').size().sort_values(ascending=False).index[0]
    busiest_ret_n = df.groupby('Return station').size().sort_values(ascending=False)[0]
    
    avg_daily_high = wdf['Max Temp'].mean()
    avg_daily_pricip = wdf['Total Precipmm'].mean()
    
    outstr = f"""{start_date}-{stop_date}<br>
    {n_trips} trips
    Busiest starting station: {busiest_dep}
    Busiest return station: {busiest_ret}
    Average daily high: {avg_daily_high}
    Average daily precipitation: {avg_daily_pricip}"""
    
    
    output = [html.Ul(children=[
                html.Li(f"{start_date} to {stop_date}"),
                html.Li(f"{n_trips:,} trips"),
                html.Li(f"Busiest starting station: {busiest_dep}"),
                html.Li(f"Busiest return station: {busiest_ret}"),
                html.Li(f"Average daily high: {avg_daily_high:.1f}°"),
                html.Li(f"Average daily precipitation: {avg_daily_pricip:.1f} mm")
                ]
             )]
                      
             
    
    return output
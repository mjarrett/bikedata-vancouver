import numpy as np
import pandas as pd
import geopandas
from datetime import datetime
import sys

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash

from credentials import loglevel, datapath

def log(*args,file=None,cb=False):
    """
    Level is none, log, verbose
    """
    if loglevel == 'none':
        return None
    
    if loglevel == 'verbose':
        args = [datetime.now()] + list(args)
    elif loglevel == 'log':
        pass
    
    
    if cb:
        try:
            trig = dash.callback_context.triggered[0]['prop_id']
        except:
            trig = "No trigger"
        args = list(args) + ["* ", trig ]
    
    
    if file == None:
        print(*args,file=sys.stdout,flush=True)
    else:
        if type(file) != str:
            raise TypeError("'file' argument must be a string")
        with open(file,'a') as f:
            print(*args,file=f,flush=True)

    
def filter_ddf(df, filter_data=None, date=None, cats=None, stations=None, direction='both'):
    
    if filter_data is not None:
        date = filter_data['date']
        cats = filter_data['cats']
        stations = filter_data['stations']
        direction = filter_data['direction']
        
    log(f"Filter {date} {cats} {stations} {direction}")
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
        df = df[df['Membership Simple'].isin(cats)]
                

    df = df.sort_values('Departure')
    
    log(f"Filter finished: {len(df)} records")
                                           
    return df

def convert_dates(start_date,end_date):
    log("convert_dates")
        
    if start_date is None:
        date = None
    elif (end_date is None) or  (start_date == end_date):
        date = start_date[:10]
    else:
        date = (start_date[:10], end_date[:10])
    return date

def date_2_str(date):
    log("date_2_str")
    if date == None:
        return None
    
    if len(date) == 2:
        d1 = datetime.strptime(date[0],'%Y-%m-%d').strftime('%A, %B %-d %Y')
        d2 = datetime.strptime(date[1],'%Y-%m-%d').strftime('%A, %B %-d %Y')
        return f"{d1} to  {d2}"
    else:
        d1 = datetime.strptime(date,'%Y-%m-%d').strftime('%A, %B %-d %Y')
        return f"{d1}"
    
def date_2_div(date):
    log("date_2_div")
    if date == None:
        return None
    
    if len(date) == 2:
        d1 = datetime.strptime(date[0],'%Y-%m-%d').strftime('%A, %B %-d %Y')
        d2 = datetime.strptime(date[1],'%Y-%m-%d').strftime('%A, %B %-d %Y')
        return [dbc.Col(html.H3(d1),width=8), 
              dbc.Col(html.Span(className="fa fa-arrow-right"),width=3),
              dbc.Col(html.H3(d2),width=8)
             ]
    else:
        d1 = datetime.strptime(date,'%Y-%m-%d').strftime('%A, %B %-d %Y')

        return dbc.Col(html.H3(d1),width=8), 
              

def get_hourly_max():
    thdf = pd.read_csv(f'{datapath}/data/Mobi_System_Data_taken_hourly.csv',index_col=0)
    return thdf.sum(1).max()

def get_daily_max():
    thdf = pd.read_csv(f'{datapath}/data/Mobi_System_Data_taken_hourly.csv',index_col=0, parse_dates=True)
    tddf = thdf.groupby(pd.Grouper(freq='d')).sum()
    return tddf.sum(1).max()


def make_thdf(df):

    
    thdf = df.pivot_table(index='Departure', 
                     columns='Departure station', 
                     values='Bike',
                     fill_value=0, 
                     aggfunc='count')
    
    thdf = thdf.groupby(pd.Grouper(freq='H')).sum() # Need this in case times aren't already rounded to hour
    
    indx = pd.date_range(thdf.index[0],thdf.index[-1], freq='H')
    thdf = thdf.reindex(indx).fillna(0)
    thdf = thdf.astype(int)
    
    return thdf

def make_rhdf(df):
    
    rhdf = df.pivot_table(index='Return', 
                     columns='Return station', 
                     values='Bike',
                     fill_value=0, 
                     aggfunc='count')
    
    rhdf = rhdf.groupby(pd.Grouper(freq='H')).sum()
    
    indx = pd.date_range(rhdf.index[0],rhdf.index[-1], freq='H')
    rhdf = rhdf.reindex(indx).fillna(0)
    rhdf = rhdf.astype(int)
    
    return rhdf



def make_ahdf(df):

        
    ahdf =  make_thdf(df).add(make_rhdf(df),fill_value=0)
    
    ahdf = ahdf.groupby(pd.Grouper(freq='H')).sum()
    
    indx = pd.date_range(ahdf.index[0],ahdf.index[-1], freq='H')
    ahdf = ahdf.reindex(indx).fillna(0)
    ahdf = ahdf.astype(int)
    return ahdf


def make_con_df(df):
    
    
    condf = df.groupby(['Departure station','Return station','Departure lat','Return lat','Departure long','Return long']).size()
    condf = condf.reset_index()
    condf.columns = ['Departure station','Return station','Departure lat','Return lat','Departure long','Return long','trips']
    
    return condf

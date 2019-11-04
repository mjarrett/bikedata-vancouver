import mobisys as mobi
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

from credentials import loglevel

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
        args = list(args) + ["* ", dash.callback_context.triggered[0]['prop_id'] ]
    
    
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
              
    

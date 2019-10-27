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


def log(*args,file=None):
    args = [datetime.now()] + list(args)
    if file == None:
        print(*args,file=sys.stdout,flush=True)
    else:
        if type(file) != str:
            raise TypeError("'file' argument must be a string")
        with open(file,'a') as f:
            print(*args,file=f,flush=True)

    
def filter_ddf(df, date=None, cats=None, stations=None, direction='both'):
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
    
    log("Filter finished")
                                           
    return df

def convert_dates(start_date,end_date):
#     if start_date2 is not None:
#         if end_date2 is not None and (start_date2 != end_date2):
#             date2 = (start_date2[:10], end_date2[:10])
#         else:
#             date2 = start_date2[:10] 
#     else:
#         date2 = None
    
#     if start_date2 is None:
#         date2 = None
#     elif (end_date2 is None) or  (start_date2 == end_date2):
#         date2 = start_date2[:10]
#     else:
#         date2 = (start_date2[:10], end_date2[:10])
        
    if start_date is None:
        date = None
    elif (end_date is None) or  (start_date == end_date):
        date = start_date[:10]
    else:
        date = (start_date[:10], end_date[:10])
    return date

def date_2_str(date):
    
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
              
    
def make_filter_table(filter_data):
    
    stations = "All" if filter_data['stations'] == None else ", ".join(filter_data['stations'])
    cats = "All" if filter_data['cats'] == None else ", ".join(filter_data['cats'])
    date = filter_data['date']
    if len(date) == 2:
        d1 = datetime.strptime(date[0],'%Y-%m-%d').strftime('%A, %B %-d %Y')
        d2 = datetime.strptime(date[1],'%Y-%m-%d').strftime('%A, %B %-d %Y')
    else:
        d1 = datetime.strptime(date,'%Y-%m-%d').strftime('%A, %B %-d %Y')
        d2 = ""
    
    
    row1 = html.Tr([html.Td(html.Strong("")), html.Td(html.Strong(d1))])
    row2 = html.Tr([html.Td(html.Strong("")), html.Td(html.Strong(d2))])
    row3 = html.Tr([html.Td(html.Strong("Stations")), html.Td(html.Em(stations))])
    row4 = html.Tr([html.Td(html.Strong("Membership Types")), html.Td(html.Em(cats))])


    table_body = [html.Tbody([row1, row2, row3, row4])]

    table = dbc.Table(table_body, bordered=False)
    
    return table

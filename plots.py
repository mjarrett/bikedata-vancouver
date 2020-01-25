import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd
import datetime as dt
import geopandas
import mobisys as mobi

from credentials import *
from helpers import *

margin=go.layout.Margin(
    l=5,
    r=5,
    b=5,
    t=5,
    pad=0)

maplayout = go.Layout(mapbox_style="light",
                          mapbox=go.layout.Mapbox(
                            accesstoken=MAPBOX_TOKEN,
                            bearing=0,
                            center=go.layout.mapbox.Center(
                            lat=49.28, 
                            lon=-123.11
                            ),
                            zoom=11.5
                            ),
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          margin=margin,
                          showlegend = False,
                         )

          
c_blue =     '#3286AD' #// primary
c_light_blue='#50AAD3'
c_purple =   '#8357B2' #// info
c_red =      '#FF5B71' # // danger
c_yellow =   '#E5DE50' #// warning
c_green =    '#5FCEC1' #// success


c_white =   '#fff' #!default;
c_gray_100= '#f8f9fa' #!default; // light
c_gray_200= '#e9ecef' #!default;
c_gray_300= '#dee2e6' #!default;
c_gray_400= '#ced4da' #!default;
c_gray_500= '#adb5bd' #!default;
c_gray_600= '#868e96' #!default; // secondary
c_gray_700= '#495057' #!default;
c_gray_800= '#343a40' #!default; // dark
c_gray_900= '#212529' #!default;
c_black=    '#000' #!default;





def make_timeseries_fig(date=None, date2=None):
    log("make_timeseries_fig")
    thdf = pd.read_csv(f'{datapath}/data/Mobi_System_Data_taken_hourly.csv',index_col=0)
    thdf.index = pd.to_datetime(thdf.index)
    
    
    trips_hdf = thdf.sum(1).reset_index()
    trips_hdf.columns = ['Hour','Trips']

    tddf = thdf.groupby(pd.Grouper(freq='d')).sum()
    trips_ddf = tddf.sum(1)
    trips_ddf = trips_ddf.reset_index()
    trips_ddf.columns = ['Date','Trips']
    trips_rdf = trips_ddf.set_index('Date')['Trips'].rolling(30,min_periods=1, center=True).mean().reset_index()

    
    trips_ddf['Color'] = c_blue 
    
    if (date is not None) or (date2 is not None):
        color = c_gray_200
        opacity = 0.7
    else:
        color = c_dark_teal
        opacity = 1


    data = [go.Scatter(
            x=trips_ddf['Date'],
            y=trips_ddf['Trips'],
            marker_color = color,
            opacity = opacity,
            name="Daily trips",
            fill='tozeroy',
                )
           ]
    
    layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       yaxis = {
                         'fixedrange': True,
                               },
                       margin=margin,
                       dragmode='zoom', 
                      showlegend=False
                  )

   


    if date is not None:
        if len(date) == 2:
            d1 = dt.datetime.strptime(date[0],'%Y-%m-%d') - dt.timedelta(0.5)
            d2 = dt.datetime.strptime(date[1],'%Y-%m-%d') + dt.timedelta(0.5)
        else:
            d1 = dt.datetime.strptime(date,'%Y-%m-%d') - dt.timedelta(0.5)
            d2 = d1 + dt.timedelta(1)
            
        data = data + [go.Scatter(
                        x=trips_ddf.set_index('Date').loc[d1:d2].index,
                        y=trips_ddf.set_index('Date').loc[d1:d2,'Trips'],
                        marker_color = c_blue,
                        fill='tozeroy',
                        name='Selection 1'
                            )
                       ]
    if date2 is not None:
        if len(date2) == 2:
            d1 = dt.datetime.strptime(date2[0],'%Y-%m-%d') - dt.timedelta(0.5)
            d2 = dt.datetime.strptime(date2[1],'%Y-%m-%d') + dt.timedelta(0.5)
        else:
            d1 = dt.datetime.strptime(date2,'%Y-%m-%d') - dt.timedelta(0.5)
            d2 = d1 + dt.timedelta(1)
            
        data = data + [go.Scatter(
                        x=trips_ddf.set_index('Date').loc[d1:d2].index,
                        y=trips_ddf.set_index('Date').loc[d1:d2,'Trips'],
                        marker_color = c_green,
                        fill='tozeroy',
                        name='Selection 2'
                            )
                       ]

    fig = go.Figure(data=data,layout=layout)

    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=c_gray_400)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=c_gray_400,title_text='Daily Trips')
    


    
    log("make_timeseries_fig finished")
    return fig


def make_station_map(df=None, direction='start', suff=""):
    log("make_station_map")  
    if suff == "":
        color = c_blue
    elif suff == "2":
        color = c_green
    
    # https://plot.ly/python/mapbox-layers/
    log("prepping sdf")
    sdf = geopandas.read_file(f'{datapath}/data/stations_df.geojson')
    sdf = sdf.to_crs({'init': 'epsg:4326'})
    sdf['long'] = sdf.geometry.map(lambda x: x.x)
    sdf['lat'] = sdf.geometry.map(lambda x: x.y)

    sdf = sdf[sdf['lat']>1]
    
    if df is None:
        mapdata = go.Scattermapbox(#lat=sdf["lat"], 
                               #lon=sdf["long"],
                               #text=sdf["name"],
                               #marker={'size':2,
                               #        'color':'black'}
                                   )
                  
    else:
        
        if direction == 'start':
            hdf = mobi.make_thdf(df)
        elif direction == 'stop':
            log("make_rhdf")
            hdf = mobi.make_rhdf(df)
        elif direction == 'both':
            hdf = mobi.make_ahdf(df)
        else:
            raise ValueError("argument 'direction' must be on of start/stop/both")


        log("trips_df")
        trips_df = hdf.sum().reset_index()
        trips_df.columns = ['station','trips']
        log("merge")
        trips_df = pd.merge(sdf,trips_df,right_on='station',left_on='name')

        # NOTE: text must be in specific format so it can be parsed by callback function
        log("text")
        text = [ f"{name}<br>{trips} trips" for name,trips in zip(trips_df['name'],trips_df['trips']) ]
        
        log("mapdata")
        mapdata = go.Scattermapbox(lat=trips_df['lat'], 
                                   lon=trips_df['long'],
                                   text=text,   
                                   hoverinfo='text',
                                   marker={'color':color,
                                           'size':trips_df['trips'],
                                           'sizemode':'area',
                                           'sizeref':2.*max(trips_df['trips'])/(40.**2),
                                           'sizemin':4})
    log("fig")
    mapfig = go.Figure(data=mapdata,layout=maplayout)
    log("make_station_map finished")
    return mapfig    


    
    
def make_trips_map(df,direction='start',suff=""):
    log("make_trips_map")
    # https://plot.ly/python/mapbox-layers/

    if suff == "":
        color = c_blue
    elif suff == "2":
        color = c_green
    
    
    cdf = mobi.make_con_df(df)
    cdf = cdf[cdf['Departure lat'] > 1]
    cdf = cdf[cdf['Return lat'] > 1]
    
    sdf = geopandas.read_file(f'{datapath}/data/stations_df.geojson')
    sdf = sdf.to_crs({'init': 'epsg:4326'})
    sdf['long'] = sdf.geometry.map(lambda x: x.x)
    sdf['lat'] = sdf.geometry.map(lambda x: x.y)
    
    
    
    mapdata = [go.Scattermapbox(lat=[cdf.iloc[i].loc["Departure lat"],cdf.iloc[i].loc["Return lat"]], 
                               lon=[cdf.iloc[i].loc["Departure long"],cdf.iloc[i].loc["Return long"]],
                               mode='lines',
                               opacity=0.5,
                               line={
                                'width': 10*cdf.iloc[i].loc['trips'] / max(cdf['trips']),
                                }
                              ) for i in range(len(cdf)) ]
    

    mapdata.append(go.Scattermapbox(lat=sdf['lat'],
                                  lon=sdf['long'],
                                  hoverinfo='text',
                                  opacity=0.3,
                                  marker={'size':4,
                                          'color':c_black
                                          }
                                 )
                 )
    

    if direction == 'start':
        text = [ f"{name}<br>{trips} trips" for name,trips in zip(cdf['Return station'],cdf['trips']) ]
        mapdata.append(go.Scattermapbox(lat=cdf["Return lat"], 
                                   lon=cdf["Return long"],
                                   #text=cdf["Return station"],
                                   text=text,
                                   hoverinfo='text',
                                   marker={'size':cdf['trips'],
                                           'sizemode':'area',
                                           'sizeref':2.*max(cdf['trips'])/(40.**2),
                                           'sizemin':4,
                                           'color':color
                                           }
                                       )
                      )
        
    elif direction == 'stop':
        text = [ f"{name}<br>{trips} trips" for name,trips in zip(cdf['Departure station'],cdf['trips']) ]
        mapdata.append(go.Scattermapbox(lat=cdf["Departure lat"], 
                                   lon=cdf["Departure long"],
                                   #text=cdf["Departure station"],
                                   text=text,    
                                   hoverinfo='text',
                                   marker={'size':cdf['trips'],
                                           'sizemode':'area',
                                           'sizeref':2.*max(cdf['trips'])/(40.**2),
                                           'sizemin':4,
                                           'color':color
                                           }
                                       )
                      )
        
    elif direction == 'both':
        
        adf = mobi.make_ahdf(df).sum().astype(int)
        adf = adf.reset_index()
        adf.columns = ['station','trips']
        adf = pd.merge(adf,sdf,left_on='station',right_on='name')
        
        text = [ f"{name}<br>{trips} trips" for name,trips in zip(adf['station'],adf['trips']) ]
        mapdata.append(go.Scattermapbox(lat=adf["lat"], 
                                   lon=adf["long"],
                                   #text=cdf["Departure station"],
                                   text=text,    
                                   hoverinfo='text',
                                   marker={'size':5,
                                           'color':color
                                           }
                                       )
                      )


    mapfig = go.Figure(data=mapdata,layout=maplayout)

    
    log("make_trips_map finished")
    return mapfig    
    

def make_daily_fig(df=None,wdf=None, suff=""):
    log("make_daily_fig")
    
    if suff == "":
        color = c_blue
    elif suff == "2":
        color = c_green
    
    daily = False
    
    if df is None:
        trips_df = pd.DataFrame(columns=[0,1])
        wddf = pd.DataFrame(columns=['precipIntensity','temperature'])
  
    else:
        
        thdf = mobi.make_thdf(df) 
        
        t1 = df.iloc[0].loc['Departure']
        t2 = df.iloc[-1].loc['Departure']
        wddf = wdf[t1:t2]
        

        if len(thdf) < 24*370:   # less than 1 year of data provide hourly counts, otherwise daily
            trips_df = thdf.sum(1).reset_index() 
            
        else:
            daily = True
            trips_df = thdf.groupby(pd.Grouper(freq='d')).sum().sum(1).reset_index()
            wddf = wddf[['precipIntensity','temperature']].groupby(pd.Grouper(freq='d')).agg(
                                                                        {'precipIntensity':sum,'temperature':max}
                                                                        )
    yaxis_title="Hourly Trips" if not daily else "Daily Trips"
    yaxis_title_weather = 'Precipitation (mm)' if daily else 'Precipitation (mm/h)'

    trips_df.columns = ['Time','Trips']

    layout = go.Layout(#title='Hourly Mobi Trips',
                   paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',
                                  
                   margin=margin,

                   yaxis =  {
                     'fixedrange': True,
                     'domain':[0.3,1],
                     'showline':True,
                     'linewidth':1, 
                     'linecolor':c_gray_600,
                   },

                   yaxis2={'domain':[0, 0.25],
                            'showline':True,
                            'linewidth':1,
                            'linecolor':c_gray_600},
                    
                   xaxis2={
                            'anchor':"y2",
                            'showline':True,
                            'linewidth':1,
                            'linecolor':c_gray_600                       
                           },
                    
                   showlegend=False

              )

    
    
    fig = make_subplots(rows=2, cols=1, row_heights=[0.8, 0.2],shared_xaxes=True,
                       specs=[[{"secondary_y": False}], [{"secondary_y": True}]])
    
    if not daily:
        print("short")
        fig.add_trace(go.Bar(
            x=trips_df['Time'],
            y=trips_df['Trips'],
            marker={'color':color},
            name='Hourly Trips',
        ),
            row=1,col=1
                )
    else:
        print("long")
        fig.add_trace(go.Bar(
            x=trips_df['Time'],
            y=trips_df['Trips'],
            marker={'color':color},
            name='Daily Trips',
        ),
            row=1,col=1
                )
    
    

    
    
    
    fig.add_trace(go.Scatter(
                    x=wddf.index,
                    y=wddf['temperature'],
                    marker_color=c_yellow,
                    name='Temperature'
                    ),
                row=2,col=1,
                  
                 )
    fig.add_trace(go.Bar(
                    x=wddf.index,
                    y=wddf['precipIntensity'],
                    marker_color=c_light_blue,
                    name='Precipitation'
                    ),
                row=2,col=1,
                secondary_y=True
                 )

    fig.update_layout(layout)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=c_gray_400)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=c_gray_400,title_text=yaxis_title,row=1,col=1)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=c_gray_400,title_text='Temparture (°C)',row=2,col=1)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=c_gray_400,title_text=yaxis_title_weather,row=2,col=1,secondary_y=True)

    if df is not None and (trips_df.loc[trips_df.index[-1],'Time'] - trips_df.loc[0,'Time']).days < 1:
        date = trips_df.loc[0,'Time']
        t1 = dt.datetime(date.year,date.month,date.day,0)
        t2 = dt.datetime(date.year,date.month,date.day,23)
        fig.update_layout(xaxis_range=[t1,t2])
                               

    log("make_daily_fig finished")
    return fig

def make_memb_fig(df=None,suff=""):
    
    log("make_memb_fig")
    if df is None:
        return go.Figure(data=[go.Pie(labels=['1','2'], values=[10,20], hole=.3)])
    
    memtypes = list(set(df['Membership Simple']))
    memtypes_member = list(set(df.loc[df['Membership Category']=='Member','Membership Simple']))
    memtypes_casual = list(set(df.loc[df['Membership Category']=='Casual','Membership Simple']))

    
    pdf = df.pivot_table(values='Departure',index='Month',columns='Membership Simple',aggfunc='count')
    memb_trips = pdf.fillna(0).astype(int).sum()
    memb_trips = memb_trips.sort_values(ascending=False)
    memb_trips = memb_trips.to_dict()


    labels = ['Member','Casual'] + list(memtypes_member) + list(memtypes_casual)
    parents = ["", ""] +  ["Member"]*len(memtypes_member) + ["Casual"]*len(memtypes_casual)
    values = [sum([memb_trips[x] for x in list(labels) if x in memtypes_member]),sum([memb_trips[x] for x in labels if x in memtypes_casual])]+ [memb_trips[x] for x in list(memtypes_member) + list(memtypes_casual)]

    
    fig =go.Figure(go.Sunburst(
        labels=labels,
        parents=parents ,
        values= values,
        branchvalues="total",
        marker={'colors':[c_purple,c_light_blue]}
    ))
    
    fig.update_layout(margin = dict(t=1, l=0, r=0, b=0))

    log("make_memb_fig finished")
    return fig
        

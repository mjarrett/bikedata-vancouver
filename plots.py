import plotly.graph_objects as go
import mobitools as mobi
import pandas as pd
from datetime import datetime
from credentials import *

margin=go.layout.Margin(
    l=5,
    r=5,
    b=5,
    t=5,
    pad=0)





def make_timeseries_fig(thdf, date=None):
    print('make_timeseries_fig')
   
    
    trips_hdf = thdf.sum(1).reset_index()
    trips_hdf.columns = ['Hour','Trips']

    tddf = thdf.groupby(pd.Grouper(freq='d')).sum()
    trips_ddf = tddf.sum(1)
    trips_ddf = trips_ddf.reset_index()
    trips_ddf.columns = ['Date','Trips']
    
    if date == None:
        colors = [ '#1e5359' for x in trips_ddf['Date'] ] 
    elif len(date) == 2:
        colors = [ '#1e5359' if (x >= datetime.strptime(date[0], '%Y-%m-%d')) and (x <= datetime.strptime(date[1], '%Y-%m-%d')) else 'lightslategray' for x in trips_ddf['Date']] 
        
    else:
        colors = [ '#1e5359' if x is True else 'lightslategray' for x in trips_ddf['Date'] == date ] 

    data = [go.Bar(
            x=trips_ddf['Date'],
            y=trips_ddf['Trips'],
            marker_color = colors
                )
           ]
    layout = go.Layout(#title='Daily Mobi Trips',
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       yaxis =  {
                         'fixedrange': True
                       },
                       margin=margin
                  )

    fig = go.Figure(data=data,layout=layout)
    
    return fig

def make_station_map(df=None, direction='start'):
    print('make_station_map')
    
    

    
    
    
    # https://plot.ly/python/mapbox-layers/
    sdf = mobi.get_stationsdf('./data/')
    sdf = sdf.to_crs({'init': 'epsg:4326'})
    sdf['long'] = sdf.geometry.map(lambda x: x.x)
    sdf['lat'] = sdf.geometry.map(lambda x: x.y)

    sdf = sdf[sdf['lat']>1]
    
    if df is None:
        mapdata = go.Scattermapbox(lat=sdf["lat"], 
                               lon=sdf["long"],
                               text=sdf["name"],
                               marker={'size':2,
                                       'color':'black'}
                                   )
                  
    else:
        if direction == 'start':
            hdf = mobi.system.make_thdf(df)
        elif direction == 'stop':
            hdf = mobi.system.make_rhdf(df)
        elif direction == 'both':
            hdf = mobi.system.make_ahdf(df)
        else:
            raise ValueError("argument 'direction' must be on of start/stop/both")
        
        #thdf = mobi.system.make_thdf(df)
        ddf = hdf.groupby(pd.Grouper(freq='d')).sum()
        
        trips_df = ddf.sum().reset_index()
        trips_df.columns = ['station','trips']

        trips_df = pd.merge(sdf,trips_df,right_on='station',left_on='name')

        text = [ f"{name}<br>{trips} trips" for name,trips in zip(trips_df['name'],trips_df['trips']) ]
        
        mapdata = go.Scattermapbox(lat=trips_df['lat'], 
                                   lon=trips_df['long'],
                                   text=text,   # NOTE: text must be in specific format so it can be parsed by callback function
                                   marker={'size':trips_df['trips'],
                                           'sizemode':'area',
                                           'sizeref':2.*max(trips_df['trips'])/(40.**2),
                                           'sizemin':4})
    maplayout = go.Layout(#title=date,
                          mapbox_style="light",
                          mapbox=go.layout.Mapbox(
                            accesstoken=MAPBOX_TOKEN,
                            bearing=0,
                            center=go.layout.mapbox.Center(
                                lat=49.28, 
                                lon=-123.12
                                ),
                            pitch=0,
                            zoom=11
                            ),
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          #showlegend = True,
                          margin=margin
                          #width=500,
                          #height=500
                         )
    mapfig = go.Figure(data=mapdata,layout=maplayout)
    return mapfig    


    
    
def make_trips_map(df,direction='start'):
    print('make_trips_map')
    # https://plot.ly/python/mapbox-layers/

    
    cdf = mobi.system.make_con_df(df)

    
    mapdata = [go.Scattermapbox(lat=[cdf.iloc[i].loc["start coords"][0],cdf.iloc[i].loc["stop coords"][0]], 
                               lon=[cdf.iloc[i].loc["start coords"][1],cdf.iloc[i].loc["stop coords"][1]],
                               mode='lines',
                               opacity=0.5,
                               line={
                                'width': 10*cdf.iloc[i].loc['trips'] / max(cdf['trips']),
                                }
                              ) for i in range(len(cdf)) ]
    
    sdf = mobi.get_stationsdf('./data/')   
    sdf = mobi.sdf_to_latlong(sdf)
    sdf['lat'] = sdf.coordinates.map(lambda x: x[0])
    sdf['long'] = sdf.coordinates.map(lambda x: x[1])
    mapdata.append(go.Scattermapbox(lat=sdf["lat"], 
                               lon=sdf["long"],
                               text=sdf["name"],
                               marker={'size':2,
                                       'color':'black'}
                                   )
                  )
        
        
    maplayout = go.Layout(#title=date,
                          mapbox_style="light",
                          mapbox=go.layout.Mapbox(
                            accesstoken=MAPBOX_TOKEN,
                            bearing=0,
                            center=go.layout.mapbox.Center(
                                lat=49.28, 
                                lon=-123.12
                                ),
                            pitch=0,
                            zoom=11
                            ),
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)',
                          showlegend = False,
                          margin=margin
                          #width=500,
                          #height=500
                         )
    mapfig = go.Figure(data=mapdata,layout=maplayout)
    return mapfig    
    

def make_daily_fig(df=None):
    print(f"make_daily_fig")

    if df is None:
        trips_df = pd.DataFrame(columns=[0,1])
  
    else:
        thdf = mobi.system.make_thdf(df)  
        trips_df = thdf.sum(1).reset_index()    


    trips_df.columns = ['Time','Trips']
    data = [go.Bar(
        x=trips_df['Time'],
        y=trips_df['Trips']
            )
       ]
    layout = go.Layout(#title='Hourly Mobi Trips',
                   paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',
                   yaxis =  {
                     'fixedrange': True
                   },
                   margin=margin
                   #height=500,
                   #width=500
              )
    fig = go.Figure(data=data,layout=layout)
    return fig



def make_map(df=None,state=None,switch=None):
    print(f'map_state: {state}')
    if state == 'stations': 
        if not switch:
            return make_station_map(df)
        elif switch:
            return make_trips_map(df)
            
    elif state == 'trips':
        if not switch:
            return make_trips_map(df)
        if switch:
            return make_station_map(df)
    else:
        raise ValueError("arg 'state' must be one of ['stations','trips']")
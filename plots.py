import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import geopandas
import mobisys as mobi
from credentials import *

margin=go.layout.Margin(
    l=5,
    r=5,
    b=5,
    t=5,
    pad=0)


maincolor = '#1e5359'
          



def make_timeseries_fig(thdf, date=None):
    print('make_timeseries_fig')
   
    
    trips_hdf = thdf.sum(1).reset_index()
    trips_hdf.columns = ['Hour','Trips']

    tddf = thdf.groupby(pd.Grouper(freq='d')).sum()
    trips_ddf = tddf.sum(1)
    trips_ddf = trips_ddf.reset_index()
    trips_ddf.columns = ['Date','Trips']
    
    if date == None:
        colors = [ maincolor for x in trips_ddf['Date'] ] 
    elif len(date) == 2:
        colors = [ maincolor if (x >= datetime.strptime(date[0], '%Y-%m-%d')) and (x <= datetime.strptime(date[1], '%Y-%m-%d')) else 'lightslategray' for x in trips_ddf['Date']] 
        
    else:
        colors = [ maincolor if x is True else 'lightslategray' for x in trips_ddf['Date'] == date ] 

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
                       margin=margin,
                       #autosize=True,
                       dragmode='select'
                  )

    fig = go.Figure(data=data,layout=layout)
    
    return fig

def make_station_map(df=None, direction='start'):
    print('make_station_map')
      
    
    # https://plot.ly/python/mapbox-layers/
    sdf = geopandas.read_file(f'./data/stations_df.geojson')
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
            hdf = mobi.make_rhdf(df)
        elif direction == 'both':
            hdf = mobi.make_ahdf(df)
        else:
            raise ValueError("argument 'direction' must be on of start/stop/both")
        
        #thdf = mobi.make_thdf(df)
        ddf = hdf.groupby(pd.Grouper(freq='d')).sum()
        
        trips_df = ddf.sum().reset_index()
        trips_df.columns = ['station','trips']

        trips_df = pd.merge(sdf,trips_df,right_on='station',left_on='name')

        text = [ f"{name}<br>{trips} trips" for name,trips in zip(trips_df['name'],trips_df['trips']) ]
        
        mapdata = go.Scattermapbox(lat=trips_df['lat'], 
                                   lon=trips_df['long'],
                                   text=text,   # NOTE: text must be in specific format so it can be parsed by callback function
                                   hoverinfo='text',
                                   marker={'color':maincolor,
                                           'size':trips_df['trips'],
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

    
    cdf = mobi.make_con_df(df)

    
    mapdata = [go.Scattermapbox(lat=[cdf.iloc[i].loc["start coords"][0],cdf.iloc[i].loc["stop coords"][0]], 
                               lon=[cdf.iloc[i].loc["start coords"][1],cdf.iloc[i].loc["stop coords"][1]],
                               mode='lines',
                               opacity=0.5,
                               line={
                                'width': 10*cdf.iloc[i].loc['trips'] / max(cdf['trips']),
                                }
                              ) for i in range(len(cdf)) ]
    

#     sdf['lat'] = sdf.coordinates.map(lambda x: x[0])
#     sdf['long'] = sdf.coordinates.map(lambda x: x[1])
    cdf['start lat'] = cdf['start coords'].map(lambda x: x[0])
    cdf['start long'] = cdf['start coords'].map(lambda x: x[1])
    cdf['stop lat'] = cdf['stop coords'].map(lambda x: x[0])
    cdf['stop long'] = cdf['stop coords'].map(lambda x: x[1])
    mapdata.append(go.Scattermapbox(lat=cdf["stop lat"], 
                               lon=cdf["stop long"],
                               text=cdf["stop station"],
                               hoverinfo='text',
                               marker={'size':4,
                                       'color':maincolor}
                                   )
                  )
    mapdata.append(go.Scattermapbox(lat=cdf["start lat"], 
                               lon=cdf["start long"],
                               text=cdf["start station"],
                               hoverinfo='text',
                               marker={'size':4,
                                       'color':maincolor}
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
        
        thdf = mobi.make_thdf(df)  
        if len(thdf) < 24*32:
            trips_df = thdf.sum(1).reset_index() 
        else:
            trips_df = thdf.groupby(pd.Grouper(freq='d')).sum().sum(1).reset_index()

    trips_df.columns = ['Time','Trips']
    data = [go.Bar(
        x=trips_df['Time'],
        y=trips_df['Trips'],
        marker={'color':maincolor}
            )
       ]
    layout = go.Layout(#title='Hourly Mobi Trips',
                   paper_bgcolor='rgba(0,0,0,0)',
                   plot_bgcolor='rgba(0,0,0,0)',
                   yaxis =  {
                     'fixedrange': True
                   },
                   margin=margin,
                   #height=500,
                   #width=500
              )
    fig = go.Figure(data=data,layout=layout)
    

    if df is not None and (trips_df.loc[trips_df.index[-1],'Time'] - trips_df.loc[0,'Time']).days < 1:
        date = trips_df.loc[0,'Time']
        t1 = datetime(date.year,date.month,date.day,0)
        t2 = datetime(date.year,date.month,date.day,23)
        fig.update_layout(xaxis_range=[t1,t2])
                               
    return fig


def make_memb_fig(df):
    if df is None:
        return go.Figure(data=[go.Pie(labels=['1','2'], values=[10,20], hole=.3)])
    
    pdf = df.pivot_table(values='Departure',index='Month',columns='Membership Simple',aggfunc='count')
    memb_trips = pdf.fillna(0).astype(int).sum()
    
    fig = go.Figure(data=[go.Pie(labels=memb_trips.index, values=memb_trips.values, hole=.3)])
    return fig
        

import plotly.graph_objects as go
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

c_dark_teal = '#1e5359'
          
c_blue =     '#007bff' #!default; // primary
c_indigo =   '#6610f2' #!default;
c_purple =   '#6f42c1' #!default;
c_pink =     '#e83e8c' #!default;
c_red =      '#dc3545' #!default; // danger
c_orange =   '#fd7e14' #!default;
c_yellow =   '#ffc107' #!default; // warning
c_green =    '#28a745' #!default; // success
c_teal =     '#20c997' #!default;
c_cyan =     '#17a2b8' #!default; // info


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


colors = [c_blue,c_indigo,c_red,c_green,c_orange,c_teal,c_cyan,c_purple,c_yellow]

def make_timeseries_fig(thdf, date=None, date2=None):

    
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
    else:
        color = c_blue
      


    data = [go.Bar(
            x=trips_ddf['Date'],
            y=trips_ddf['Trips'],
            marker_color = color,
            name="Daily trips"
                )
           ]
    
    layout = go.Layout(paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       yaxis = {
                         'fixedrange': True,
                         'showgrid':   False
                               },
                       xaxis={'showgrid':False
                              },
                       margin=margin,
                       #autosize=True,
                       dragmode='select',
                       legend=go.layout.Legend(
                            x=0,
                            y=1,
                            traceorder="normal",
                        )
            
                  )

    fig = go.Figure(data=data,layout=layout)
    
    def add_highlight(date,color):
        print(date)
        if date is None:
            return None
        
        elif date is not None:
            if len(date) == 2:
                d1 = dt.datetime.strptime(date[0],'%Y-%m-%d') - dt.timedelta(0.5)
                d2 = dt.datetime.strptime(date[1],'%Y-%m-%d') + dt.timedelta(0.5)
            else:
                d1 = dt.datetime.strptime(date,'%Y-%m-%d') - dt.timedelta(0.5)
                d2 = d1 + dt.timedelta(1)

            shape = go.layout.Shape(
                    type="rect",
                    # x-reference is assigned to the x-values
                    xref="x",
                    # y-reference is assigned to the plot paper [0,1]
                    yref="paper",
                    x0=d1,
                    y0=0,
                    x1=d2,
                    y1=1,
                    fillcolor=color,
                    opacity=0.5,
                    layer="below",
                    line_width=0,
                )

            return shape

    shapes = [add_highlight(date,c_blue),add_highlight(date2,c_green)]
    fig.update_layout(shapes=[x for x in shapes if x is not None])
   
    

    
    # Add rolling average
    fig.add_trace(go.Scatter(
                    x=trips_rdf['Date'],
                    y=trips_rdf['Trips'],
                    name="Rolling average",
                    marker_color = c_cyan,
                    hoverinfo = 'skip'
                    )
                 )
    
    return fig

def make_station_map(df=None, direction='start', suff=""):
      
    if suff == "":
        color = c_blue
    elif suff == "2":
        color = c_green
    
    # https://plot.ly/python/mapbox-layers/
    sdf = geopandas.read_file(f'{datapath}/stations_df.geojson')
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
                                   marker={'color':color,
                                           'size':trips_df['trips'],
                                           'sizemode':'area',
                                           'sizeref':2.*max(trips_df['trips'])/(40.**2),
                                           'sizemin':4})
    
    mapfig = go.Figure(data=mapdata,layout=maplayout)
    return mapfig    


    
    
def make_trips_map(df,direction='start',suff=""):
    # https://plot.ly/python/mapbox-layers/

    if suff == "":
        color = c_blue
    elif suff == "2":
        color = c_green
    
    
    cdf = mobi.make_con_df(df)
    cdf = cdf[cdf['Departure lat'] > 1]
    cdf = cdf[cdf['Return lat'] > 1]
    
    sdf = geopandas.read_file(f'{datapath}/stations_df.geojson')
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
    return mapfig    
    

def make_daily_fig(df=None, suff=""):

    
    if suff == "":
        color = c_blue
    elif suff == "2":
        color = c_green
    
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
        marker={'color':color}
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
        t1 = dt.datetime(date.year,date.month,date.day,0)
        t2 = dt.datetime(date.year,date.month,date.day,23)
        fig.update_layout(xaxis_range=[t1,t2])
                               
    return fig


def make_memb_fig(df=None,suff=""):
    
    
    if df is None:
        return go.Figure(data=[go.Pie(labels=['1','2'], values=[10,20], hole=.3)])
    
    pdf = df.pivot_table(values='Departure',index='Month',columns='Membership Simple',aggfunc='count')
    memb_trips = pdf.fillna(0).astype(int).sum()
    
    fig = go.Figure(data=[go.Pie(labels=memb_trips.index, 
                                 values=memb_trips.values, 
                                 hole=.3,
                                 marker={'colors':colors})])
    return fig
        

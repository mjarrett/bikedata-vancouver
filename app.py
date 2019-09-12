# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State


import mobitools as mobi
import pandas as pd
from credentials import *



#######################################################################################
#
#  SETUP
#
#######################################################################################

df = mobi.system.prep_sys_df('Mobi_System_Data.csv')
thdf = mobi.system.make_thdf(df)
trips_hdf = thdf.sum(1).reset_index()
trips_hdf.columns = ['Hour','Trips']

tddf = thdf.groupby(pd.Grouper(freq='d')).sum()
print(tddf.head())
trips_ddf = tddf.sum(1)
trips_ddf = trips_ddf.reset_index()
trips_ddf.columns = ['Date','Trips']

margin=go.layout.Margin(
    l=5,
    r=5,
    b=5,
    t=5,
    pad=0)

def make_timeseries_fig(date=None):

    data = [go.Bar(
            x=trips_ddf['Date'],
            y=trips_ddf['Trips']
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

def make_station_map(date='2018-01-01'):
    # https://plot.ly/python/mapbox-layers/
    sdf = mobi.get_stationsdf('../mobi/')
    sdf['lat'] = sdf.coordinates.map(lambda x: x[0])
    sdf['long'] = sdf.coordinates.map(lambda x: x[1])
    sdf = sdf[sdf['lat']>1]
    
    
    if len(date) == 2:
        trips_alltime = tddf.loc[date[0]:date[1]].sum().reset_index()
    else:
        trips_alltime = tddf.loc[date].reset_index()
    trips_alltime.columns = ['station','trips']
    sdf = pd.merge(trips_alltime,sdf,left_on='station',right_on='name')


    mapdata = go.Scattermapbox(lat=sdf["lat"], 
                               lon=sdf["long"],
                               marker={'size':sdf['trips'],
                                       'sizemode':'area',
                                       'sizeref':2.*max(sdf['trips'])/(40.**2),
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
    
def make_trips_map(date='2018-01-01'):
    # https://plot.ly/python/mapbox-layers/
    sdf = mobi.get_stationsdf('../mobi/')
    sdf['lat'] = sdf.coordinates.map(lambda x: x[0])
    sdf['long'] = sdf.coordinates.map(lambda x: x[1])
    sdf = sdf[sdf['lat']>1]
    
    
    if len(date) == 2:
        ddf = df.set_index('Departure').loc[date[0]:date[1]]
    else:
        ddf = df.set_index('Departure').loc[date]

    print(ddf.head())
    print(ddf.tail())
    

    ddf = mobi.system.add_station_coords(ddf,sdf)
    
    
    mapdata = [go.Scattermapbox(lat=[ddf.iloc[i].loc["Departure coords"][0],ddf.iloc[i].loc["Return coords"][0]], 
                               lon=[ddf.iloc[i].loc["Departure coords"][1],ddf.iloc[i].loc["Return coords"][1]],
                               mode='lines',
                               opacity=0.5,
                               line={
                                'width': 2,
                                }
                              ) for i in range(len(ddf)) ]
              

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
    

def make_daily_fig(date='2018-01-01'):
    print(f"make_daily_fig")
    print(f"date: {date}")

    if len(date) == 2:
        trips_df = thdf.loc[date[0]:date[1],:].sum(1).reset_index()
    else:
        trips_df = thdf.loc[date,:].sum(1).reset_index()    

    print(trips_df.head())
    print(trips_df.tail())
    trips_df.columns = ['Time','Trips']
    data = [go.Scatter(
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
    





#######################################################################################
#
#  LAYOUT
#
#######################################################################################
    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Let's copy https://github.com/plotly/dash-sample-apps/blob/master/apps/dash-oil-and-gas/
app.layout = html.Div(id="mainContainer",children=[
    html.H1(children='Hello Dash'),

    
    
    
    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    
    html.Div(id='row1_container', className="simple_container", children=[
    
        html.Div(className="pretty_container", children=[

            dcc.Graph(
                id='timeseries-graph',
                figure=make_timeseries_fig() 
            )
        ])
    ]),
    
    html.Div(id='row2_container', className="simple_container", children=[
    
        html.Div(id='map_container', className="pretty_container row", children=[
            dcc.Graph(
                id='map-graph',
                figure=make_station_map()  
            )
        ]),

        html.Div(id='daily_container', className="pretty_container row", children=[
            dcc.Graph(
                id='daily-graph',
                figure=make_daily_fig()
                )
        ]),
        
        html.Div(id='trips_container', className="pretty_container row", children=[
            dcc.Graph(
                id='trips-graph',
                figure=make_trips_map()
                )
        ])
    ])
])



#######################################################################################
#
#  CALLBACKS
#
#######################################################################################
@app.callback([Output('timeseries-graph','figure'), Output('map-graph','figure'), Output('daily-graph','figure')],
              [Input('timeseries-graph','clickData'), Input('timeseries-graph','selectedData')],
              [State('timeseries-graph','figure')])
def update_timeseries_text(clickData, selectedData, timeseries_graph_figure):
    print(dash.callback_context.triggered)  # last triggered
    print(dash.callback_context.inputs)     # all triggered
    print(dash.callback_context.states)

    #if dash.callback_context.inputs['timeseries-graph.clickData'] is not None:
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        date = clickData['points'][0]['x']
    elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        date = (selectedData['points'][0]['x'],selectedData['points'][-1]['x'])
    
    print(date)
    return  timeseries_graph_figure, make_station_map(date), make_daily_fig(date)



if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8051)

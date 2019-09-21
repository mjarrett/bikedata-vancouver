from helpers import *
from plots import *

def timeseries_clickdata_callback(callback_context, df, thdf):
    date = callback_context.inputs['timeseries-graph.clickData']['points'][0]['x']
    filter_dropdown_values = callback_context.states['filter-dropdown.value']
    ddf = filter_ddf(df,date=date, stations=None, cats=filter_dropdown_values)
    return  make_timeseries_fig(thdf,date), make_station_map(ddf), make_daily_fig(ddf), 'stations'

def timeseries_selectdata_callback(callback_context, df, thdf):
    dates = [x['x'] for x in callback_context.inputs['timeseries-graph.selectedData']['points'] ] 
    date = (dates[0], dates[-1])
    filter_dropdown_values = callback_context.states['filter-dropdown.value']
    ddf = filter_ddf(df,date=date, stations=None, cats=filter_dropdown_values)
    return  make_timeseries_fig(thdf,date), make_station_map(ddf), make_daily_fig(ddf), 'stations'
    
    
def map_click_callback(callback_context, df, thdf):
            
    if callback_context.inputs['timeseries-graph.clickData'] is not None:
        date = callback_context.inputs['timeseries-graph.clickData']['points'][0]['x']
    elif callback_context.inputs['timeseries-graph.selectedData'] is not None:
        dates = [x['x'] for x in callback_context.inputs['timeseries-graph.selectedData']['points'] ] 
        date = (dates[0], dates[-1])
    station = callback_context.inputs['map-graph.clickData']['points'][0]['text'].split('<')[0].strip()
    filter_dropdown_values = callback_context.states['filter-dropdown.value']
    ddf = filter_ddf(df,date=date, stations=[station], cats=filter_dropdown_values)
    
    timeseries_graph_figure = callback_context.states['timeseries-graph.figure']
    daily_graph_figure = callback_context.states['daily-graph.figure']
    
    return timeseries_graph_figure, make_trips_map(ddf), make_daily_fig(ddf), 'trips'

def reset_button_callback(callback_context, df, thdf):
    if dash.callback_context.inputs['timeseries-graph.clickData'] is not None:
        date = dash.callback_context.inputs['timeseries-graph.clickData']['points'][0]['x']
    else:
        dates = [x['x'] for x in callback_context.inputs['timeseries-graph.selectedData']['points'] ] 
        date = (dates[0], dates[-1])
    filter_dropdown_values = callback_context.states['filter-dropdown.value']
    ddf = filter_ddf(df,date=date, stations=None, cats=filter_dropdown_values)
    
    timeseries_graph_figure = callback_context.states['timeseries-graph.figure']
    
    return  timeseries_graph_figure, make_station_map(ddf), make_daily_fig(ddf), 'stations'


def filter_button_callback(callback_context,df, thdf):
    print("WARNING: Filter button doesn't know which of clickdata or selectdata was called most recently")
    if callback_context.inputs['timeseries-graph.clickData'] is not None:
        date = callback_context.inputs['timeseries-graph.clickData']['points'][0]['x']
    elif callback_context.inputs['timeseries-graph.selectedData'] is not None:
        dates = [x['x'] for x in callback_context.inputs['timeseries-graph.selectedData']['points'] ] 
        date = (dates[0], dates[-1])
    else:
        date = None
    
    if callback_context.inputs['map-graph.clickData'] is not None:
        stations = [callback_context.inputs['map-graph.clickData']['points'][0]['text'].split('<')[0].strip()]
    else:
        stations = None
    
    filter_dropdown_values = callback_context.states['filter-dropdown.value']
    map_state = callback_context.states['map-state.children']
    timeseries_graph_figure = callback_context.states['timeseries-graph.figure']
    


    if map_state == 'stations': 
        ddf = filter_ddf(df,date=date, stations=None, cats=filter_dropdown_values)
        return timeseries_graph_figure, make_station_map(ddf), make_daily_fig(ddf), map_state 

    elif map_state == 'trips':
        ddf = filter_ddf(df,date=date, stations=stations, cats=filter_dropdown_values)
        return timeseries_graph_figure, make_trips_map(ddf), make_daily_fig(ddf), map_state





from helpers import *
from plots import *

def filter_button_callback(callback_context,df):
    if callback_context.inputs['timeseries-graph.clickData'] is not None:
        date = callback_context.inputs['timeseries-graph.clickData']['points'][0]['x']
    elif callback_context.inputs['timeseries-graph.selectedData'] is not None:
        dates = callback_context.inputs['timeseries-graph.selectedData']
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




    return  timeseries_graph_figure, make_map(df=ddf,state=map_state,switch=False), make_daily_fig(ddf), map_state 
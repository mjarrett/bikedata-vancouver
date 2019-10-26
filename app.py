# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from datetime import datetime
import mobisys as mobi
import pandas as pd
import urllib
import json

from credentials import *
from plots import * 
from helpers import *
from layouts import *



 
    
external_stylesheets=[dbc.themes.BOOTSTRAP,"https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)





            




body = dbc.Container(id="mainContainer",children=[
    
    summary_jumbo,
    
    summary_cards,
    
    main_div,
    
    detail_div,
    
        
])  

app.layout = html.Div([header,body,footer])
                                             
#######################################################################################
#
#  CALLBACKS
#
#######################################################################################


@app.callback(Output('detail-div-status','children'),
              [Input('go-button','n_clicks')],
             )
def update_detail_status(n_clicks):
    log("**update_detail_status callback")
    log(f"n clicks: {n_clicks}")
    if n_clicks is None:
        log("d-none")
        return "d-none"
    else:
        log("")
        return ""

@app.callback(Output('detail-div-status2','children'),
              [Input('go-button2','n_clicks')]
             )
def update_detail_status2(n_clicks):
    log("**update_detail_status callback2")
    log(f"n clicks: {n_clicks}")
    if n_clicks is None:
        log("d-none")
        return "d-none"
    else:
        log("")
        return ""
    
@app.callback([Output('header-div','className'), Output('detail-cards-div','className'),
               Output('daily-div','className'), Output('map-div','className'),
               Output('memb-div','className'), Output('explore-div','className'),
               Output('header-div2','className'), Output('detail-cards-div2','className'),
               Output('daily-div2','className'), Output('map-div2','className'),
               Output('memb-div2','className'), Output('explore-div2','className')],
               #[Input('go-button','n_clicks'), Input('filter-meta-div','children'), Input('filter-meta-div2','children')]
#                [Input('go-button','n_clicks'), Input('go-button2','n_clicks')],
               [Input('detail-div-status','children'), Input('detail-div-status2','children')]
             ) 
# def toggle_div_visibility(n_clicks, filter_data, filter_data2):
def toggle_div_visibility(status, status2):

    log('**toggle_div_visibility callback')
    log(status, status2)
    
    if status == 'd-none':
        log("Hidding both")
        date_1_divs = ["d-none"]*6
        date_2_divs = ["d-none"]*6       
        
    elif status2 == 'd-none':
        log("show date1")
        date_1_divs = [""]*6
        date_2_divs = ["d-none"]*6
    else:
        log("show both")
        date_1_divs = [""]*6
        date_2_divs = [""]*6
        
    return date_1_divs + date_2_divs


@app.callback(Output('timeseries-graph','figure'),
             [Input('filter-meta-div','children'),Input('filter-meta-div2','children')]
             ) 
def timeseries_callback(filter_data,filter_data2):
    log('timeseries_callback')
    
    filter_data = json.loads(filter_data)
    filter_data2 = json.loads(filter_data2)

    return make_timeseries_fig(thdf,filter_data['date'],filter_data2['date'])


@app.callback([Output('datepicker','start_date'), Output('datepicker','end_date'),
               Output('datepicker','initial_visible_month')],
              [Input('timeseries-graph','clickData'), Input('timeseries-graph','selectedData')],
              [State("filter-meta-div",'children')]
             )
def update_datepicker_from_graph(clickData, selectedData, filter_data):
    
    if clickData is None and selectedData is None:
        raise PreventUpdate
        
    filter_data = json.loads(filter_data)
    
    if filter_data['date'] is not None:
        raise PreventUpdate
    
    
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        date = clickData['points'][0]['x']
        return (date, date, date)
    elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        dates = [x['x'] for x in selectedData['points'] ]
        return (dates[0], dates[-1],dates[0])
    
    else:
        raise PreventUpdate    
    
@app.callback([Output('datepicker2','start_date'), Output('datepicker2','end_date'),
               Output('datepicker2','initial_visible_month')],
              [Input('timeseries-graph','clickData'), Input('timeseries-graph','selectedData')],
              [State("filter-meta-div2",'children')]
             )
def update_datepicker_from_graph(clickData, selectedData, filter_data):
    
    if clickData is None and selectedData is None:
        raise PreventUpdate
        
    filter_data = json.loads(filter_data)
    
    if filter_data['date'] is not None:
        raise PreventUpdate
    
    
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        date = clickData['points'][0]['x']
        return (date, date, date)
    elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        dates = [x['x'] for x in selectedData['points'] ]
        return (dates[0], dates[-1],dates[0])
    
    else:
        raise PreventUpdate  



        
# Keep track of filter
@app.callback(Output("filter-meta-div",'children'),
              [Input('go-button','n_clicks'),
               Input('map-graph','clickData'),
               Input('stations-radio','value'),
               Input('map-return-link','n_clicks')],
              [State("filter-meta-div",'children'),
               State('datepicker','start_date'), 
               State('datepicker','end_date'),
               State('filter-dropdown','value')]
             )
def update_filter_meta_div(n_clicks,clickData,radio_value, return_nclicks, 
                           filter_data,
                           start_date,end_date,filter_values):
    if clickData is None and n_clicks is None:
        raise PreventUpdate
    
    log("update_filter_meta_div")
    log("trigger: ",dash.callback_context.triggered)  # last triggered
    filter_data = json.loads(filter_data)
    
    # IF go-button is triggered, update all values
    if  dash.callback_context.triggered[0]['prop_id'] == 'go-button.n_clicks':
        date = convert_dates(start_date,end_date)
         
        filter_data = {'date':date, 'cats':filter_values, 'stations':None, 'direction':'start'}

      
    # If map #1 is clicked           
    if clickData is not None:
        station = clickData['points'][0]['text'].split('<')[0].strip()
        filter_data['stations'] = [station]
       
        
    # If radio1 is clicked
    if  dash.callback_context.triggered[0]['prop_id'] == 'stations-radio.value':
        if radio_value == filter_data['direction']:
            raise PreventUpdate
        else:
            filter_data['direction'] = radio_value
            
    # If return button triggered
    if  dash.callback_context.triggered[0]['prop_id'] == 'map-return-link.n_clicks':
        filter_data['stations'] = None
    
    return json.dumps(filter_data)


# Keep track of filter2
@app.callback(Output("filter-meta-div2",'children'),
              [Input('go-button2','n_clicks'),
               Input('map-graph2','clickData'),
               Input('stations-radio2','value'),
               Input('map-return-link2','n_clicks')],
              [State("filter-meta-div2",'children'),
               State('datepicker2','start_date'), 
               State('datepicker2','end_date'),
               State('filter-dropdown2','value')]
             )
def update_filter_meta_div2(n_clicks,clickData,radio_value,return_nclicks,
                           filter_data,
                           start_date,end_date,filter_values):
    if clickData is None and n_clicks is None:
        raise PreventUpdate
    
    log("update_filter_meta_div2")
    log("trigger: ",dash.callback_context.triggered)  # last triggered
    filter_data = json.loads(filter_data)
    
    # If go-butto2 is triggered, update all values
    if  dash.callback_context.triggered[0]['prop_id'] == 'go-button2.n_clicks':
        date = convert_dates(start_date,end_date)
        
        filter_data = {'date':date, 'cats':filter_values, 'stations':None, 'direction':'start'}

      
    # If map2 is clicked           
    if clickData is not None:
        station = clickData['points'][0]['text'].split('<')[0].strip()
        filter_data['stations'] = [station]
       
        
    # If radio2 is clicked
    if  dash.callback_context.triggered[0]['prop_id'] == 'stations-radio2.value':
        if radio_value == filter_data['direction']:
            raise PreventUpdate
        else:
            filter_data['direction'] = radio_value

    # If return button triggered
    if  dash.callback_context.triggered[0]['prop_id'] == 'map-return-link.n_clicks':
        filter_data['stations'] = None           
        
    return json.dumps(filter_data)
        
# Update details div
@app.callback([Output("date-header", 'children'), Output("filter_output","children"),
               Output('modal-div','children'),
               Output('detail-cards-div','children'),Output('daily-graph','figure'),
               Output('map-div','children'),Output('memb-graph','figure')],
              [Input("filter-meta-div",'children')],
             )
def daily_div_callback(filter_data):
    filter_data = json.loads(filter_data)
    suff = ""
    
    if filter_data['date'] is None:
        raise PreventUpdate
        
    log("daily_div_callback")
    
    ddf = filter_ddf(df,date=filter_data['date'], 
                     stations=filter_data['stations'], 
                     cats=filter_data['cats'], 
                     direction=filter_data['direction'])

        
    trips = False if filter_data['stations'] is None else True
    direction = filter_data['direction']
    date = date_2_str(filter_data['date'])
    
    filter_table = make_filter_table(filter_data)
    data_modal = make_data_modal(ddf, suff=suff)
    detail_cards_div_children=make_detail_cards(ddf,wdf,suff=suff)
    daily_fig = make_daily_fig(ddf,suff=suff)
    map_div = make_map_div(ddf,trips,direction,suff)
    memb_fig = make_memb_fig(ddf,suff=suff)
    
    return [date,filter_table,data_modal,detail_cards_div_children,daily_fig,map_div,memb_fig]


# Update details div2
@app.callback([Output('date-header2','children'), Output("filter_output2","children"), 
               Output('modal-div2','children'),
               Output('detail-cards-div2','children'),Output('daily-graph2','figure'),
               Output('map-div2','children'),Output('memb-graph2','figure')],
              [Input("filter-meta-div2",'children')],
             )
def daily_div_callback2(filter_data):
    filter_data = json.loads(filter_data)
    suff = "2"
    
    if filter_data['date'] is None:
        raise PreventUpdate
        
    log("daily_div_callback2")
    
    ddf = filter_ddf(df,date=filter_data['date'], 
                     stations=filter_data['stations'], 
                     cats=filter_data['cats'], 
                     direction=filter_data['direction'])

        
    trips = False if filter_data['stations'] is None else True
    direction = filter_data['direction']
    date = date_2_str(filter_data['date'])
    
    filter_table = make_filter_table(filter_data)
    data_modal = make_data_modal(ddf, suff=suff)
    detail_cards_div_children=make_detail_cards(ddf,wdf,suff=suff)
    daily_fig = make_daily_fig(ddf,suff=suff)
    map_div = make_map_div(ddf,trips,direction,suff)
    memb_fig = make_memb_fig(ddf,suff=suff)
    return [date,filter_table, data_modal,detail_cards_div_children,daily_fig,map_div,memb_fig]


  
@app.callback(Output('date-modal','is_open'),
               [Input('date-button','n_clicks'),Input('go-button','n_clicks'),
                Input('timeseries-graph','clickData'),Input('timeseries-graph','selectedData')],
                [State('filter-meta-div','children')]
              )
def toggle_date_modal(n_clicks,go_n_clicks,clickData,selectedData,filter_data):
    
    filter_data = json.loads(filter_data)
    if filter_data['date'] is not None:
        raise PreventUpdate

    if dash.callback_context.triggered[0]['prop_id'] == 'date-button.n_clicks':
        return True if n_clicks is not None else False
    if dash.callback_context.triggered[0]['prop_id'] == 'go-button.n_clicks':
        return False
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        return True
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        return True
        
@app.callback(Output('date-modal2','is_open'),
               [Input('date-button2','n_clicks'),Input('go-button2','n_clicks'),
                Input('timeseries-graph','clickData'),Input('timeseries-graph','selectedData')],
               [State('filter-meta-div','children'),State('filter-meta-div2','children')]
              )
def toggle_date_modal2(n_clicks,go_n_clicks,clickData,selectedData,filter_data,filter_data2):
    
    filter_data = json.loads(filter_data)
    if filter_data['date'] is None:
        raise PreventUpdate

    if dash.callback_context.triggered[0]['prop_id'] == 'date-button2.n_clicks':
        return True
    if dash.callback_context.triggered[0]['prop_id'] == 'go-button2.n_clicks':
        return False
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        return True
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        return True 

    
    
@app.callback(Output('data-modal','is_open'),
              [Input('data-button','n_clicks')]
             )
def open_data_modal(n_clicks):
    if n_clicks is not None:
        return True

    
    
@app.callback(Output('data-modal2','is_open'),
              [Input('data-button2','n_clicks')]
             )
def open_data_modal(n_clicks):
    if n_clicks is not None:
        return True


    
    
@app.callback(Output("download-data-button",'href'),
              [Input("data-button",'n_clicks')],
              [State("data-table","data")]
             )
def download_data(n_clicks,data):
    if n_clicks is None:
        raise PreventUpdate
    ddf = pd.DataFrame(data)
    csv_string = ddf.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string





@app.callback(Output("download-data-button2",'href'),
              [Input("data-button2",'n_clicks')],
              [State("data-table2","data")]
             )
def download_data2(n_clicks,data):
    if n_clicks is None:
        raise PreventUpdate
    ddf = pd.DataFrame(data)
    csv_string = ddf.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

        
@app.callback([Output('date-button','className'),Output('date-button2','className')],
              [Input("filter-meta-div",'children'),Input("filter-meta-div2",'children')],
             )
def toggle_date_buttons(filter_data,filter_data2):
    
    filter_data = json.loads(filter_data)
    filter_data2 = json.loads(filter_data2)
    
    if filter_data['date'] is None:
        return ["mr-1","mr-1 d-none"]
    elif filter_data2['date'] is None:
        return ["mr-1 d-none", "mr-1"]
    else:
        return ["d-none","d-none"]
    
    
    

        
        

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=8051)

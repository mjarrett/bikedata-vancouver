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



print(dash.__version__)

external_stylesheets=['/assets/css/bootstrap_custom.min.css','/assets/css/style.css',"https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"]


meta_tags = [{'name':"twitter:card", 'content':"summary_large_image"},
             {'name':"twitter:site", 'content':"@VanBikeShareBot"},
             {'name':"twitter:creator", 'content':"@mikejarrett_"},
             {'name':"twitter:title", 'content':"BikeData Vancouver"},
             {'name':"twitter:description", 'content':"A tool to explore bikeshare usage in Vancouver"},
             {'name':"twitter:image" , 'content':"https://bikedata.mikejarrett.ca/assets/logo.png"},
             {'property':"og:url", 'content':"https://bikedata.mikejarrett.ca"},
             {'property':"og:title", 'content':"BikeData Vancouver"},
             {'property':"og:description", 'content':"A tool to explore bikeshare usage in Vancouver"},
             {'property':"og:image" , 'content':"https://bikedata.mikejarrett.ca/assets/logo.png"},
             {'property':"og:type" , 'content':"website"},
             #             html.Meta(property="og:url", content="https://bikedata.mikejarrett.ca"),
             #             html.Meta(property="og:title", content="A Twitter for My Sister"),
             #             html.Meta(property="og:description", content="In the early days, Twitt"),
             #             html.Meta(property="og:image", content="http://graphics8.nytimes.com/images/2011/12/08/technology/bits-newtwitter/bits-newtwitter-tmagArticle.jpg")
                        ]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets, meta_tags=meta_tags)
server = app.server  #this is needed for wsgi server
app.title = 'BikeData Vancouver'



#app.config['suppress_callback_exceptions'] = True




body = dbc.Container(id="mainContainer",fluid=True,children=[

    lead,
    
    main_div,

    html.Hr(className="my-2"),

    detail_div,


])

app.layout = html.Div([header,body])

#######################################################################################
#
#  CALLBACKS
#
#######################################################################################

# @app.callback(Output('info-collapse','is_open'),
#               [Input('open-info-collapse-btn','n_clicks')],
#               [State('info-collapse','is_open')]
#              )
# def toggle_info_collapse(n_clicks,is_open):
#     if n_clicks:
#         return not is_open
#     else:
#         return is_open



@app.callback(Output('go-button','disabled'),
              [Input('datepicker','start_date')]
             )
def toggle_go_button(start_date):
    log("toggle_go_button",cb=True)

    if start_date is None:
        return True
    else:
        return False

@app.callback(Output('go-button2','disabled'),
              [Input('datepicker2','start_date')]
             )
def toggle_go_button2(start_date):
    log("toggle_go_button2",cb=True)

    if start_date is None:
        return True
    else:
        return False



@app.callback(Output('detail-div-status','children'),
              [Input('go-button','n_clicks'),Input('close-btn','n_clicks')],
             )
def update_detail_status(go_n_clicks,close_n_clicks):
    log("update_detail_status",cb=True)

    if dash.callback_context.triggered[0]['prop_id'] == 'go-button.n_clicks':
        if go_n_clicks is None:
            return "d-none"
        else:
            return ""

    if dash.callback_context.triggered[0]['prop_id'] == 'close-btn.n_clicks':
        if close_n_clicks is None:
            raise PreventUpdate
        return "d-none"




@app.callback(Output('detail-div-status2','children'),
              [Input('go-button2','n_clicks'),Input('close-btn2','n_clicks')],
             )
def update_detail_status2(go_n_clicks,close_n_clicks):
    log("update_detail_status2",cb=True)

    if dash.callback_context.triggered[0]['prop_id'] == 'go-button2.n_clicks':
        if go_n_clicks is None:
            return "d-none"
        else:
            return ""

    if dash.callback_context.triggered[0]['prop_id'] == 'close-btn2.n_clicks':
        if close_n_clicks is None:
            raise PreventUpdate
        return "d-none"


# @app.callback([Output('header-div','width'),Output('header-div2','width')],
#               [Input('detail-div-status','children'), Input('detail-div-status2','children')]
#              )
# def toggle_detail_header_width(status,status2):
#     log("toggle_detail_header_width",cb=True)

#     if status == '' and status2 == '':
#         return [6, 6]
#     else:
#         return [12,12]


@app.callback([Output('header-div','className'), Output('detail-cards-div','className'),
               Output('daily-div','className'), Output('map-div','className'),
               Output('memb-div','className'), Output('explore-div','className'),
               Output('header-div2','className'), Output('detail-cards-div2','className'),
               Output('daily-div2','className'), Output('map-div2','className'),
               Output('memb-div2','className'), Output('explore-div2','className')],
               [Input('detail-div-status','children'), Input('detail-div-status2','children')]
             )
def toggle_div_visibility(status, status2):
    log("toggle_div_visibility",cb=True)

#     if status == 'd-none':
#         date_1_divs = ["d-none"]*6
#     else:
#         date_1_divs = [""]*6

    if status2 == 'd-none':
        date_2_divs = ["d-none"]*6
    else:
        date_2_divs = [""]*6


    return [""]*6 + date_2_divs


@app.callback(Output('timeseries-graph','figure'),
             [Input('filter-meta-div','children'),Input('filter-meta-div2','children')]
             )
def timeseries_callback(filter_data,filter_data2):
    log("timeseries_callback",cb=True)

    filter_data = json.loads(filter_data)
    filter_data2 = json.loads(filter_data2)

    return make_timeseries_fig(filter_data['date'],filter_data2['date'])

@app.callback(Output('datepicker','initial_visible_month'),
              [Input('datepicker','start_date')]
             )
def update_initial_date(date):
    log("update_initial_date",cb=True)
    log(date)
    if date is not None:
        return date
    else:
        return startdate_iso

@app.callback([Output('datepicker','start_date'), Output('datepicker','end_date'),
               Output('datepicker2','start_date'), Output('datepicker2','end_date')],
              [Input('timeseries-graph','clickData'), Input('timeseries-graph','selectedData'),
               Input('timeseries-graph','relayoutData')],
              [State("filter-meta-div",'children')]
             )
def update_datepicker_from_graph(clickData, selectedData, relayoutData,filter_data):
    log("update_datepicker_from_graph",cb=True)


    filter_data = json.loads(filter_data)

#     if filter_data['date'] is not None:
#         raise PreventUpdate


    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        if clickData is None:
            raise PreventUpdate
        date = clickData['points'][0]['x']
        return (date, date, date, date)
    elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        if selectedData is None:
            raise PreventUpdate
        dates = [x['x'] for x in selectedData['points'] ]
        return (dates[0], dates[-1], dates[0], dates[-1])
    elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.relayoutData':
        if relayoutData is None or 'xaxis.range[0]' not in relayoutData.keys():
            raise PreventUpdate
        return (relayoutData['xaxis.range[0]'][:10],relayoutData['xaxis.range[1]'][:10],
                relayoutData['xaxis.range[0]'][:10],relayoutData['xaxis.range[1]'][:10])

    else:
        raise PreventUpdate

@app.callback(Output('datepicker2','initial_visible_month'),
              [Input('datepicker2','start_date')]
             )
def update_initial_date2(date):
    log("update_initial_date",cb=True)
    log(date)
    if date is not None:
        return date
    else:
        return startdate_iso


# @app.callback([Output('datepicker2','start_date'), Output('datepicker2','end_date')],
#               [Input('timeseries-graph','clickData'), Input('timeseries-graph','selectedData')],
#               [State("filter-meta-div2",'children')]
#              )
# def update_datepicker_from_graph2(clickData, selectedData, filter_data):
#     log("update_datepicker_from_graph2",cb=True)

#     if clickData is None and selectedData is None:
#         raise PreventUpdate

#     filter_data = json.loads(filter_data)

#     if filter_data['date'] is not None:
#         raise PreventUpdate


#     if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
#         date = clickData['points'][0]['x']
#         return (date, date)
#     elif dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
#         dates = [x['x'] for x in selectedData['points'] ]
#         return (dates[0], dates[-1])

#     else:
#         raise PreventUpdate




# Keep track of filter
@app.callback(Output("filter-meta-div",'children'),
              [Input('go-button','n_clicks'),
               Input('map-graph','clickData'),
               Input('stations-radio','value'),
               Input('map-return-btn','n_clicks'),
               Input('close-btn','n_clicks')],
              [State("filter-meta-div",'children'),
               State('datepicker','start_date'),
               State('datepicker','end_date'),
               State('checklist-member','value'),
               State('checklist-casual','value')]
             )
def update_filter_meta_div(n_clicks,clickData,radio_value, return_nclicks, close_nclicks,
                           filter_data,
                           start_date,end_date,checklist_member,checklist_casual):

    log("update_filter_meta_div",cb=True)

    filter_data = json.loads(filter_data)

    cat_values = checklist_member + checklist_casual 

    # IF go-button is triggered, update all values
    if  dash.callback_context.triggered[0]['prop_id'] == 'go-button.n_clicks': 
        if n_clicks is None:
            raise PreventUpdate
        date = convert_dates(start_date,end_date)

        filter_data = {'date':date, 'cats':cat_values, 'stations':None, 'direction':'start'}


    # If map #1 is clicked
    if dash.callback_context.triggered[0]['prop_id'] == 'map-graph.clickData':
        if clickData is None:
            raise PreventUpdate
        station = clickData['points'][0]['text'].split('<')[0].strip()
        filter_data['stations'] = [station]


    # If radio1 is clicked
    if  dash.callback_context.triggered[0]['prop_id'] == 'stations-radio.value':
        if radio_value == filter_data['direction']:
            raise PreventUpdate
        else:
            filter_data['direction'] = radio_value

    # If return button triggered
    if  dash.callback_context.triggered[0]['prop_id'] == 'map-return-btn.n_clicks':
        if return_nclicks is None:
            raise PreventUpdate
        filter_data['stations'] = None

    # If close button triggered
    if  dash.callback_context.triggered[0]['prop_id'] == 'close-btn.n_clicks':
        if close_nclicks is None:
            raise PreventUpdate
        filter_data['date'] = None

    return json.dumps(filter_data)


# Keep track of filter2
@app.callback(Output("filter-meta-div2",'children'),
              [Input('go-button2','n_clicks'),
               Input('map-graph2','clickData'),
               Input('stations-radio2','value'),
               Input('map-return-btn2','n_clicks'),
               Input('close-btn2','n_clicks')],
              [State("filter-meta-div2",'children'),
               State('datepicker2','start_date'),
               State('datepicker2','end_date'),
               State('checklist-member2','value'),
               State('checklist-casual2','value')]
             )
def update_filter_meta_div2(n_clicks,clickData,radio_value, return_nclicks, close_nclicks,
                           filter_data,
                           start_date,end_date,checklist_member,checklist_casual):

    log("update_filter_meta_div2",cb=True)
    

    filter_data = json.loads(filter_data)
    cat_values = checklist_member + checklist_casual 

    # IF go-button2 is triggered, update all values
    if  dash.callback_context.triggered[0]['prop_id'] == 'go-button2.n_clicks':
        if n_clicks is None:
            raise PreventUpdate
        date = convert_dates(start_date,end_date)

        filter_data = {'date':date, 'cats':cat_values, 'stations':None, 'direction':'start'}


    # If map #2 is clicked
    if dash.callback_context.triggered[0]['prop_id'] == 'map-graph2.clickData':
        if clickData is None:
            raise PreventUpdate
        station = clickData['points'][0]['text'].split('<')[0].strip()
        filter_data['stations'] = [station]


    # If radio2 is clicked
    if  dash.callback_context.triggered[0]['prop_id'] == 'stations-radio2.value':
        if radio_value == filter_data['direction']:
            raise PreventUpdate
        else:
            filter_data['direction'] = radio_value

    # If return button triggered
    if  dash.callback_context.triggered[0]['prop_id'] == 'map-return-btn2.n_clicks':
        if return_nclicks is None:
            raise PreventUpdate
        filter_data['stations'] = None

    # If close button triggered
    if  dash.callback_context.triggered[0]['prop_id'] == 'close-btn2.n_clicks':
        if close_nclicks is None:
            raise PreventUpdate
        filter_data['date'] = None

    return json.dumps(filter_data)

# Update details div
@app.callback([Output("date-header", 'children'),
               Output('modal-div','children'),
               Output('detail-cards-div','children'),Output('daily-graph','figure'),
               Output('map-div','children'),Output('memb-graph','figure')],
              [Input("filter-meta-div",'children')],
             )
def daily_div_callback(filter_data):
    log("daily_div_callback",cb=True)

    filter_data = json.loads(filter_data)
    suff = ""

    if filter_data['date'] is None:
        raise PreventUpdate

    ddf = filter_ddf(df,filter_data)


    trips = False if filter_data['stations'] is None else True
    direction = filter_data['direction']

    detail_header = make_detail_header(filter_data, suff=suff)
    data_modal = make_data_modal(ddf, filter_data, suff=suff)
    detail_cards_div_children=make_detail_cards(ddf,wdf,suff=suff)
    daily_fig = make_daily_fig(ddf,wdf,suff=suff)
    map_div = make_map_div(ddf,trips,direction,suff)
    memb_fig = make_memb_fig(ddf,suff=suff)

    return [detail_header,data_modal,detail_cards_div_children,daily_fig,map_div,memb_fig]


# Update details div2
@app.callback([Output('date-header2','children'),
               Output('modal-div2','children'),
               Output('detail-cards-div2','children'),Output('daily-graph2','figure'),
               Output('map-div2','children'),Output('memb-graph2','figure')],
              [Input("filter-meta-div2",'children')],
             )
def daily_div_callback2(filter_data):
    log("daily_div_callback2",cb=True)

    filter_data = json.loads(filter_data)
    suff = "2"

    if filter_data['date'] is None:
        raise PreventUpdate


    ddf = filter_ddf(df,filter_data)


    trips = False if filter_data['stations'] is None else True
    direction = filter_data['direction']
    date = date_2_div(filter_data['date'])

    detail_header = make_detail_header(filter_data, suff=suff)
    data_modal = make_data_modal(ddf, filter_data,suff=suff)
    detail_cards_div_children=make_detail_cards(ddf,wdf,suff=suff)
    daily_fig = make_daily_fig(ddf,wdf,suff=suff)
    map_div = make_map_div(ddf,trips,direction,suff)
    memb_fig = make_memb_fig(ddf,suff=suff)
    return [detail_header, data_modal,detail_cards_div_children,daily_fig,map_div,memb_fig]



@app.callback(Output('date-modal','is_open'),
             [Input('date-button','n_clicks'),Input('go-button','n_clicks'),Input("date-update-btn",'n_clicks'),
              Input('timeseries-graph','clickData'),Input('timeseries-graph','selectedData')],
             [State('filter-meta-div','children')]
              )
def toggle_date_modal(n_clicks,go_n_clicks,update_n_clicks,clickData,selectedData,filter_data):
    log("toggle_date_modal",cb=True)

    filter_data = json.loads(filter_data)


    if dash.callback_context.triggered[0]['prop_id'] == 'date-button.n_clicks':
        return True if n_clicks is not None else False
    if dash.callback_context.triggered[0]['prop_id'] == 'go-button.n_clicks':
        return False
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.clickData':
        if filter_data['date'] is not None:
            raise PreventUpdate
        return True
    if dash.callback_context.triggered[0]['prop_id'] == 'timeseries-graph.selectedData':
        if filter_data['date'] is not None:
            raise PreventUpdate
        return True
    if dash.callback_context.triggered[0]['prop_id'] == 'date-update-btn.n_clicks':
        return True


@app.callback(Output('date-modal2','is_open'),
               [Input('date-button2','n_clicks'),Input('go-button2','n_clicks'),Input("date-update-btn2",'n_clicks'),
                Input('timeseries-graph','clickData'),Input('timeseries-graph','selectedData')],
               [State('filter-meta-div','children'),State('filter-meta-div2','children')]
              )
def toggle_date_modal2(n_clicks,go_n_clicks,update_n_clicks,clickData,selectedData,filter_data,filter_data2):
    log("toggle_date_modal2",cb=True)

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
    if dash.callback_context.triggered[0]['prop_id'] == 'date-update-btn2.n_clicks':
        return True



@app.callback(Output('about-modal','is_open'),
              [Input('about-navlink','n_clicks')]
             )
def toggle_about_modal(n_clicks):
    print('toggle_about_modal')
    if n_clicks is None:
        raise PreventUpdate
    return True
            



# Checkbox toggles
@app.callback(Output('checklist-member','value'),
              [Input('checklist-member-header','value')]
             )
def toggle_checkboxes(vals):
    if vals == ['Member']:
        return memtypes_member
    elif vals == []:
        return []

@app.callback(Output('checklist-casual','value'),
              [Input('checklist-casual-header','value')]
             )
def toggle_checkboxes(vals):
    if vals == ['Casual']:
        return memtypes_casual
    elif vals == []:
        return []



@app.callback(Output('checklist-member2','value'),
              [Input('checklist-member-header2','value')]
             )
def toggle_checkboxes(vals):
    if vals == ['Member']:
        return memtypes_member
    elif vals == []:
        return []

@app.callback(Output('checklist-casual2','value'),
              [Input('checklist-casual-header2','value')]
             )
def toggle_checkboxes(vals):
    if vals == ['Casual']:
        return memtypes_casual
    elif vals == []:
        return []





############################################

@app.callback(Output('data-modal','is_open'),
              [Input('data-button','n_clicks')]
             )
def open_data_modal(n_clicks):
    log("open_data_modal",cb=True)

    if n_clicks is not None:
        return True



@app.callback(Output('data-modal2','is_open'),
              [Input('data-button2','n_clicks')]
             )
def open_data_modal2(n_clicks):
    log("open_data_modal2",cb=True)
    if n_clicks is not None:
        return True




@app.callback(Output("download-data-button",'href'),
              [Input("data-button",'n_clicks')],
              [State('filter-meta-div','children')]
             )
def download_data(n_clicks,filter_data):
    log("download_data",cb=True)

    if n_clicks is None:
        raise PreventUpdate

    filter_data = json.loads(filter_data)
    ddf = filter_ddf(df,filter_data)

    if len(ddf) > 100000:
        raise PreventUpdate

    csv_string = ddf.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


@app.callback(Output("download-data-button2",'href'),
              [Input("data-button2",'n_clicks')],
              [State('filter-meta-div','children')]
             )
def download_data2(n_clicks,filter_data):
    log("download_data2",cb=True)

    if n_clicks is None:
        raise PreventUpdate

    filter_data = json.loads(filter_data)
    ddf = filter_ddf(df,filter_data)

    if len(ddf) > 100000:
        raise PreventUpdate

    csv_string = ddf.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


@app.callback([Output('date-button','className'),Output('date-button2','className')],
              [Input("filter-meta-div",'children'),Input("filter-meta-div2",'children')],
             )
def toggle_date_buttons(filter_data,filter_data2):
    log("toggle_date_buttons",cb=True)

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

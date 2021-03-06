# region Import required libraries
# -----------------------------------------------------------------------------------------------
from dash_core_components.Tab import Tab
import copy
import pathlib
import dash
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from dash import no_update
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from datetime import date
import plotly.express as px
import json

#endregion Import

#region Setup runtime variables
# -----------------------------------------------------------------------------------------------
# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
PLOTLY_CHART_CONFIGS = {'displayModeBar': False, 'doubleClickDelay': 1000}

#endregion Setup runtime variables

#region Setup data stuff
# -----------------------------------------------------------------------------------------------
# Set dummy variables
last_updated = "2021-01-19 11:25AM(PST)"
dataload_df = pd.read_csv("data/load_status.csv")
dataload_df["y_value"] = 1
pipelineperf_df = pd.read_csv("data/pipeline_execution_times.csv")

recon_data_df = pd.read_csv("data/recon2.csv", sep=",", header=0)
recon_total_count= len(recon_data_df.index)
recon_passed_count= len(recon_data_df[recon_data_df["overall_status"]=="Pass"].index)
recon_failed_count = len(recon_data_df[recon_data_df["overall_status"]=="Fail"].index)

#endregion Setup data stuff

app = dash.Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
server = app.server



recon_table = dbc.Table.from_dataframe(recon_data_df, striped = True, bordered = True, dark = False)
recon_badges = [dbc.Button(id="button-total", color= "primary", children=["Rules Total",dbc.Badge(recon_total_count, color = "light", className= "ml-3")]),
                dbc.Button(id="button-failed", color= "danger", className="ml-3", children=["Rules Failed",dbc.Badge(recon_failed_count, color = "light", className= "ml-3")]),
                dbc.Button(id="button-passed", color= "success", className="ml-3", children=["Rules Passed",  dbc.Badge(recon_passed_count, color = "light", className= "ml-3")])

                ]

#region General layout for charts
# -----------------------------------------------------------------------------------------------

layout = dict(
    autosize=True,
    # automargin=True,
    margin=dict(l=30, r=30, b=20, t=28),
    hovermode="closest",
    plot_bgcolor="#1a2229",
    paper_bgcolor="#2d353c",
    xaxis = dict(color="#9ba8b4", showgrid=False),
    yaxis = dict(color="#9ba8b4", showgrid=False),
    
    title="Sample Title",
    titlefont=dict(
        family='Open Sans',
        size=18,
        color='white'
    ),
    
    legend = dict(
            x=0.16,
            y=-0.12,
            traceorder="normal",
            font=dict(
                family="Open Sans",
                size=12,
                color="#9ba8b4"
            ),
            bgcolor="#1a2229",
            bordercolor="Black",
            borderwidth=1,
            orientation='h'
        )
)

#endregion General layout for charts

#region Utility functions

# Color Mapper
# -----------------------------------------------------------------------------------------------
def generate_status_colors(row):
    if row["status_code"]==1:
        return "#28a745"
    elif  row["status_code"]==2:
        return "#dc3545"
    elif row["status_code"]==4:
        return "grey"
    else:
        return "white"

# DataLoad Status Graph (LoadStatus Tab)
# -----------------------------------------------------------------------------------------------
def loadStatus_graph():
    dataload_df["color"] = dataload_df.apply(generate_status_colors, axis=1)
    layout_count = copy.deepcopy(layout)
    statusplot = px.bar(dataload_df, x="job_title", y="y_value")
    
    #statusplot.update_layout(layout_count,  yaxis_zeroline=False, yaxis={'visible': False})
    statusplot.update_traces(marker_color = dataload_df["color"])
    statusplot.update_layout(layout_count)
    statusplot.update_layout(
        title = "Job Execution",
        title_x=0.5,
        yaxis={'visible': False},
        titlefont=dict(
            family='Open Sans',
            size=18,
            color = "#ffffff"
        ),
        showlegend = True,
        yaxis_zeroline=False,
        
    )
    # fig = go.Figure(layout=layout_count)
    
    # fig.add_trace(
        
    #     # go.Bar(
    #     #     #name='testing',
    #     #     x=dataload_df["job_title"],
    #     #     y=dataload_df["y_value"],
    #     #     marker_color=dataload_df["color"],
    #     #     orientation='v',
    #     #     showlegend = True,
    #     #     # marker=dict(
    #     #     #     color = '#AC5700'
    #     #     # )
            
    #     # ),    
    # )
    
    # fig.update_layout(
    #     title = "Job Execution",
    #     title_x=0.5,
    #     yaxis={'visible': False},
    #     #yaxis_title="",
    #     titlefont=dict(
    #         family='Open Sans',
    #         size=18,
    #         color = "#ffffff"
    #     ),
    #     showlegend = True,
    #     yaxis_zeroline=False,
        
    # )
    
    return statusplot


def pipelinePerf_graph():
    layout_count = copy.deepcopy(layout)
    perfplot = px.line(pipelineperf_df, x="run_date", y="total_execution_time_mins", color="job_title")
    perfplot.update_layout(layout_count)
    perfplot.update_layout(xaxis=dict(tickformat="%Y-%m-%d", tickmode= 'linear'))
    return perfplot

#endregion Utility functions

#region Creating App Layout
# -----------------------------------------------------------------------------------------------
app.layout = html.Div(
    [
        # dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        
        # Navbar
        # --------------------------------------------------------------------------------
        
        html.Div(
            [
                html.Div(
                    [
                        # html.Div(
                        #     [
                        #         html.Img(
                        #         src=app.get_asset_url("dash-logo.png"),
                        #         id="cepel-logo",
                        #         )
                        #     ], className="one-third column ", id = "cepel-col"
                        # ),
                        html.Div(
                        [
                        html.Div(
                            [
                                html.H3(
                                    "Commercial DataOperations Dashboard",
                                    style={"margin-bottom": "0px"},
                                    className = "white_input"
                                ),
                                html.H5(
                                    "Daily Data Load Monitoring", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="two column",
                    id="title",
                ),
                
                
                html.Div(
                    [
                        #html.Img(src=app.get_asset_url("GitHub-Mark-Light-64px.png"), id = "gh-logo"),
                        
                        # html.A(
                        #     id="gh-link",
                        #     children=["Contact: Commercial Data Team"],
                        #     style={"color": "white", "border": "solid 1px white"},
                        #     href="mailto:datateam@test.com",
                            
                        # )
                        html.P("Last Updated: {0}".format(last_updated),
                                id="last-updated"
                            )
                    ],
                    id="button",
                ), 
            ],
            id="header",
            className="row dark_header",
        )],
    ),
        
        # Tabs
        # --------------------------------------------------------------------------------
        
        html.Div(
            
            [
                html.Div(
                    [
                        dcc.Tabs(
                        [
                            dcc.Tab(label="Load Status", children=[
                                html.Div([
                                    dcc.Graph(id= "loadStatusGraph", figure=loadStatus_graph(),className = "twelve columns", config = PLOTLY_CHART_CONFIGS)
                                ], className="tab_content"),
                                html.Div(id="job_error_modal_div"),

                            ]),

                            dcc.Tab(label="Recon Status", children=[
                                html.Div([
                                            html.H5("Recon Status: " + str(date.today()), className= "mt-1 ml-1"),
                                            #html.Hr(),
                                            # html.Div(recon_badges, className="ml-5 mt-3" ),
                                            # html.Hr(),
                                            dbc.Container(id="badges-cont", children=recon_badges, className="ml-3 mt-0" ),
                                            html.Hr(),
                                            dbc.Container(id="recon_table", children=recon_table,className="p-2 mt-1 ml-3", fluid= True),
                                            html.Div(children=recon_table,id="recon_table_div", className="p-2 mt-3 ml-3"),

                                               ], className="tab_content")

                            ]),
                            dcc.Tab(label="Pipeline Performance", children=[
                                html.Div([
                                    dcc.Graph(figure=pipelinePerf_graph(),className = "twelve columns", config = PLOTLY_CHART_CONFIGS)
                                ], className="tab_content")

                            ]),
                            
                            
                            dcc.Tab(label = "About the App", children = [
                                
                                html.Div([
                                
                                    # html.P("""
                                    #        This dash application allows you to predict medical charges using machine learning alogirthms
                                    #        (Random Forest Regression, SVR and Lasso Regression). You can also:
                                    #        """
                                    #        ),
                                        
                                    dcc.Markdown('''
                                    #### **Predictive Analysis on Medical Charges**
                                    
                                    This dash application allows you to predict medical charges using machine learning algorithms
                                    (Random Forest Regression, SVR and Lasso Regression). Developed with Python and all codes published
                                    on GitHub. Feel free to review and download repository. You can:
                                    * calculate body mass index,
                                    * predict medical costs billed by health insurance
                                    * review data analysis
                                    * explore data distribution.
                                    
                                    ##### **Inspiration**
                                    
                                    I have inspired one of my old Kaggle notebook. You can find details about different ML pipelines and hyperparameters tuning:  
                                    https://www.kaggle.com/tolgahancepel/medical-costs-regression-hypertuning-eda
                                    
                                    ##### **Dataset**
                                    https://www.kaggle.com/mirichoi0218/insurance
                                    
                                    ##### **GitHub**
                                    https://github.com/tolgahancepel/medical-charges-prediction
                                    '''
                                    )    
                                    
                                ], className = "tab_content"),

                            ]),
                        ]              
                        ),
                    
                    ], className = "tabs_pretty_container twelve columns")

            ],className = "row flex-display-closertop",
            
        ),

        #region First Row
        # --------------------------------------------------------------------------------
        
        # html.Div(
        #     [
        #         html.Div(
        #             [
        #                 # Header of BMI
        #                 html.Div([
        #                     html.H6("Body Mass Index Calculator", className = "bmi_card_header_text"),
        #                     html.H4("Your BMI: 0", id = "bmi_value", className = "bmi_card_value_text")
        #                 ], className = "bmi_card_header"),
                        
        #                 # Height Input
                        
        #                 html.P("Height (cm)", className="control_label white_input"),
        #                 html.Div(
        #                     dcc.Input(
        #                         className = "bmi_input",
        #                     id="input_height", type="number", placeholder="Enter your height",
        #                     min=0, max=250),
        #                  className="dcc_control",                            
        #                  ),
                        
        #                 # Weight Input
                        
        #                 html.P("Weight (kg)", className="control_label white_input"),
        #                 html.Div(
        #                     dcc.Input(
        #                         className = "bmi_input",
        #                         id="input_weight", type="number", placeholder="Enter your weight",
        #                         min=0, max=250),
        #                  className="dcc_control ",                            
        #                  ),
                        
        #                 # Age Input
                        
        #                 html.P("Age", className="control_label white_input"),
        #                 html.Div(
        #                     dcc.Input(
        #                         className = "bmi_input",
        #                         id="input_age", type="number", placeholder="Enter your age",
        #                         min=2, max=122),
        #                  className="dcc_control ",                            
        #                  ),
                            
        #                 # Calculate and Reset Buttons
                        
        #                 html.Div(
        #                     [
        #                         html.Button('Reset', id='btn_reset', n_clicks=0, className= "btn_reset"),
        #                         html.Button('Calculate', id='btn_calculate', n_clicks=0, className = "btn_calculate"),
        #                     ],
        #                  className="dcc_control", id = "bmi-buttons"                         
        #                  ),

        #             ],
        #             className="pretty_container four columns",
        #             id="cross-filter-options",
        #         ),
                                
        #         # Prediction
        #         # --------------------------------------------------------------------------------
                
        #         html.Div(
        #             [
                        
                        
        #                 html.Div(
        #                     [
        #                         # Header of Prediction Card
        #                         html.Div([
        #                             html.H5("Prediction", className = "bmi_card_header_text"),
        #                         ], className = "prediction_card_header"),
                                
                                
        #                         html.Div([
                                    
        #                             # Age
                                                                               
        #                             html.Div(
        #                                 [
        #                                     html.P("Age", className="control_label white_input"),
        #                                     dcc.Input(
        #                                         id="predict_age", type="number", placeholder="Enter your age",
        #                                         min=2, max=122),
                                                
        #                                 ], className = "three columns predict_input",
        #                             ),
                                    
        #                             # BMI
                                    
        #                             html.Div(
        #                                 [
        #                                     html.P("BMI", className="control_label white_input"),
        #                                     dcc.Input(
        #                                         id="predict_bmi", type="number", placeholder="Enter your BMI",
        #                                         min=2, max=122),
                                                
        #                                 ], className = "three columns predict_input",
        #                             ),
                                    
                                    
        #                             # Children
                                    
        #                             html.Div(
        #                                 [
        #                                     html.P("Children", className="control_label white_input"),
        #                                     dcc.Dropdown(
        #                                         id='predict_children',
        #                                         options=[
        #                                             {'label': '0', 'value': '0'},
        #                                             {'label': '1', 'value': '1'},
        #                                             {'label': '2', 'value': '2'},
        #                                             {'label': '3', 'value': '3'},
        #                                             {'label': '4', 'value': '4'},
        #                                             {'label': '5', 'value': '5'},
        #                                             {'label': '6', 'value': '6'},
        #                                             {'label': '7', 'value': '7'},
        #                                             {'label': '8', 'value': '8'},
        #                                             {'label': '9', 'value': '9'},
        #                                             {'label': '10', 'value': '10'},
        #                                         ], value='0'
        #                                     ),
                                                
        #                                 ], className = "three columns predict-input-last",
        #                             ),
        #                         ], className = "row"),
                                
        #                         html.Div([
                                    
        #                             # Region
                                    
        #                             html.Div(
        #                                     [
        #                                           html.P("Region", className="control_label white_input"),
        #                                           dcc.Dropdown(
        #                                               id='predict_region',
        #                                               options=[
        #                                                   {'label': 'Southwest', 'value': 'southwest'},
        #                                                   {'label': 'Southeast', 'value': 'southeast'},
        #                                                   {'label': 'Northwest', 'value': 'northwest'},
        #                                                   {'label': 'Northeast', 'value': 'northeast'}
        #                                               ],
        #                                               value="southwest"
        #                                           ),
                                                
        #                                     ], className = "three columns predict_input",
        #                                 ),
                                    
        #                                # Sex
                                        
        #                                 html.Div(
        #                                     [
        #                                           dcc.RadioItems(
        #                                             id = "predict_sex",
        #                                             options=[
        #                                                 {"label": "Male ", "value": "male"},
        #                                                 {"label": "Female ", "value": "female"},
        #                                             ],
        #                                             value="male",
        #                                             labelStyle={"display": "inline-block"},
        #                                             className="dcc_control",
        #                                         ),
                                                
        #                                     ], className = "three columns predict_input", style = {"margin-top": "5%"}
        #                                 ),
                                                                    
        #                             html.Div(
        #                                     [
        #                                           dcc.Checklist(
        #                                             id = "predict_smoker",
        #                                             options=[
        #                                                 {'label': 'Smoker', 'value': 1},
        #                                             ],
        #                                             labelStyle={'display': 'inline-block'}
        #                                         )  
                                                
        #                                     ], className = "three columns predict-input-last", style = {"margin-top": "5%"}
        #                                 ),
                                    
        #                         ], className = "row"),
                                
        #                         html.Div(
        #                             [
                                        
        #                                 html.Button('Predict', id='btn_predict', n_clicks=0, className = "twelve columns btn-predict"),
        #                             ],
        #                             className="row container-display", style = {"padding-top": "20px"}                           
        #                          ),
                                
        #                     ],
        #                     className="pretty_container"
        #                 ),
                        
        #                 # Prediction results
                        
        #                 html.Div(
        #                     [
        #                         html.Div(
        #                             [html.H6(id="rf_result", children = "$0000.00", className = "predict_result"), html.P("Random Forest")],
        #                             id="wells",
        #                             className="mini_container",
        #                         ),
        #                         html.Div(
        #                             [html.H6(id="svr_result", children = "$0000.00", className = "predict_result"), html.P("SVM")],
        #                             id="gas",
        #                             className="mini_container",
        #                         ),
        #                         html.Div(
        #                             [html.H6(id="lasso_result", children = "$0000.00", className = "predict_result"), html.P("Lasso")],
        #                             id="oil",
        #                             className="mini_container",
        #                         ),
        #                     ],
        #                     id="info-container",
        #                     className="row container-display",
        #                 ),
        #             ],
        #             id="right-column",
        #             className="eight columns",
        #         ),
        #     ],
        #     className="row flex-display",
        # )
        #endregion First Row
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)

#endregion Creating App Layout

#region App Callbacks
# --------------------------------------------------------------------------------------------

# Failed data load bar click callback
@app.callback(
    Output("job_error_modal_div", "children"),
    [Input("loadStatusGraph", "clickData")],  
)
def show_job_error_modal(clickData):
    clicked_bar_index = clickData.get("points")[0].get("pointIndex")
    clicked_filtered_df = dataload_df.iloc[[clicked_bar_index]]
    job_error_text = clicked_filtered_df["additional_info"].values[0]
    job_status_desc = clicked_filtered_df["status_desc"].values[0]
    modal_body_content = [ html.Label(job_error_text,style={"color": "black"}),
                        html.A("Cloudwatch Link", href="https://www.google.com"),
                           
                        ]  
    modal_output = dbc.Modal(
            [
                dbc.ModalHeader("{0}!".format(job_status_desc), style={"color": "red"}),
                dbc.ModalBody(modal_body_content),
            ],
            id="modal",
            is_open=True,
            centered=True,
        )
    return modal_output


# Recon Table/Tab callback
@app.callback(Output("recon_table", "children"), 
                Input("button-total", "n_clicks"),
                Input("button-failed", "n_clicks"),
                Input("button-passed", "n_clicks")
)
def filter_table(total_click_count, failed_click_count, passed_click_count):
    clicked_button_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if not(total_click_count or failed_click_count or passed_click_count):
        df_filtered = recon_data_df
    elif "button-failed" in clicked_button_id:
        df_filtered = recon_data_df[recon_data_df["overall_status"]=="Fail"]
    elif "button-passed" in clicked_button_id:
        df_filtered = recon_data_df[recon_data_df["overall_status"]=="Pass"]
    else:
        df_filtered = recon_data_df
    return dbc.Table.from_dataframe(df_filtered, striped = True, bordered = True, dark = True)

#endregion App Callbacks

# Main
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True, dev_tools_ui=False, port=8059)

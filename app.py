import dash
from dash import Dash, dash_table, dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash_extensions.enrich import html, dcc, Input, Output, State, ctx
from dash import callback
import threading
import webcolors
import random
import os
import json
from dash.exceptions import PreventUpdate
import shutil
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = 'simple_white'
import io

# Assuming df is your DataFrame
df = pd.read_csv('taar_phewas_consgenesymbols_minimal_harmonized.tsv', sep='\t') # Uncomment and use if your data is in a CSV file
b_vis={"padding": "1rem 1rem", "margin-top": "2rem", "margin-bottom": "1rem", 'display':'inline-block'}
b_invis={"padding": "1rem 1rem", "margin-top": "2rem", "margin-bottom": "1rem", 'display':'none'}

app = dash.Dash(__name__)

app.layout = html.Div(children=[dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i, "type": "numeric" if i in ['p', 'beta','se','z','sample_size'] else "text"} for i in df.columns],
    data=df.to_dict('records'),
    editable=True,
    filter_action="native", # Enable filtering
    sort_action="native", # Enable sorting
    sort_mode="multi", # Allow sorting by multiple columns
    column_selectable="single", # Allow selecting columns
   # row_selectable="multi", # Allow selecting multiple rows
   # row_deletable=True, # Allow deleting rows
    selected_columns=[], # Initially selected columns
  #  selected_rows=[], # Initially selected rows
    page_action="native", # Enable pagination
    page_current= 0, # Initial page
    page_size= 15, # Rows per page
),
html.Button("Replot data", id="plot_data", style=b_vis),
dcc.Download(id="download"),
html.Button("Download Data", id="download-button", style=b_vis),
html.Div(id='plot_container', children=[]),

])


@app.callback(
    Output('plot_container', 'children'),
    Input('plot_data','n_clicks'),
    State('table', "derived_virtual_data"),
    State('table', "derived_virtual_selected_rows"),
    prevent_initial_call=False
)
def update_bar_plot(n_clicks, rows, derived_virtual_selected_rows):
    # Convert the rows back into a DataFrame
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    dff=df if rows is None else pd.DataFrame(rows)
    
    # Calculate the counts of different values in the "Subcategory" field

    counts=pd.DataFrame(dff['subcategory'].value_counts()).reset_index().rename(columns={'index':'subcategory','subcategory':'association_count'})
    counts_genes=pd.DataFrame(dff['gs'].value_counts()).reset_index().rename(columns={'index':'gene','gs':'association_count'})
    min_p_indices = dff.groupby('trait')['p'].idxmin()
    filtered_data = dff.loc[min_p_indices]
    filtered_data = dff[['trait','is_gene_trait','p','beta','rsid', 'gs']]
    filtered_data=filtered_data.sort_values('p')
    # Create a bar plot
    return [
        dcc.Graph(
            id="gwas_subcats_plot",
            figure={
                "data": [
                    {
                        "x": counts['subcategory'],
                        "y": counts['association_count'],
                        "type": "bar",
                        "marker": {"color": 'skyblue'},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": 'Association count'}
                    },
                    "height": 300,
                    "margin": {"t": 20, "l": 10, "r": 10},
                },
            },
        ),
        dcc.Graph(
            id="gene_subcats_plot",
            figure={
                "data": [
                    {
                        "x": counts_genes['gene'],
                        "y": counts_genes['association_count'],
                        "type": "bar",
                        "marker": {"color": 'skyblue'},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": 'Association count'}
                    },
                    "height": 300,
                    "margin": {"t": 20, "l": 10, "r": 10},
                },
            },
        ),
        dcc.Markdown('Traits arranged by max association strength'),
        dash_table.DataTable(
            id='trait_ranking_table',
            columns=[{"name": i, "id": i, "type": "numeric" if i in ['p', 'beta','se','z','sample_size'] else "text"} for i in filtered_data.columns],
            data=filtered_data.to_dict('records'),
            editable=True,
            filter_action="native", # Enable filtering
            sort_action="native", # Enable sorting
            sort_mode="multi", # Allow sorting by multiple columns
            column_selectable="single", # Allow selecting columns
        # row_selectable="multi", # Allow selecting multiple rows
        # row_deletable=True, # Allow deleting rows
            selected_columns=[], # Initially selected columns
        #  selected_rows=[], # Initially selected rows
            page_action="native", # Enable pagination
            page_current= 0, # Initial page
            page_size= 15, # Rows per page
            active_cell={"row": 0, "column": 0}
        )        
        ]

@app.callback(
    Output("download", "data"),
    Input("download-button", "n_clicks"),
    State("table", "derived_virtual_data"),
    prevent_intiial_call=True,
)
def generate_and_download_file(n_clicks, rows):
    if n_clicks is None:
        raise PreventUpdate
    else:

        # Assuming rows is a list of dictionaries representing the selected rows
        # Convert it back to a DataFrame
        df_selected = pd.DataFrame(rows)

        # Generate a CSV file from the DataFrame
        #csv_string = df_selected.to_csv(index=False, encoding='utf-8')
        #csv_string = "data:text/csv;charset=utf-8," + csv_string

        return dcc.send_data_frame(df_selected.to_csv, "associations.csv")


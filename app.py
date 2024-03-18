import dash
import dash_table
import pandas as pd

# Assuming df is your DataFrame
df = pd.read_csv('taar_phewas_consgenesymbols_minimal_harmonized.tsv', sep='\t') # Uncomment and use if your data is in a CSV file

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
    filter_action="native", # Enable filtering
    sort_action="native", # Enable sorting
    sort_mode="multi", # Allow sorting by multiple columns
    column_selectable="single", # Allow selecting columns
    row_selectable="multi", # Allow selecting multiple rows
    row_deletable=True, # Allow deleting rows
    selected_columns=[], # Initially selected columns
    selected_rows=[], # Initially selected rows
    page_action="native", # Enable pagination
    page_current= 0, # Initial page
    page_size= 10, # Rows per page
)

if __name__ == '__main__':
    app.run_server(debug=True)
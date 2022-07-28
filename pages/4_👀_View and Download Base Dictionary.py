import streamlit as st
import pandas as pd
import functions as f

st.set_page_config(page_title="LIS Translation Tool", page_icon='🗃️', 
                layout="wide",
                initial_sidebar_state="expanded",
     menu_items={
         'About': "# This is the LIS file translation tool."
     })


st.title('🗃️LIS File Translation Tool🧰⚙️')
st.header('View and Download Base Dictionary')

base_dict = f.load_json('data/base_dict.json')
base_dict = pd.DataFrame.from_dict(base_dict, orient='index').reset_index(drop = False)
base_dict.rename(columns={'index': 'LIS Test Name', 'AssayName': 'Assay Name'}, inplace = True)

with st.expander('Click here to see the interactivity of the table'):
    st.markdown("""
    ### Interactivity
Dataframes displayed as interactive tables with st.dataframe have the following interactive features:
- **Column sorting**: sort columns by clicking on their headers.
- **Column resizing**: resize columns by dragging and dropping column header borders.
- **Table (height, width) resizing**: resize tables by dragging and dropping the bottom right corner of tables.
- **Search**: search through data by clicking a table, using hotkeys (⌘ Cmd + F or Ctrl + F) to bring up the search bar, and using the search bar to filter data.
- **Copy to clipboard**: select one or multiple cells, copy them to clipboard, and paste them into your favorite spreadsheet software.
""")

st.dataframe(base_dict, width=1000)

df_xlsx = f.dfs_to_excel([base_dict], ['Base Dictionary'])
st.download_button(label='📥 Download Base Dictionary 📥',
                                data=df_xlsx,
                                file_name='Base Dictionary.xlsx')

st.markdown("""
---
### Base Dictionary Update Request
Please fill out this google form if you find out a LIS test should be included in the base dictionary or there are wrong translations for some tests in the base dictionary.

*We will update the base dictionary as soon as possible.*
- [Google form](https://forms.gle/RedT4n5e1PZvAweXA)
- [View submitted results](https://docs.google.com/spreadsheets/d/1yewrCftjO5iJzg5ib7wTrII80ayT4zHxek_D9D4KIEw/edit?usp=sharing)

""")


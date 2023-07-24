from http.cookies import BaseCookie
from operator import index
from statistics import median
import pandas as pd
import streamlit as st
from io import BytesIO
import json
import difflib

## Functions

# load the json file
@st.cache_resource
def load_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


# Read all sheets in one excel
@st.cache_resource
def load_all_sheets(excel_file):
    df_dict = pd.read_excel(excel_file, sheet_name=None)
    return df_dict


# Function to save all dataframes to one single excel
def dfs_to_excel(df_list, sheet_list): 
    output = BytesIO()
    writer = pd.ExcelWriter(output,engine='xlsxwriter')   
    for dataframe, sheet in zip(df_list, sheet_list):
        dataframe.to_excel(writer, sheet_name=sheet, startrow=0 , startcol=0, index=False)   
        for column in dataframe:
            column_length = max(dataframe[column].astype(str).map(len).mean()+10, len(column))
            col_idx = dataframe.columns.get_loc(column)
            writer.sheets[sheet].set_column(col_idx, col_idx, column_length)

    writer.save()
    processed_data = output.getvalue()
    return processed_data


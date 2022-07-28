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
@st.cache
def load_json(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


# Read all sheets in one excel
@st.cache
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



















##### NOT BEEN USED #####
# Function for getting matched tests
def get_close_match(panelDict: dict, tests: list, cutoff: float):
    """
    Take all unique test names in the raw file and find the most similar test name in the
    panel dictionary and then translate it into corresponding roche assay names.
    
    @input
    panelDef: a dictionary for panel definition(contains historical LIS tranlation data)
    test: a list of unique LIS test names which need translation
    cutoff: a float number which determines the word similarity cutoff for the get_close_match function. 
    
    @return
    match_result: a dictionary of suggested translations for the new test data
    """
    match_result = {}

    for test in tests:
        matches = difflib.get_close_matches(test, panelDict.keys(), n=1, cutoff = cutoff)
        if len(matches) > 0:
            best_match = matches[0]
            score = difflib.SequenceMatcher(None, test, best_match).ratio()
            match_result[test] = {'Include':1, 
                                    'Material':panelDict[best_match]['Material'],
                                    'SimilarTest': best_match,
                                    'AssayName': panelDict[best_match]['AssayName'],
                                    'ConfidenceScore': score}
        else:
            match_result[test] = {'Include':1, 
                                    'Material': '',
                                    'SimilarTest': 'No similar test found',
                                    'AssayName': '',
                                    'ConfidenceScore': 0}
        st.session_state.match_result = match_result

        return match_result


# Function of getting panel definition dataframe
def dict_to_df(match_result):
    """
    Turn the match_result from get_close_match into a dataframe

    @input
    match_result: a dictionary

    @output
    panel_df: a dataframe
     
    """
    panel_df = pd.DataFrame()

    for key, value in match_result.items():
        tmp = pd.DataFrame([[key, value['Include'], value['Material'], 
                            value['SimilarTest'], value['AssayName'], 
                            value['ConfidenceScore']]])
        panel_df = pd.concat([panel_df, tmp])
        st.session_state.panel_df = panel_df

    panel_df.columns = ['Test Name', 'Include', 'Material', 'Similar Test',
                        'Assay Name', 'Confidence Score']
    st.session_state.panel_df = panel_df
    return panel_df


# Functio of adding new columns for results to raw file
def append_to_raw(raw: pd.DataFrame, LIS_column_name: str, match_result:dict):
    """
    Append the data in match_result as new columns to the raw file
    New columns are Similat Test, Assay Name, Confidence Score

    @input
    raw: A DataFrame selected by user which contains the LIS test names. 
         The column of LIS test names cannot have missing values
    LIS_column_name: A string which is the column name of the LIS test name in the raw file
    match_result:  A dictionary contains the test names and similar test and roche assay name

    @return
    result_df: A DataFrame contains the raw file and three new columns
    
    """
    result_df = raw.copy()
    result_df.dropna(subset = LIS_column_name, inplace = True)
    st.session_state.result_df = result_df

    for index, row in result_df.iterrows():
        result_df.loc[index,'Similar Test'] = match_result[row[LIS_column_name]]['SimilarTest']
        result_df.loc[index, 'Assay Name'] = match_result[row[LIS_column_name]]['AssayName']
        result_df.loc[index, 'Confidence Score'] = round(match_result[row[LIS_column_name]]['ConfidenceScore'],3)
        st.session_state.result_df = result_df
        
    return result_df



# Function for saving the user-defined dictionary
@st.cache
def create_panelDef(panel_file):
    """
        Translate the input file to a dictionary.
        input panel_file: the panel definition excel file user upload or the base dicitonary
        return panelDict: a dictionary
    """
    panelDict = {}
    for i in range(len(panel_file)):
        row = panel_file.iloc[i]
        test_name = row['Test Name']
        include = row['Include']
        material = row['Material']
        tempList = row[3:]
        roche_names = []
        for name in tempList:
            if pd.notna(name):
                roche_names.append(name)
        panelDict[test_name] = {'Include': include, 'Material': material, 'Result_Test': roche_names}
    return panelDict



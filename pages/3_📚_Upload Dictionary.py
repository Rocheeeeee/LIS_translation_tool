from http.cookies import BaseCookie
from operator import index
import pandas as pd
import streamlit as st
import json
from io import BytesIO
import functions as f
import difflib

st.set_page_config(page_title="LIS Translation Tool", page_icon='🗃️', 
                layout="wide",
                initial_sidebar_state="expanded",
     menu_items={
         'About': "# This is the LIS file translation tool."
     })

st.title('🗃️LIS File Translation Tool🧰⚙️')
st.header('Upload your dictionary')

with st.expander('Click here to view the instructions'):
    st.markdown("""
    #### Instructions
1. Select your dictionary file. **ONLY EXCEL files are accepted**
2. Select the sheet that contains your dictionary.
3. Click the **Upload Dictionary** button to upload.
    """)

# create an empty dictionary for saving the user-defined dictionary
panelDict = {}
if 'panelDict' not in st.session_state:
    st.session_state.panelDict = panelDict

# User upload their own dictionary
st.info("**Please make sure the dictionary follows the format below, or the upload will not succeed.**")
st.markdown("""
| Test Name | Include | Material | Assay Name |
| ----------- | ----------- | ----------- | ----------- |
| BMP | 1 | SERUM | CO27,GLU7,CA7,CREP7,BUN7|
| Insulin | 1 | SERUM | INSUL |

> - The 4 columns above are mandatory and the names need to be exactly the same as the example. However, it's fine that your dictionary contains other columns like *Similar Test*, *Confidence Score*. 
> - If a test name corresponds to multiple assays, please type all the assay names in **ONE cell** and separate the assays with commas(,)
""")

st.markdown('---')
uploaded_dict = st.file_uploader("Select the excel file. Please make sure the file follows the format above.", type=['xlsx'])
if uploaded_dict is not None:
    own_dict = pd.ExcelFile(uploaded_dict)
    all_dict_sheets = ['(Not Selected Yet)'] + own_dict.sheet_names

    ## User select the sheet name that needs translation
    selected_dict_sheet = st.selectbox('Select the sheet name:', all_dict_sheets, key='dictionary_selection')

    ## to read just one sheet to dataframe and display the sheet:
    if selected_dict_sheet != '(Not Selected Yet)':
        try:
            own_dict_sheet = pd.read_excel(own_dict, sheet_name = selected_dict_sheet)
            # own_dict_sheet['Result_Test'].fillna('NA', inplace=True)
            st.session_state.own_dict_sheet = own_dict_sheet
            with st.expander("Click here to check the dictionary you uploaded"):
                st.write("Number of observations: " + str(len(own_dict_sheet)))
                st.write(own_dict_sheet)
                st.caption("<NA> means there is no value in the cell")

            # If the button is clicked, app will save the dictionary
            if st.button('📤 Upload Dictionary'):
                newDict = {}
                for i in range(len(own_dict_sheet)):
                    row = own_dict_sheet.iloc[i]
                    test_name = row['Test Name']
                    include = row['Include']
                    material = row['Material']
                    assay = row['Assay Name']
                    newDict[test_name] = {'Include': include, 'Material': material, 'AssayName': assay}
                st.session_state.newDict = newDict
                st.success('🎉 Dicitonary uploaded successfully')

        except KeyError:
            st.warning('🚨 Your dictionary does not follow the naming conventions. Column names should be **Test Name**, **Include**, **Material**, **Assay Name**.')




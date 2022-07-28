from lib2to3.pgen2.parse import ParseError
import streamlit as st
import pandas as pd
import numpy as np
import functions as f
from datetime import datetime
from dateutil import parser

st.set_page_config(page_title="LIS Translation Tool", page_icon='🗃️', 
                layout="wide",
                initial_sidebar_state="expanded",
     menu_items={
         'About': "# This is the LIS file translation tool."
     })


st.title('🗃️LIS File Translation Tool🧰⚙️')
st.header('Timestamps Formatting')
st.subheader('Fill in the missing timestamps and format the date and time')
with st.expander('Click here to view the instructions'):
    st.markdown("""
    #### Instructions
1. Select the file you want to translate. **ONLY EXCEL files are accpeted**
2. Select the sheet that contains the raw data.
3. Select the columns for *patient ID*
4. Select the timestamp columns which you want to format.
5. Select the delimiter that the raw file is using to separate data and time in the columns
6. Preview the formatted data below. If the result is correct, click **Download Current Result** to download the formatted file.
    """)

## Section: Upload the excel file
st.header('Upload Raw Data')
uploaded_file = st.file_uploader("Select the file which needs translation:", type=['xlsx'])
st.info('Please only upload excel file.')



if uploaded_file is not None:
    # get the file name of raw data
    st.session_state.file_name = uploaded_file.name
    LIS_file = pd.ExcelFile(uploaded_file)
    all_sheets = ['(Not Selected Yet)'] + LIS_file.sheet_names
    
    ## User select the sheet name that needs translation
    selected_sheet = st.selectbox('Select the sheet with raw data:', all_sheets)

    ## to read just one sheet to dataframe and display the sheet:
    if selected_sheet != '(Not Selected Yet)':
        # Read the data in as string
        raw_data = pd.read_excel(LIS_file, sheet_name = selected_sheet, dtype=str)

        with st.expander("Click here to check the file you uploaded"):
            st.write("Number of observations: " + str(len(raw_data)))
            st.write("Here are the first 10 rows of raw data")
            st.write(raw_data.head(10))
            st.caption("<NA> means there is no value in the cell")

        all_columns = ['(Not Selected Yet)'] + list(raw_data.columns)
        ID_column = st.selectbox("Select the column for patient ID", all_columns)

        if ID_column != '(Not Selected Yet)':
            st.session_state.ID_column = ID_column
            if raw_data[ID_column].isna().sum() > 0:
                st.warning('WARNING: There are missing patient ID in this data.  Rows without patient ID will be dropped durning translation.')
            st.session_state.raw_data = raw_data


            st.markdown('---')
            # select the presentation of timestamps: date and time are in the same or separate columns
            presentation = st.selectbox('Are the date and time displayed in one or separate columns for the timestamps in your data?',
                        ('Please Select', 'One Column', 'Separate Columns'))
            filled_data = raw_data.copy()
            st.session_state.filled_data = filled_data

            if presentation == 'One Column':
                # select the timestamp columns
                datetime_columns = st.multiselect("Please select the columns of timestamps that need formatting.\
                                            Multiple selections are allowed", raw_data.columns)
                st.info('A row will be dropped if there are any missing timestamps in the columns you selected')
                st.session_state.datetime_columns = datetime_columns
                
                if len(datetime_columns) > 0:
                    # fill in missing dates
                    datetime_columns = st.session_state.datetime_columns
                    ID_column = st.session_state.ID_column
                    filled_data = st.session_state.filled_data
                    filled_data[datetime_columns] = filled_data.groupby(ID_column)[datetime_columns].ffill().bfill()

                    # drop the rows which there are missing dates
                    filled_data.dropna(subset = datetime_columns, how='any', inplace = True)
                    st.session_state.filled_data = filled_data

                    # select delimiter
                    delimiter = st.selectbox('Select the delimiter that separates date and time in timestamp columns',
                                    ('Please Select', 'Space', '@', '_', ';'))
                    if delimiter == 'Space':
                        delimiter = ' '
                    st.info('Please make sure all the timestamp columns you selected are using the same delimiter.')
                    
                    if delimiter != 'Please Select':
                        for col in datetime_columns:
                            #replace special delimiter to a space
                            filled_data[col] = filled_data[col].apply(lambda d: d.replace(delimiter, ' '))
                            st.session_state.filled_data = filled_data

                            try:
                                #parse the dates into standardized format
                                if delimiter == '@': # for the special format "OCT 13,2020@12:23"
                                    # replace the , so it can be parsed correctly by the parser
                                    filled_data[col] = filled_data[col].apply(lambda d: d.replace(',', ' '))
                                    filled_data[col] = filled_data[col].apply(lambda dt: parser.parse(dt))

                                else:
                                    # handle the timestamp value error(0000/00/00 00:00:00), replace with NaT
                                    filled_data[col] = pd.to_datetime(filled_data[col], errors='coerce')

                                # drop the rows with missing timestamps or value error(0000/00/00 00:00:00)
                                filled_data = filled_data.dropna(subset = [col])

                                # separate the timestamp into Date and Time columns
                                date_col = col + '__Date'
                                time_col = col + '__Time'
                                filled_data[date_col] = filled_data[col].apply(lambda dt: dt.strftime('%m%d%Y'))
                                filled_data[time_col] = filled_data[col].apply(lambda dt: str(dt.time()))

                            except parser.ParserError:
                                 st.error('🚨ERROR: Please make sure you select the correct delimiter for column '+ col)
                    

            elif presentation == 'Separate Columns':
                # Select the date columns
                date_columns = st.multiselect('Please select the columns of test dates.  \
                    Multiple selections are allowed', raw_data.columns)
                st.session_state.date_columns = date_columns
                time_columns = st.multiselect('Please select the columns of test times.  \
                    Multiple selections are allowed', raw_data.columns)
                st.session_state.time_columns = time_columns

                if (len(date_columns) > 0) and (len(time_columns) > 0):
                    # fill in missing dates
                    date_columns = st.session_state.date_columns
                    time_columns = st.session_state.time_columns
                    ID_column = st.session_state.ID_column
                    filled_data = st.session_state.filled_data
                    
                    filled_data[date_columns] = filled_data.groupby(ID_column)[date_columns].ffill().bfill()
                    filled_data[time_columns] = filled_data.groupby(ID_column)[time_columns].ffill().bfill()

                    # drop the rows which there are missing dates
                    filled_data.dropna(subset=time_columns, how='any', inplace = True)
                    st.session_state.filled_data = filled_data
                    
                    # formate date columns
                    for col in date_columns:
                        try:
                            filled_data[col] = filled_data[col].apply(lambda d: parser.parse(d).strftime('%m%d%Y'))
                            st.session_state.filled_data = filled_data
                        except parser.ParserError:
                            st.error("🚨ERROR: There is unknown format of date that cannot be parsed by the program.")

                    # format the time columns:
                    for col in time_columns:
                        try:
                            filled_data[col] = filled_data[col].apply(lambda t: str(parser.parse(t).time()))
                            st.session_state.filled_data = filled_data
                        except parser.ParserError:
                            st.error("🚨ERROR: There is unknown format of time that cannot be parsed by the program.")


            # calculate turn around time


            st.markdown('---')
            st.markdown('#### Preview the formatted data')
            st.markdown("""
            - **The program would use the current datetime to make up for any missing parts of the timestamp**
            - For example, in the parsing of '12/20' , which got parsed as 2022-12-20 as 2022 is the current year
            - If a time is not supplied then 00:00:00 is used
            """)
            st.write("There are " + str(len(raw_data) - len(filled_data)) + " rows be dropped because of missing timestamps")
            st.write(filled_data)
            st.caption('Please scroll to the right to see the newly created columns')
            st.caption("<NA> means there is no value in the cell")


            # Formatting the new file name
            today = datetime.today().strftime("%Y%m%d%H%M")+'_'
            new_file_name = 'Time Formatted_' + today + st.session_state.file_name 

            # output the excel file and let the user download
            sheet_list = ['Time Formatted Data', 'Raw Data']
            df_xlsx = f.dfs_to_excel([filled_data, raw_data], sheet_list)
            st.download_button(label='📥 Download Current Result 📥',
                                            data=df_xlsx,
                                            file_name= new_file_name)

import string
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import functions as f


st.set_page_config(page_title="LIS Translation Tool", page_icon='🗃️', 
                layout="wide",
                initial_sidebar_state="expanded",
     menu_items={
         'About': "# This is the LIS file translation tool."
     })

st.title('🗃️LIS File Translation Tool🧰⚙️')
st.header('📊Summary Report')
st.info('Please standardize the timestamps and translate the LIS test names before using this tool.')

with st.expander('Click here to view the instructions'):
    st.markdown("""
    #### Instructions
1. Select the raw data which timestamps are standardized by this application. **ONLY EXCEL files are accpeted**
2. Select the sheet name which contains the formatted timestamp data.
3. Select the column name for *Patient ID*, *Assay Names*, *Test Arrival Date*, *Test Arrival Time* respectively.
4. Click **Generate Aggregated Report** button to view the result.
5. For each visualization plot, click the three dot icon on the upper-right coner to download the plot.
6. Click **Download Summary Report** to download the aggregated tables as an Excel file.
    """)


# function
def format_date(date, time):
    if type(date) == 'str':
        date = datetime.strptime(date, '%Y-%m-%d')
    if type(time) == 'str':
        time = datetime.strptime(time, '%H:%M:%S')
    date1 = date.date()
    weekday = date1.strftime('%A')
    hour = datetime.strptime(time, '%H:%M:%S').hour
    return (str(date1), weekday, hour)



## Upload the excel file
st.header('Upload Graph Data Worksheet')
uploaded_file = st.file_uploader("Select the excel file:", type=['xlsx'])


if uploaded_file is not None:
    # get the file name of raw data
    st.session_state.file_name = uploaded_file.name

    # read in all the sheets in the uploaded excel file
    dict_of_df = f.load_all_sheets(uploaded_file)
    st.session_state.dict_of_df = dict_of_df
    all_sheets = ['(Not Selected Yet)'] + list(dict_of_df.keys())

    # LIS_file = pd.ExcelFile(uploaded_file)
    # all_sheets = ['(Not Selected Yet)'] + LIS_file.sheet_names
    
    ## User select the sheet name for graph data worksheet
    selected_sheet = st.selectbox('Select the sheet of Graph Data Workseet:', all_sheets)
    st.info("If there is no graph data worksheet in the file you uploaded, please translate the file first.")

    ## to read just one sheet to dataframe and display the sheet:
    if selected_sheet != '(Not Selected Yet)':
        # Read the data in as string
        raw_data = dict_of_df[selected_sheet]
        # raw_data = pd.read_excel(LIS_file, sheet_name = selected_sheet, dtype=str)

        with st.expander("Click here to check the file you uploaded"):
            st.write("Number of observations: " + str(len(raw_data)))
            st.write("Here are the first 10 rows of raw data")
            st.write(raw_data.head(10))
            st.caption("<NA> means there is no value in the cell")

        all_columns = ['(Not Selected Yet)'] + list(raw_data.columns)

        ID_col = st.selectbox('Select the column for patient ID', all_columns)

        assay_col = st.selectbox('Select the column for translated assay names', all_columns)

        st.subheader("The following two columns should be generated by **Timestamps Formatting**")
        arrival_date_col = st.selectbox('Select the column for tests received date', all_columns)
        st.info("This column should only contain **DATE** and be in the format of **yyyy-mm-dd**")

        arrival_time_col = st.selectbox('Select the column for tests received time', all_columns)
        st.info("This column should only contain **TIME** and in the format of **HH:MM:SS**")


        if st.button("📊 Generate Summary Report"):
            if '(Not Selected Yet)' in (ID_col, assay_col, arrival_date_col, arrival_time_col):
                st.warning('WARNING: You missed selecting one of the columns above')
            else:
                try:
                    df = raw_data.copy()
                    df['Arrival_Date'], df['Arrival_Weekday'], df['Arrival_Hour'] = zip(*df.apply(lambda t: format_date(t[arrival_date_col], t[arrival_time_col]), axis=1))

                    # count the number of unique IDs per day/hour
                    sum_per_date_hour = df.groupby(['Arrival_Date', 'Arrival_Hour']).agg({ID_col: 'nunique', assay_col: 'count'}).reset_index()
                    sum_per_date = df.groupby(['Arrival_Date']).agg({ID_col: 'nunique', assay_col: 'count'}).reset_index()
                    sum_per_week = df.groupby(['Arrival_Weekday']).agg({ID_col: 'nunique', assay_col: 'count'}).reset_index()

                    sum_per_date_hour.rename(columns={ID_col: 'Number of samples', assay_col:'Number of assays'}, inplace = True)
                    sum_per_date.rename(columns={ID_col: 'Number of samples', assay_col:'Number of assays'}, inplace = True)
                    sum_per_week.rename(columns={ID_col: 'Number of samples', assay_col:'Number of assays'}, inplace = True)

                    

                    # Visualizations
                    chart1 = alt.Chart(sum_per_date_hour, title='Number of samples arrived in each hour each day').mark_rect().encode(
                        alt.X('Arrival_Hour:O', title='Hour of day'),
                        alt.Y('Arrival_Date:O', title='Date'),
                        alt.Color('Number of samples', title='Number of samples'),
                        tooltip = ['Arrival_Date', 'Arrival_Hour', 'Number of samples']
                    ).interactive()


                    chart1_assay = alt.Chart(sum_per_date_hour, title='Number of assays arrived in each hour each day').mark_rect().encode(
                        alt.X('Arrival_Hour:O', title='Hour of day'),
                        alt.Y('Arrival_Date:O', title='Date'),
                        alt.Color('Number of assays', title='Number of assays', scale = alt.Scale(scheme='orangered')),
                        tooltip = ['Arrival_Date', 'Arrival_Hour', 'Number of assays']
                    ).interactive()


                    chart2 = alt.Chart(sum_per_date, title='Number of samples arrived in each date'
                    ).mark_bar().encode(
                            alt.X('Number of samples:Q', title='Count'),
                            alt.Y("Arrival_Date:O", title='Date'),
                            tooltip = ['Arrival_Date', 'Number of samples']
                    ).interactive()

                    chart2_assay = alt.Chart(sum_per_date, title='Number of assays arrived in each date'
                    ).mark_bar().encode(
                            alt.X('Number of assays:Q', title='Count'),
                            alt.Y("Arrival_Date:O", title='Date'),
                            tooltip = ['Arrival_Date', 'Number of assays']
                    ).interactive()



                    chart3 = alt.Chart(sum_per_week, title='Number of samples arrived on each day'
                    ).mark_bar().encode(
                            alt.Y('Arrival_Weekday:O', title='Day of Week', sort=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']),
                            alt.X('Number of samples', title='Count'),
                            tooltip = ['Arrival_Weekday', 'Number of samples']
                    ).interactive()

                    chart3_assay = alt.Chart(sum_per_week, title='Number of assays arrived on each day'
                    ).mark_bar().encode(
                            alt.Y('Arrival_Weekday:O', title='Day of Week', sort=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']),
                            alt.X('Number of assays', title='Count'),
                            tooltip = ['Arrival_Weekday', 'Number of assays']
                    ).interactive()


                    # Present the summary report
                    st.header("Aggregated results for tests arrival time")

                    number_of_assays = str(sum_per_date['Number of assays'].sum())
                    number_of_samples = str(sum_per_date['Number of samples'].sum())
                    start_date = str(sum_per_date['Arrival_Date'].iloc[0])
                    end_date = str(sum_per_date['Arrival_Date'].iloc[-1])

                    st.subheader("There were total "  + number_of_samples + " samples and " + number_of_assays + " assays arrived between " + start_date + ' and ' + end_date)
                    
                    tab1, tab2, tab3 = st.tabs(['Aggregated by arrival date and hour', 'Aggregated by arrival date', 'Aggregated by arrival day of week'])
                    with tab1:
                        col11, col12, col13 = st.columns([1,3,3])
                        col11.dataframe(sum_per_date_hour, width=800)
                        col12.write(chart1)
                        col13.write(chart1_assay)
                        col12.caption('White square means there were no tests arrived in that hour.')

                    with tab2:
                        col21, col22, col23 = st.columns(3)
                        col21.dataframe(sum_per_date, width=800)
                        col22.write(chart2)
                        col23.write(chart2_assay)

                    with tab3:
                        col31, col32, col33 = st.columns(3)
                        sum_per_week['Arrival_Weekday'] = pd.Categorical(sum_per_week['Arrival_Weekday'], 
                                categories=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday'],
                                ordered=True)
                        sum_per_week = sum_per_week.sort_values('Arrival_Weekday', ignore_index = True)
                        col31.dataframe(sum_per_week, width=800)
                        col32.write(chart3)
                        col33.write(chart3_assay)


                    # Download summary report
                    st.warning("The result file is still generating, please wait until the download button show up...")
                    # Formatting the new file name
                    new_file_name = 'Summary for_' + st.session_state.file_name
                    
                    dict_of_df = st.session_state.dict_of_df
                    # output the excel file and let the user download
                    sheet_name_list = ['Aggregated by date and time', 'Aggregated by date', 'Aggregated by day of week',
                                'Formatted Data'] + list(dict_of_df.keys())
                    df_list = [sum_per_date_hour, sum_per_date, sum_per_week, raw_data] + list(dict_of_df.values())
                    df_xlsx = f.dfs_to_excel(df_list, sheet_name_list)
                    st.download_button(label='📥 Download Summary Report 📥',
                                                    data=df_xlsx,
                                                    file_name= new_file_name)
                                                    
                    st.success("🎉 File successfully generated. Please click on the download button to download.")

                except AttributeError:
                    st.error("ERROR: ")
                except ValueError:
                    st.error('ERROR: Your timestamps are not standardized. Please visit the **Timestamps Formatting** page to standardize the file before using this function.')


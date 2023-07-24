import string
import streamlit as st
import pandas as pd
import altair as alt
from altair import datum
from datetime import datetime, timedelta
import functions as f
import numpy as np


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
1. Select the data which timestamps are standardized and test names are translated by this application. **ONLY EXCEL files are accpeted**
2. Select the sheet name of **Graph Data Worksheet**.
3. Follow the prompt and select corresponding columns respectively.
4. Click **Generate Summary Reports** button to view the result.
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

    
    ## User select the sheet name for graph data worksheet
    st.subheader("Select the Graph Data Worksheet")
    selected_sheet = st.selectbox(' ', all_sheets)
    st.info("If there is no graph data worksheet in the file you uploaded, please translate the file first.")

    ## to read just one sheet to dataframe and display the sheet:
    if selected_sheet != '(Not Selected Yet)':
        # Read the data in as string
        raw_data = dict_of_df[selected_sheet]

        with st.expander("Click here to check the file you uploaded"):
            st.write("Number of observations: " + str(len(raw_data)))
            st.write("Here are the first 10 rows of raw data")
            st.write(raw_data.head(10))
            st.caption("<NA> means there is no value in the cell")

        all_columns = ['(Not Selected Yet)'] + list(raw_data.columns)
        st.subheader('Select the column for patient ID')
        ID_col = st.selectbox('Patient ID', all_columns)

        st.subheader('Select the column for test priority')
        priority_col = st.selectbox("Priority", all_columns)

        if priority_col != '(Not Selected Yet)':
            all_priority = ['(Not Selected Yet)'] + list(raw_data[priority_col].unique())
            st.subheader("Select the specific priority level you want to view the TAT")
            selected_priority = st.selectbox('Priority Level', all_priority)

        st.subheader("This column is the assay names translated by the **LIS Translation**")
        assay_col = st.selectbox('Select the column for translated assay names', all_columns)

        st.subheader("The following columns should be generated by **Timestamps Formatting**")
        arrival_date_col = st.selectbox('Select the column for tests received date', all_columns)
        st.info("This column should only contain **RECEIPT DATE** and be in the format of **yyyy-mm-dd**")

        arrival_time_col = st.selectbox('Select the column for tests received time', all_columns)
        st.info("This column should only contain **RECEIPT TIME** and in the format of **HH:MM:SS**")

        complete_date_col = st.selectbox('Select the column for tests completed date', all_columns)
        st.info("This column should only contain **COMPLETION DATE** and be in the format of **yyyy-mm-dd**")

        complete_time_col = st.selectbox('Select the column for tests completed time', all_columns)
        st.info("This column should only contain **COMPLETION TIME** and in the format of **HH:MM:SS**")

        if assay_col != '(Not Selected Yet)':
            st.subheader("Select the specific assays that you want to view their TAT")
            assays = raw_data[assay_col].unique()
            # tests the SWC mostly want to look into: BUN and TNT-STAT
            mostly_want_assays = ['BUN', 'BUN5P', 'BUN7', 'TNT-STAT', 'TNT-STAT8']
            # check if the data contains any of those
            defaults = [value for value in mostly_want_assays if value in assays]
            selected_assay = st.multiselect("The default assays are BUN and TAT-STAT", assays, default = defaults) 
            st.info('We suggest that do not select more than 5 assays at one time, or the display of histograms will be hard to read.')

# create a bar chart for a selected date. And generate a 5 column for only that date as well as a 5 column that covered all of the data
        # if arrival_date_col != '(Not Selected Yet)':
        #     start_date = min(raw_data[arrival_date_col])
        #     end_date = max(raw_data[arrival_date_col])
        #     st.date_input('Select the specific date that you want to view the TAT', value = start_date, min_value=start_date, max_value=end_date)

        if st.button("📊 Generate Summary Reports"):
            if '(Not Selected Yet)' in (ID_col, assay_col, priority_col, arrival_date_col, arrival_time_col):
                st.warning('WARNING: You missed selecting one of the columns above')
            else:
                try:
                    raw_data[ID_col] = raw_data[ID_col].astype(str) 
                    df = raw_data.copy()
                    df['Arrival_Date'], df['Arrival_Weekday'], df['Arrival_Hour'] = zip(*df.apply(lambda t: format_date(t[arrival_date_col], t[arrival_time_col]), axis=1))

                    # count the number of unique IDs and assays per day/hour
                    sum_per_date_hour = df.groupby(['Arrival_Date', 'Arrival_Hour']).agg({ID_col: 'nunique', assay_col: 'count'}).reset_index()
                    sum_per_date = df.groupby(['Arrival_Date']).agg({ID_col: 'nunique', assay_col: 'count'}).reset_index()
                    sum_per_week = df.groupby(['Arrival_Weekday']).agg({ID_col: 'nunique', assay_col: 'count'}).reset_index()

                    sum_per_date_hour.rename(columns={ID_col: 'Number of samples', assay_col:'Number of assays'}, inplace = True)
                    sum_per_date.rename(columns={ID_col: 'Number of samples', assay_col:'Number of assays'}, inplace = True)
                    sum_per_week.rename(columns={ID_col: 'Number of samples', assay_col:'Number of assays'}, inplace = True)

                # get the peak day
                    sample_peak_date = sum_per_date.iloc[sum_per_date['Number of samples'].idxmax()]['Arrival_Date']
                    assay_peak_date = sum_per_date.iloc[sum_per_date['Number of assays'].idxmax()]['Arrival_Date']


                # Visualizations for test receipt time
                    # Heat map for number of samples arrived at each time
                    chart1 = alt.Chart(sum_per_date_hour, title='Number of samples arrived in each hour each day').mark_rect().encode(
                        alt.X('Arrival_Hour:O', title='Hour of day'),
                        alt.Y('Arrival_Date:O', title='Date'),
                        alt.Color('Number of samples', title='Number of samples'),
                        tooltip = ['Arrival_Date', 'Arrival_Hour', 'Number of samples']
                    ).interactive()
                    # Heat map for number of assays arrived at each time
                    chart1_assay = alt.Chart(sum_per_date_hour, title='Number of assays arrived in each hour each day').mark_rect().encode(
                        alt.X('Arrival_Hour:O', title='Hour of day'),
                        alt.Y('Arrival_Date:O', title='Date'),
                        alt.Color('Number of assays', title='Number of assays', scale = alt.Scale(scheme='orangered')),
                        tooltip = ['Arrival_Date', 'Arrival_Hour', 'Number of assays']
                    ).interactive()
                    # bar chart for number of samples arrived at each day
                    chart2 = alt.Chart(sum_per_date, title='Number of samples arrived in each date'
                    ).mark_bar().encode(
                            alt.X('Number of samples:Q', title='Count'),
                            alt.Y("Arrival_Date:O", title='Date'),
                            color = alt.Color(value='#0B41CD'),
                            tooltip = ['Arrival_Date', 'Number of samples']
                    ).interactive()
                    # bar chart for number of assays arrived at each day
                    chart2_assay = alt.Chart(sum_per_date, title='Number of assays arrived in each date'
                    ).mark_bar().encode(
                            alt.X('Number of assays:Q', title='Count'),
                            alt.Y("Arrival_Date:O", title='Date'),
                            color = alt.Color(value='#1482FA'),
                            tooltip = ['Arrival_Date', 'Number of assays']
                    ).interactive()
                    # bar chart for number of samples arrvied at each day of week
                    chart3 = alt.Chart(sum_per_week, title='Number of samples arrived on each day'
                    ).mark_bar().encode(
                            alt.Y('Arrival_Weekday:O', title='Day of Week', sort=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']),
                            alt.X('Number of samples', title='Count'),
                            color = alt.Color(value='#0B41CD'),
                            tooltip = ['Arrival_Weekday', 'Number of samples']
                    ).interactive()
                    # bar chart for number of assays arrived at each day of week
                    chart3_assay = alt.Chart(sum_per_week, title='Number of assays arrived on each day'
                    ).mark_bar().encode(
                            alt.Y('Arrival_Weekday:O', title='Day of Week', sort=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']),
                            alt.X('Number of assays', title='Count'),
                            color = alt.Color(value='#1482FA'),
                            tooltip = ['Arrival_Weekday', 'Number of assays']
                    ).interactive()

                # Line chart for Peak date
                    peak_sample_line = alt.Chart(sum_per_date_hour[sum_per_date_hour['Arrival_Date']==sample_peak_date], title='Number of samples arrived in each hour on the peak day'
                    ).mark_line().encode(
                        alt.X('Arrival_Hour:O', title='Hour'),
                        alt.Y('Number of samples', title='Count'),
                        color = alt.Color(value='#0B41CD'),
                        tooltip = ['Arrival_Hour', 'Number of samples']
                    ).interactive()

                    peak_assay_line = alt.Chart(sum_per_date_hour[sum_per_date_hour['Arrival_Date']==assay_peak_date], title='Number of assays arrived in each hour on the peak day'
                    ).mark_line().encode(
                        alt.X('Arrival_Hour:O', title='Hour'),
                        alt.Y('Number of assays', title='Count'),
                        color = alt.Color(value='#1482FA'),
                        tooltip = ['Arrival_Hour', 'Number of assays']
                    ).interactive()


                # Calculate test turn around time
                    tat_df = raw_data.copy()
                    # combine date and time into one timestamp
                    tat_df['Arrival Datetime'] = pd.to_datetime(tat_df[arrival_date_col].apply(lambda d: d.strftime('%Y-%m-%d')) +' '+ tat_df[arrival_time_col])
                    tat_df['Complete Datetime'] = pd.to_datetime(tat_df[complete_date_col].apply(lambda d: d.strftime('%Y-%m-%d')) +' '+ tat_df[complete_time_col])
                    # calculate TAT
                    tat_df['TAT'] = tat_df['Complete Datetime'] - tat_df['Arrival Datetime'] 
                    tat_df['TAT_minutes'] = tat_df['TAT'].apply(lambda delta: delta.total_seconds()/60) #turn around time in  
                    tat_df['TAT'] = tat_df['TAT'].apply(lambda delta: str(delta)) #TAT in string

                    # need a df for test TAT and a df for assay TAT
                    # tat_df are for test TAT
                    # assay_tat_df are for assay tat
                    assay_tat_df = tat_df.copy()
                    tat_df.drop([assay_col], axis = 1, inplace = True)
                    tat_df.drop_duplicates(inplace=True)

                # slide bar for user to select threshold TAT
                    slider = alt.binding_range(min = 10, max = 600, step=10, name='Threshold:')
                    threshold_selector = alt.selection_point(name='threshold_selector', fields=['Threshold'], bind=slider, _init_ = {'Threshold':120})
                # histogram of test TAT
                    TAT_hist = alt.Chart(tat_df, title='Distribution of test TAT by test priority').mark_bar().encode(
                        alt.X('TAT_minutes', bin=alt.Bin(maxbins=30), title='Turn around time (minutes)'),
                        alt.Y('count()', title='Distinct count '),
                        color = alt.Color(priority_col,scale = alt.Scale(scheme='tableau20')),
                        tooltip = [priority_col, 'count()']
                    ) 
                # cumulative percentage of test TAT
                    TAT_line = alt.Chart(tat_df).transform_window(
                        cumulative_count = 'count()',
                        sort = [{'field': 'TAT_minutes'}]
                    ).transform_joinaggregate(
                        total_count = 'count()'
                    ).transform_calculate(
                        cumulative_percentage = "datum.cumulative_count / datum.total_count * 100"
                    ).mark_line(color='#E74C3C').encode(
                        alt.X('TAT_minutes'),
                        alt.Y('cumulative_percentage:Q', title = 'Cumulative percentage(%)')
                    )
                # Layered the two charts
                    TAT_layered = alt.layer(TAT_hist, TAT_line).resolve_scale(
                                y = 'independent'
                        ).transform_filter(
                            datum.TAT_minutes <= threshold_selector.Threshold
                        ).add_selection(
                            threshold_selector
                        ).properties(width=700, height=500
                        ).interactive()



                # Histogram for specific priority 
                    # filter the dataframe by the user selected priority
                    tat_df_pri = tat_df[tat_df[priority_col]==selected_priority]
                    #histogram of TAT for selected priority
                    TAT_hist_pri = alt.Chart(tat_df_pri, title='Distribution of TAT for '+selected_priority).mark_bar().encode(
                        alt.X('TAT_minutes', bin=alt.Bin(maxbins=30), title='Turn around time (minutes)'),
                        alt.Y('count()', title='Distinct count'),
                        color = alt.Color(value='#0B41CD'),
                        tooltip = [priority_col, 'count()']
                    ) 
                # cumulative percentage of test TAT for specific priority
                    TAT_line_pri = alt.Chart(tat_df_pri).transform_window(
                        cumulative_count = 'count()',
                        sort = [{'field': 'TAT_minutes'}]
                    ).transform_joinaggregate(
                        total_count = 'count()'
                    ).transform_calculate(
                        cumulative_percentage = "datum.cumulative_count / datum.total_count * 100"
                    ).mark_line(color='#E74C3C').encode(
                        alt.X('TAT_minutes'),
                        alt.Y('cumulative_percentage:Q', title = 'Cumulative percentage(%)')
                    )
                # Layered the two charts for specific priority
                    TAT_layered_pri = alt.layer(TAT_hist_pri, TAT_line_pri).resolve_scale(
                            y = 'independent'
                        ).transform_filter(
                            datum.TAT_minutes <= threshold_selector.Threshold
                        ).add_selection(
                            threshold_selector
                        ).properties(width=700, height=500
                        ).interactive()


                # Present the summary report
                    st.header("Summary report")

                    number_of_assays = str(sum_per_date['Number of assays'].sum())
                    number_of_samples = str(sum_per_date['Number of samples'].sum())
                    start_date = str(sum_per_date['Arrival_Date'].iloc[0])
                    end_date = str(sum_per_date['Arrival_Date'].iloc[-1])

                    st.subheader("There were total "  + number_of_samples + " samples and " + number_of_assays + " assays arrived between " + start_date + ' and ' + end_date)
                    st.write('Select the tabs below to view each section.')
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Aggregated by arrival date and hour', 'Aggregated by arrival date', 'Aggregated by arrival day of week', 'TAT for all tests', 'TAT for selected assays'])
                    st.markdown('---')
                    with tab1:
                        col11, col12, col13 = st.columns([1,3,3])
                        col11.dataframe(sum_per_date_hour, width=800)
                        col12.write(chart1)
                        col12.write("The date with most number of sample arrived is " + str(sample_peak_date))
                        col12.write(peak_sample_line)

                        col13.write(chart1_assay)
                        col13.write('The date with most number of assays arrived is ' + str(assay_peak_date))
                        col13.write(peak_assay_line)
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

                    # TAT of all priorities and all tests, and user selected priority
                    with tab4:
                        col41, col42 = st.columns(2)
                        col41.write(TAT_layered)
                        col42.write(TAT_layered_pri)

                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Mean TAT", str(round(tat_df['TAT_minutes'].mean(),2)) +" min")
                        col2.metric("Median TAT", str(round(tat_df['TAT_minutes'].median(),2)) +" min")
                        col3.metric("Min TAT", str(tat_df['TAT_minutes'].min())+" min")
                        col4.metric("Max TAT", str(tat_df['TAT_minutes'].max())+" min")


                    # TAT of user selected assays
                    with tab5:
                        assay_tat_df = assay_tat_df[assay_tat_df[assay_col].isin(selected_assay)]
                        assay_TAT_hist = alt.Chart(assay_tat_df, title='Distribution of assay TAT by test priority'
                        ).mark_bar().encode(
                            alt.X('TAT_minutes', bin=alt.Bin(maxbins=30), title='Turn around time (minutes)'),
                            alt.Y('count()', title='Distinct count of assays'),
                            color = alt.Color(priority_col,scale = alt.Scale(scheme='tableau20')),
                            column = assay_col,
                            tooltip = [priority_col, 'count()']
                        ).transform_filter(
                            datum.TAT_minutes <= threshold_selector.Threshold
                        ).add_selection(
                            threshold_selector
                        ).properties(width='container', height=500
                        ).interactive()

                        assay_TAT_line = alt.Chart(assay_tat_df, title = 'Cumulative percentage(%)'
                        ).transform_window(
                            cumulative_count = 'count()',
                            sort = [{'field': 'TAT_minutes'}]
                        ).transform_joinaggregate(
                            total_count = 'count()'
                        ).transform_calculate(
                            cumulative_percentage = "datum.cumulative_count / datum.total_count * 100"
                        ).mark_line(color='#E74C3C').encode(
                            alt.X('TAT_minutes', title = 'Turn around time in minutes'),
                            alt.Y('cumulative_percentage:Q', title = 'Cumulative percentage(%)'),
                            column = assay_col,
                            tooltip = ['TAT_minutes']
                        ).transform_filter(
                            datum.TAT_minutes <= threshold_selector.Threshold
                        ).add_selection(
                            threshold_selector
                        ).properties(width='container', height=500
                        ).interactive()
                        st.write(assay_TAT_hist)
                        st.write(assay_TAT_line)

                    # Download summary report
                    st.warning("The result file is still generating, please wait until the download button show up...")
                    # Formatting the new file name
                    new_file_name = 'Summary for_' + st.session_state.file_name
                    dict_of_df = st.session_state.dict_of_df
                    # output the excel file and let the user download
                    tat_df = tat_df.drop(["Arrival Datetime", "Complete Datetime"], axis = 1)
                    sheet_name_list = ['Aggregated by date and time', 'Aggregated by date', 'Aggregated by day of week',
                                'Turn around time'] + list(dict_of_df.keys())
                    df_list = [sum_per_date_hour, sum_per_date, sum_per_week, tat_df] + list(dict_of_df.values())
                    df_xlsx = f.dfs_to_excel(df_list, sheet_name_list)
                    st.download_button(label='📥 Download Summary Report 📥',
                                                    data=df_xlsx,
                                                    file_name= new_file_name)
                                                    
                    st.success("🎉 File successfully generated. Please click on the download button to download.")


                except ValueError:
                    st.error('ERROR: Your timestamps do not match the designated format. Please visit the **Timestamps Formatting** page to standardize the file before using this function.')

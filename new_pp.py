import pandas as pd
import numpy as np
import json
import mysql.connector
import plotly.express as px
import requests
import streamlit as st

# Connect to MySQL and fetch data based on selected option
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Data23Wrangl#",
    database="phonepe_db"
)
cursor = connection.cursor(buffered=True)

# Streamlit app
st.set_page_config(layout="wide")
st.title('PhonePe Pulse Data Visualization')

# Selection option
option = st.radio('**Select your option**', ('All India', 'State wise', 'Top Ten categories'), horizontal=True)

if option == 'All India':
    
    # Select tab
    tab1, tab2 = st.tabs(['Transaction','User'])

    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            tr_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022', '2023'), key='tr_yr')
        with col2:
            tr_qtr = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='tr_qtr')
        with col3:
            tr_typ = st.selectbox('**Select Transaction type**', ('Recharge & bill payments', 'Peer-to-peer payments',
                                                                  'Merchant payments', 'Financial Services', 'Others'),
                                  key='tr_typ')

        # Transaction data query
        cursor.execute(
            f"SELECT DISTINCT state, transaction_amount, transaction_count FROM aggregated_transaction WHERE year = '{tr_yr}' AND quarter = '{tr_qtr}' AND transaction_type = '{tr_typ}';")
        
        result = cursor.fetchall()

        if result:
            df_result = pd.DataFrame(result, columns=['State', 'Transaction_amount', 'Transaction_count'])
            df_result['Transaction_amount'] = df_result['Transaction_amount'].astype(float)
            df_result['Transaction_count'] = df_result['Transaction_count'].astype(int)

            # Dictionary for state name replacements
            state_replacements = {
                'andaman-&-nicobar-islands': 'Andaman and Nicobar Islands','andhra-pradesh': 'Andhra Pradesh','arunachal-pradesh': 'Arunachal Pradesh',
                'assam': 'Assam','bihar': 'Bihar','chandigarh': 'Chandigarh','chhattisgarh': 'Chhattisgarh','dadra-and-nagar-haveli': 'Dadra and Nagar Haveli',
                'daman-and-diu': 'Daman and Diu','delhi': 'Delhi',f'goa': 'Goa','gujarat': 'Gujarat','haryana': 'Haryana','himachal-pradesh': 'Himachal Pradesh',
                'jammu-&-kashmir': 'Jammu & Kashmir','jharkhand': 'Jharkhand','karnataka': 'Karnataka','kerala': 'Kerala','ladakh': 'Ladakh','lakshadweep': 'Lakshadweep',
                'madhya-pradesh': 'Madhya Pradesh','maharashtra': 'Maharashtra','manipur': 'Manipur','meghalaya': 'Meghalaya','mizoram': 'Mizoram','nagaland': 'Nagaland',
                'odisha': 'Odisha','puducherry': 'Puducherry','punjab': 'Punjab','rajasthan': 'Rajasthan','sikkim': 'Sikkim','tamil-nadu': 'Tamil Nadu','telangana': 'Telangana',
                'tripura': 'Tripura','uttar-pradesh': 'Uttar Pradesh','uttarakhand': 'Uttarakhand','west-bengal': 'West Bengal'
            }

            # Replace the names in the 'State' column
            df_result['State'] = df_result['State'].replace(state_replacements)

            # Load GeoJSON data for India's states from a different URL
            india_states_geojson_url = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'

            fig = px.choropleth(
                data_frame=df_result,
                geojson=india_states_geojson_url,
                locations='State',
                featureidkey='properties.ST_NM',
                color='Transaction_amount',
                hover_name='State',
                hover_data={'Transaction_amount': True, 'State': False, 'Transaction_count': True},  # Show Value in hover
                color_continuous_scale='Viridis',  # Choose a color scale
            )

            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(title_text='All India Transaction Amount and Transaction Count')
            # fig.show()
            # Display the choropleth map using Streamlit
            st.plotly_chart(fig)

            # Total Transaction Amount & Average transaction amount table query
            cursor.execute(f""" select year, SUM(transaction_amount) AS Total_amount, AVG(transaction_amount) AS Average_amount 
                           FROM aggregated_transaction 
                           GROUP BY year 
                           ORDER BY year ASC;""")
            result = cursor.fetchall()

            df_result_ta = pd.DataFrame(result, columns=['Year', 'Total_amount', 'Average_amount'])

            # Area plot to show total & average amount over years
            fig_trend = px.area(
                df_result_ta,
                x='Year',
                y=['Total_amount', 'Average_amount'],
                labels={'value': 'Amount', 'variable': 'Type', 'Year': 'Year'},
                title='Overall Transaction Amount and Average Amount Trend (2018-2023)',
                template='plotly_white',
                color_discrete_sequence=['rgba(55, 128, 191, 0.7)', 'rgba(255, 153, 51, 0.7)'],
                width=800,
                height=400
            )

            # Display the area chart in Streamlit
            st.plotly_chart(fig_trend)

            # Total Transaction count & Average transaction count table query
            cursor.execute(
                f"SELECT year, SUM(Transaction_count) AS Total_count, AVG(Transaction_count) AS Average_count FROM aggregated_transaction GROUP BY Year ORDER BY YEAR ASC;")
            result = cursor.fetchall()

            df_result_tc = pd.DataFrame(result, columns=['Year','Total_count', 'Average_count'])
            
            # Convert 'Year' to datetime if it's stored as a string
            df_result_tc['Year'] = pd.to_datetime(df_result_tc['Year'], format='%Y')
            
            # Area plot to show total & average amount over years
            fig_trend = px.area(
                df_result_tc,
                x='Year',
                y=['Total_count', 'Average_count'],
                labels={'value': 'Count', 'variable': 'Type', 'Year': 'Year'},
                title='Overall Transaction Count and Average Count Trend (2018-2023)',
                template='plotly_white',
                color_discrete_sequence=['rgba(55, 128, 191, 0.7)', 'rgba(255, 153, 51, 0.7)'],
                width=800,
                height=400
            )

            # Display the area chart in Streamlit
            st.plotly_chart(fig_trend)
                
    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            u_yr = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022','2023'),key='u_yr')
        
        with col2:
            u_qtr = st.selectbox('**Select Quarter**', ('1','2','3','4'),key='u_qtr')
        
        with col3:
            u_typ = st.selectbox('**Select User Brand**', ('Xiaomi', 'Samsung', 'Vivo', 'Oppo', 'OnePlus', 'Realme', 'Apple',
        'Motorola', 'Lenovo', 'Huawei', 'Others', 'Tecno', 'Gionee',
        'Infinix', 'Asus', 'Micromax', 'HMD Global', 'Lava', 'COOLPAD',
        'Lyf'),key='u_typ')

        # User count bar chart query
        cursor.execute(
            f"SELECT DISTINCT state, user_count FROM aggregated_user WHERE year = '{u_yr}' AND quarter = '{u_qtr}' AND user_brand = '{u_typ}';")
        result = cursor.fetchall()

        if result:
            df_result_count = pd.DataFrame(result, columns=['State', 'user_count'])
            df_result_count['user_count'] = df_result_count['user_count'].astype(int)

            # Plot the interactive bar chart with hover information
            chart_count = px.bar(df_result_count, x='State', y='user_count',
                                    hover_data={'user_count': True},  # Show only 'User_count' in hover tooltip
                                    color_discrete_sequence=px.colors.sequential.Tealgrn_r)  # Set color sequence
            chart_count.update_layout(title=f'All India User Count: {u_typ} - {u_yr}, Quarter {u_qtr}',
                                        xaxis_title='State',
                                        yaxis_title='User Count',
                                        showlegend=False)  # Hide legend to improve readability
            st.plotly_chart(chart_count, use_container_width=True)
        
        # User percentage bar chart query
        cursor.execute(
            f"SELECT DISTINCT State, user_percentage FROM aggregated_user WHERE Year = '{u_yr}' AND Quarter = '{u_qtr}' AND user_brand = '{u_typ}';")
        result_percent = cursor.fetchall()

        if result_percent:
            df_result_percentage = pd.DataFrame(result_percent, columns=['State', 'user_percentage'])

            # Plot the interactive bar chart with hover information
            chart_count = px.bar(df_result_percentage, x='State', y='user_percentage',
                                    hover_data={'user_percentage': True},  # Show only 'user_percentage' in hover tooltip
                                    color_discrete_sequence=px.colors.sequential.Tealgrn_r)  # Set color sequence
            chart_count.update_layout(title=f'All India User Percentage: {u_typ} - {u_yr}, Quarter {u_qtr}',
                                        xaxis_title='State',
                                        yaxis_title='User Percentage',
                                        showlegend=False)  # Hide legend to improve readability
            st.plotly_chart(chart_count, use_container_width=True)

            # Total & Average User Count table query
            cursor.execute(
                f"SELECT Year, SUM(user_count) as Total_Registered_User, AVG(user_count) as Average_Registered_User FROM aggregated_user GROUP BY Year ORDER BY Year ASC;")
            result = cursor.fetchall()

            df_result1 = pd.DataFrame(result, columns=['Year', 'Total_Registered_User', 'Average_Registered_User'])

            # Convert 'Year' to datetime if it's stored as a string
            df_result1['Year'] = pd.to_datetime(df_result1['Year'], format='%Y')

            # Area chart to show total & average registered users over years
            fig_area_chart = px.area(
                df_result1,
                x='Year',
                y=['Total_Registered_User', 'Average_Registered_User'],
                labels={'value': 'Count', 'variable': 'Type', 'Year': 'Year'},
                title='Total and Average Registered Users (2018-2023)',
                template='plotly_white',
                color_discrete_sequence=['rgba(55, 128, 191, 0.7)', 'rgba(255, 153, 51, 0.7)'],
                width=800,
                height=400
            )

            # Display the area chart in Streamlit
            st.plotly_chart(fig_area_chart)
                
if option == 'State wise':
    st.header('Transaction and User Analysis by District')

    # Select tab
    tab1, tab2 = st.tabs(['Transaction','User'])

    # -------------------------       /     State wise Transaction        /        ------------------ #
    with tab1:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st_nm = st.selectbox('**Select State**', ('andaman-&-nicobar-islands','andhra-pradesh','arunachal-pradesh','assam','bihar',
            'chandigarh','chhattisgarh','dadra-&-nagar-haveli-&-daman-&-diu','delhi','goa', 'gujarat','haryana','himachal-pradesh','jammu-&-kashmir',
            'jharkhand','karnataka','kerala','ladakh','lakshadweep','madhya-pradesh','maharashtra','manipur','meghalaya','mizoram','nagaland',
            'odisha','puducherry','punjab','rajasthan','sikkim','tamil-nadu','telangana','tripura','uttar-pradesh','uttarakhand','west-bengal'),key='st_nm')
            
        with col2:
            tr_yr = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022','2023'),key='tr_yr')
            
        with col3:
            tr_qtr = st.selectbox('**Select Quarter**', ('1','2','3','4'),key='tr_qtr')
            
        # Fetch transaction count based on selected state, year, and quarter by District
        cursor.execute(f"""
            SELECT District, SUM(transaction_count) AS Total_Transactions
            FROM map_transaction
            WHERE State = '{st_nm}' AND Year = '{tr_yr}' AND Quarter = '{tr_qtr}'
            GROUP BY District;
        """)
        data_count = cursor.fetchall()

        if data_count:
            # Create DataFrame from fetched data
            df = pd.DataFrame(data_count, columns=['District', 'Total_Transactions'])

            # Plot the interactive pie chart
            pie_chart = px.pie(df, values='Total_Transactions', names='District',
                                title=f'{st_nm} - Total Transactions by District: {tr_yr}, Quarter {tr_qtr}')

            pie_chart.update_traces(textposition='inside', textinfo='percent+label')  # Correct usage of textinfo
            pie_chart.update_layout(showlegend=True)

            # Display the pie chart
            st.plotly_chart(pie_chart, use_container_width=True) 
                                
        # Fetch transaction amount based on selected state, year, and quarter by District
        cursor.execute(f"""
            SELECT District, SUM(transaction_amount) AS Total_Transaction_Amount
            FROM map_transaction
            WHERE State = '{st_nm}' AND Year = '{tr_yr}' AND Quarter = '{tr_qtr}'
            GROUP BY District;
        """)
        data_amount = cursor.fetchall()

        if data_amount:
            # Create DataFrame from fetched data
            df = pd.DataFrame(data_amount, columns=['District', 'Total_Transaction_Amount'])

            # Plot the interactive pie chart
            pie_chart = px.pie(df, values='Total_Transaction_Amount', names='District',
                                title=f'{st_nm} - Total Transaction Amount by District: {tr_yr}, Quarter {tr_qtr}')

            pie_chart.update_traces(textposition='inside', textinfo='percent+label')  # Correct usage of textinfo
            pie_chart.update_layout(showlegend=True)

            # Display the pie chart
            st.plotly_chart(pie_chart, use_container_width=True)

    with tab2:
        col1, col2, col3 = st.columns(3)

        with col1:
            map_sn = st.selectbox('**Select State**', ('andaman-&-nicobar-islands','andhra-pradesh','arunachal-pradesh','assam','bihar',
            'chandigarh','chhattisgarh','dadra-&-nagar-haveli-&-daman-&-diu','delhi','goa', 'gujarat','haryana','himachal-pradesh','jammu-&-kashmir',
            'jharkhand','karnataka','kerala','ladakh','lakshadweep','madhya-pradesh','maharashtra','manipur','meghalaya','mizoram','nagaland',
            'odisha','puducherry','punjab','rajasthan','sikkim','tamil-nadu','telangana','tripura','uttar-pradesh','uttarakhand','west-bengal'),key='map_sn')
            
        with col2:
            map_yr = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022','2023'),key='map_yr')
            
        with col3:
            map_qtr = st.selectbox('**Select Quarter**', ('1','2','3','4'),key='map_qtr')

        st.header('Total Registered Users by District')

        cursor.execute(f"""
            SELECT District, SUM(registered_user) AS Total_Registered_Users
            FROM map_user
            WHERE State = '{map_sn}' AND Year = '{map_yr}' AND Quarter = '{map_qtr}'
            GROUP BY District;
        """)
        data_registered_users = cursor.fetchall()

        if data_registered_users:
            # Create DataFrame from fetched data
            df_registered_users = pd.DataFrame(data_registered_users, columns=['District', 'Total_Registered_Users'])

            # Plot the interactive pie chart for total registered users
            pie_chart = px.pie(df_registered_users, values='Total_Registered_Users', names='District',
                                title=f'{map_sn} - Total Registered Users by District: {map_yr}, Quarter {map_qtr}',
                                labels={'Total_Registered_Users': 'Registered Users'})
                                # color_discrete_sequence=px.colors.sequential.Viridis)

            pie_chart.update_traces(textposition='inside', textinfo='percent+label')  # Add labels inside the pie chart

            # Display the pie chart
            st.plotly_chart(pie_chart, use_container_width=True)

        else:
            st.warning('No data available for the selected state.')
        
        #Total app_opens by registered users
        st.header('App Opens by Registered Users')

        # Fetch total registered users and app opens at district level based on selected state
        cursor.execute(f"""
            SELECT District, SUM(registered_user) AS Total_Registered_Users, SUM(app_opens) AS Total_App_Opens
            FROM map_user
            WHERE State = '{map_sn}'
            GROUP BY District;
        """)
        data_registered_users_app_opens = cursor.fetchall()

        if data_registered_users_app_opens:
            # Create DataFrame from fetched data
            df_registered_users_app_opens = pd.DataFrame(data_registered_users_app_opens, columns=['District', 'Total_Registered_Users', 'Total_App_Opens'])

            # Plot the interactive pie chart for total app opens by registered users
            pie_chart = px.pie(df_registered_users_app_opens, values='Total_App_Opens', names='District',
                                title=f'{map_sn} - Total App Opens by Registered Users: {map_yr}, Quarter {map_qtr}',
                                labels={'Total_App_Opens': 'App Opens'})

            pie_chart.update_traces(textposition='inside', textinfo='percent+label')  # Correct usage of textinfo

            # Display the pie chart
            st.plotly_chart(pie_chart, use_container_width=True)
        else:
            st.warning('No data available for the selected state.')

if option == 'Top Ten categories':
    # Select tab
    tab1, tab2 = st.tabs(['Transaction','User'])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            map_yr = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022','2023'),key='map_yr')
            
        with col2:
            map_qtr = st.selectbox('**Select Quarter**', ('1','2','3','4'),key='map_qtr')

        # st.header(f'Top Ten States - Transaction Amount for {map_yr}, Quarter {map_qtr}')
        st.title('Top Transactions Analysis')

        # Define the width for the bars in the bar chart (e.g., 0.8 for 80% of the default width)
        custom_bar_width = 0.8

        # Define the custom colors for the bars
        custom_colors = px.colors.sequential.Viridis

        # Query to get top ten states from top_transaction table
        cursor.execute(f"""
                SELECT State, SUM(Transaction_count) AS Total_Transactions, SUM(Transaction_amount) AS Total_Amount
                FROM top_transaction_district
                WHERE Year = '{map_yr}' AND Quarter = '{map_qtr}'
                GROUP BY State
                ORDER BY Total_Transactions DESC
                LIMIT 10;
            """)
        top_states_data = cursor.fetchall()

        # Create DataFrames from fetched data
        df_top_states = pd.DataFrame(top_states_data, columns=['State', 'Total_Transactions', 'Total_Amount'])

        # Plot interactive horizontal bar charts for top ten states, , and pincodes
        fig_states = px.bar(df_top_states, 
                            x='Total_Amount', 
                            y='State', 
                            orientation='h',
                            title=f'Top Ten States with Most Transactions: {map_yr}, Quarter {map_qtr}',
                            labels={'Total_Amount': 'Total Amount', 'State': 'State'},
                            color='Total_Amount',  # Specify the column to use for coloring the bars
                            color_discrete_map=custom_colors,
                            template='plotly_white')  # Use custom colors for the bars

        # Display the interactive horizontal bar charts
        st.plotly_chart(fig_states, use_container_width=True)

        # Fetch top ten districts with the most number of transactions and transaction amount
        cursor.execute(f"""
            SELECT District, SUM(Transaction_count) AS Total_Transactions, SUM(Transaction_amount) AS Total_Amount
            FROM top_transaction_district
            WHERE Year = '{map_yr}' AND Quarter = '{map_qtr}'
            GROUP BY District
            ORDER BY Total_Transactions DESC
            LIMIT 10;
        """)
        top_districts_data = cursor.fetchall()

        # Create DataFrames from fetched data 
        df_top_districts = pd.DataFrame(top_districts_data, columns=['District', 'Total_Transactions', 'Total_Amount'])

        # Plot interactive horizontal bar charts for top ten districts
        fig_districts = px.bar(df_top_districts, 
                               x='Total_Amount', 
                               y='District', 
                               orientation='h',
                               title=f'Top Ten Districts with Most Transactions: {map_yr}, Quarter {map_qtr}',
                               labels={'Total_Amount': 'Total Amount', 'District': 'District'},
                               color='Total_Amount',  # Specify the column to use for coloring the bar
                               color_discrete_map=custom_colors,
                               template='plotly_white')  # Use custom colors for the bars

        # Display the interactive horizontal bar charts
        st.plotly_chart(fig_districts, use_container_width=True)

        # Fetch top ten pincodes with the most number of transactions and transaction amount
        cursor.execute(f"""
            SELECT Pincode, SUM(Transaction_count) AS Total_Transactions, SUM(Transaction_amount) AS Total_Amount
            FROM top_transaction_pincode
            WHERE Year = '{map_yr}' AND Quarter = '{map_qtr}'
            GROUP BY Pincode
            ORDER BY Total_Transactions DESC
            LIMIT 10;
        """)
        top_pincodes_data = cursor.fetchall()

        # Create DataFrames from fetched data
        df_top_pincodes = pd.DataFrame(top_pincodes_data, columns=['Pincode', 'Total_Transactions', 'Total_Amount'])
        df_top_pincodes['Pincode'] = df_top_pincodes['Pincode'].astype(str)

        # Create the horizontal bar chart using Plotly Express
        fig_pincodes = px.bar(
            df_top_pincodes,
            x='Total_Amount',
            y='Pincode',
            orientation='h',
            title=f'Top Ten Pincodes with Most Transactions: {map_yr}, Quarter {map_qtr}',
            labels={'Total_Amount': 'Total Amount', 'Pincode': 'Pincode'},
            width=1100,# Set the custom width for the bars
            color='Total_Amount',  # Specify the column to use for coloring the bars
            color_discrete_map=custom_colors,  # Use custom colors for the bars
            template='plotly_white',  # Specify the plotly template (optional)
        )
        # Update the width of the bars in the bar chart
        fig_pincodes.update_traces(marker=dict(line=dict(width=custom_bar_width)))

        # Display the chart in Streamlit
        st.plotly_chart(fig_pincodes)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            us_yr = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022','2023'),key='us_yr')
            
        with col2:
            ur_qtr = st.selectbox('**Select Quarter**', ('1','2','3','4'),key='ur_qtr')

        st.header(f'Top Ten Registered Users Analysis')
        
        # Define the width for the bars in the bar chart (e.g., 0.8 for 80% of the default width)
        custom_bar_width = 0.8

        # Define the custom colors for the bars
        #custom_colors = px.colors.sequential.Viridis

        # Query to find top states registered users
        cursor.execute(f"""
                       SELECT State, SUM(registered_user) AS Total_Users
                        FROM top_user_district
                        WHERE Year = '{us_yr}' AND Quarter = '{ur_qtr}'
                        GROUP BY State
                        ORDER BY Total_Users DESC
                        LIMIT 10;
                        """)
        top_user_state = cursor.fetchall()

        # Create DataFrames from fetched data
        df_top_user_states = pd.DataFrame(top_user_state, columns=['State', 'Total_Users'])

        # Plot interactive horizontal bar charts for top ten states, , and pincodes
        fig_states = px.bar(df_top_user_states, 
                            x='Total_Users', 
                            y='State', 
                            orientation='h',
                            title=f'Top Ten States with Most Registered Users: {us_yr}, Quarter {ur_qtr}',
                            labels={'Total_Users': 'Total Users', 'State': 'State'},
                            color='Total_Users',  # Specify the column to use for coloring the bars
                            # color_continuous_scale='Blues',
                            #color_continuous_scale='Viridis',
                            color_continuous_scale=['#fdae61', '#fee08b', '#d73027'],
                            template='plotly_white')  # Use custom colors for the bars

        # Display the interactive horizontal bar charts
        st.plotly_chart(fig_states, use_container_width=True)

        # Fetch top ten districts with the most number of registered users
        cursor.execute(f"""
            SELECT District, SUM(registered_user) AS Total_Users
            FROM top_user_district
            WHERE Year = '{us_yr}' AND Quarter = '{ur_qtr}'
            GROUP BY District
            ORDER BY Total_Users DESC
            LIMIT 10;
        """)
        top_user_districts_data = cursor.fetchall()

        # Create DataFrames from fetched data 
        df_top_user_districts = pd.DataFrame(top_user_districts_data, columns=['District', 'Total_Users'])

        # Plot interactive horizontal bar charts for top ten districts
        fig_districts = px.bar(df_top_user_districts, 
                               x='Total_Users', 
                               y='District', 
                               orientation='h',
                               title=f'Top Ten Districts with Most Registered Users: {us_yr}, Quarter {ur_qtr}',
                               labels={'Total_Users': 'Total Users', 'District': 'District'},
                               color='Total_Users',  # Specify the column to use for coloring the bar
                            #  color_continuous_scale='Blues',
                               template='plotly_white')  # Use custom colors for the bars

        # Display the interactive horizontal bar charts
        st.plotly_chart(fig_districts, use_container_width=True)\
        
        # Fetch top ten pincodes with the most number of registered users
        cursor.execute(f"""
            SELECT Pincode, SUM(registered_user) AS Total_Users
            FROM top_user_pincode
            WHERE Year = '{us_yr}' AND Quarter = '{ur_qtr}'
            GROUP BY Pincode
            ORDER BY Total_Users DESC
            LIMIT 10;
        """)
        top_pincodes_data = cursor.fetchall()

        # Create DataFrames from fetched data
        df_top_pincodes = pd.DataFrame(top_pincodes_data, columns=['Pincode', 'Total_Users'])
        df_top_pincodes['Pincode'] = df_top_pincodes['Pincode'].astype(str)

        # Create the horizontal bar chart using Plotly Express
        fig_pincodes = px.bar(
            df_top_pincodes,
            x='Total_Users',
            y='Pincode',
            orientation='h',
            title=f'Top Ten Pincodes with Most Registered Users: {us_yr}, Quarter {ur_qtr}',
            labels={'Total_Users': 'Total Users', 'Pincode': 'Pincode'},
            width=1100,# Set the custom width for the bars
            color='Total_Users',  # Specify the column to use for coloring the bars
            # color_continuous_scale='Blues',  # Use custom colors for the bars
            template='plotly_white',  # Specify the plotly template (optional)
        )
        # Update the width of the bars in the bar chart
        fig_pincodes.update_traces(marker=dict(line=dict(width=custom_bar_width)))

        # Display the chart in Streamlit
        st.plotly_chart(fig_pincodes)





        
        



        
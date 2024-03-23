import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import io

def fetch_data_from_github(file_path):
    try:
        # Fetch the raw content of the CSV file from GitHub
        response = requests.get(file_path)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        st.error(f"Error fetching data from GitHub: {e}")
        return None

def create_subscription_growth_chart(df_sub):
    fig_sub = go.Figure()

    fig_sub.add_trace(go.Scatter(x=df_sub['Quarter'], y=df_sub['Netflix Sub Change Q2Q'],
                                 mode='lines+markers', name='Netflix',
                                 line=dict(color='red')))
    fig_sub.add_trace(go.Scatter(x=df_sub['Quarter'], y=df_sub['Disney + Sub Change Q2Q'],
                                 mode='lines+markers', name='Disney+',
                                 line=dict(color='blue')))
    fig_sub.add_trace(go.Scatter(x=df_sub['Quarter'], y=df_sub['Hulu Sub Change Q2Q'],
                                 mode='lines+markers', name='Hulu',
                                 line=dict(color='green')))
    fig_sub.add_trace(go.Scatter(x=df_sub['Quarter'], y=df_sub['Peacock Subs Change Q2Q'],
                                 mode='lines+markers', name='Peacock',
                                 line=dict(color='black')))

    fig_sub.update_layout(title_text='Subscription Growth Over Time',
                          xaxis_title='Quarter',
                          yaxis_title='Sub Increase in millions',
                          legend=dict(title='Services'))

    return fig_sub

def create_netflix_subscription_breakdown_chart(df_netflix_data):
    fig_netflix = go.Figure()

    fig_netflix.add_trace(go.Scatter(x=df_netflix_data['Quarter'], y=df_netflix_data['Sub Increase Q2Q M'],
                                     mode='lines+markers', name='Netflix', line=dict(color='red')))

    fig_netflix.add_shape(
        go.layout.Shape(
            type="rect",
            x0='19Q4',
            y0=0,
            x1='20Q2',
            y1=16,
            fillcolor="rgba(0, 0, 255, 0.15)",
            line=dict(color="rgba(255, 0, 0, 0.5)"),
        )
    )

    fig_netflix.add_annotation(
        go.layout.Annotation(
            x='19Q4',
            y=15,
            xref="x",
            yref="y",
            text="COVID-19 Pandemic",
            showarrow=True,
            arrowhead=2,
            ax=-100,
            ay=-40
        )
    )

    price_hike_quarters = df_netflix_data[df_netflix_data['Price Hike for at least 1 plan'] == True]['Quarter']
    fig_netflix.add_trace(go.Scatter(x=price_hike_quarters,
                                     y=df_netflix_data.loc[df_netflix_data['Price Hike for at least 1 plan'] == True, 'Sub Increase Q2Q M'],
                                     mode='markers', name='Price Hike for at least 1 plan',
                                     marker=dict(symbol='x', size=13, color='black')))

    fig_netflix.add_trace(go.Scatter(x=['23Q1'], y=[df_netflix_data.loc[df_netflix_data['Quarter'] == '23Q1', 'Sub Increase Q2Q M'].iloc[0]],
                                     mode='markers', name='Password Sharing Crackdown',
                                     marker=dict(symbol='circle', size=10, color='blue')))

    fig_netflix.update_layout(title_text='Detailed Netflix Subscription Timeline',xaxis_title='Quarter', yaxis_title='Sub Increase in millions', height=370)

    return fig_netflix

def create_netflix_subscription_growth_chart(df_netflix_data, df_sub):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df_netflix_data['Quarter'], 
                             y=df_netflix_data['Sub Increase Q2Q M'], 
                             mode='lines+markers', 
                             name='Netflix',
                             line=dict(color='red')))

    fig.add_trace(go.Scatter(x=df_sub['Quarter'], y=df_sub['Disney + Sub Change Q2Q'],
                             mode='lines+markers', name='Disney+',
                             line=dict(color='blue')))

    fig.update_layout(
        title_text='Netflix Sub Growth Over Time',
        xaxis_title='Quarter',
        yaxis_title='Sub Increase in millions',
        height=370
    )

    return fig

def plot_netflix_stock_growth(df_data):
    needed_quarters = ["18Q2", "18Q3", "18Q4", "19Q1", "19Q2", "19Q3", "19Q4", "20Q1", "20Q2"]
    df_data = df_data[df_data["Quarter"].isin(needed_quarters)]
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_data['Quarter'],
        y=df_data['Netflix Stock Change Q2Q %'],
        mode='lines+markers',
        name='Netflix',
        line=dict(color='red')
    ))

    fig.add_trace(go.Scatter(
        x=df_data['Quarter'],
        y=df_data['NASDAQ Change Q2Q %'],
        mode='lines+markers',
        name='NASDAQ',
        line=dict(color='blue')
    ))

    # Add marker for x = "20Q1"
    fig.add_trace(go.Scatter(
        x=["20Q1"],
        y=[df_data.loc[df_data['Quarter'] == "20Q1", 'Netflix Stock Change Q2Q %'].iloc[0]],  # Get the corresponding y value
        mode='markers',
        name='Covid-19 Beginning',
        marker=dict(color='green', size=15, symbol="cross")
    ))

    fig.update_layout(
        title_text='Netflix Stock Growth Over Quarters',
        xaxis_title='Quarter',
        yaxis_title='Stock Increase Percentage',
        yaxis=dict(tickformat=".1%"),
        height=370
    )

    st.plotly_chart(fig)


def create_genre_breakdown_charts(df_genre):
    # Create the plot for total hours viewed by genre
    genre_sum = df_genre.groupby("Genre")["Hours Viewed"].sum().reset_index()
    genre_sum_sorted = genre_sum.sort_values(by="Hours Viewed", ascending=False)
    fig_genre_total_hours = go.Figure(
        data=[go.Bar(
            x=genre_sum_sorted["Genre"],
            y=genre_sum_sorted["Hours Viewed"],
            name="Total Hours Viewed"
        )]
    )
    fig_genre_total_hours.update_layout(
        title="Total Hours Viewed by Genre",
        xaxis_title="Genre",
        yaxis_title="Total Hours Viewed",
        yaxis=dict(range=[0, genre_sum_sorted["Hours Viewed"].max() + 1000000])
    )

    # Subset the DataFrame for Genre equals Children
    df_children = df_genre[df_genre['Genre'] == 'Children']
    cocomelon_hours = df_children[df_children['Title'].str.contains('CoComelon', case=False)]['Hours Viewed'].sum()
    paw_patrol_hours = df_children[df_children['Title'].str.contains('PAW Patrol', case=False)]['Hours Viewed'].sum()
    other_hours = df_children[~df_children['Title'].str.contains('CoComelon|PAW Patrol', case=False)]['Hours Viewed'].sum()

    fig_genre_comparison = go.Figure()
    fig_genre_comparison.add_trace(go.Bar(
        x=['CoComelon & PAW Patrol', 'All Other Childrens Shows'],
        y=[cocomelon_hours + paw_patrol_hours, other_hours],
        marker_color=['blue', 'green']
    ))
    fig_genre_comparison.update_layout(
        title='CoComelon & PAW Patrol Compared to All Other Childrens TV Shows',
        xaxis_title='Category',
        yaxis_title='Combined Viewing Hours'
    )

    return fig_genre_total_hours, fig_genre_comparison

def create_region_breakdown_chart(df_region):
    fig = go.Figure()

    values = df_region[df_region['Quarter'] == df_region['Quarter'].iloc[0]][['UCAN Sub', 'EMEA Sub', 'LATAM Sub', 'APAC Sub']].iloc[0].tolist()
    pie_chart = go.Pie(labels=['UCAN Sub', 'EMEA Sub', 'LATAM Sub', 'APAC Sub'], values=values, name=df_region['Quarter'].iloc[0])
    fig.add_trace(pie_chart)

    buttons = [dict(label='Play',
                     method='animate',
                     args=[None, dict(frame=dict(duration=400, redraw=True), fromcurrent=True)]),
               dict(label='Pause',
                    method='animate',
                    args=[[None], dict(frame=dict(duration=0, redraw=True), mode='immediate')])]

    fig.update_layout(title='Subscription Distribution Over Quarters in Millions', 
                      updatemenus=[dict(type='buttons', showactive=False, buttons=buttons)],
                      annotations=[dict(text=df_region['Quarter'].iloc[0], showarrow=False, x=0.9, y=0.3, font=dict(size=20))],
                      height=380,
                      legend=dict(traceorder='normal', title=dict(font=dict(size=16)), font=dict(size=18)))  # Set the legend font size

    frames = [go.Frame(data=[go.Pie(labels=['UCAN Sub', 'EMEA Sub', 'LATAM Sub', 'APAC Sub'],
                                    values=df_region[df_region['Quarter'] == quarter][['UCAN Sub', 'EMEA Sub', 'LATAM Sub', 'APAC Sub']].iloc[0].tolist(),
                                    name=quarter)],
                       name=quarter,
                       layout=dict(annotations=[dict(text=quarter, showarrow=False, x=0.8, y=0.5, font=dict(size=20))]))
              for quarter in df_region['Quarter']]

    fig.frames = frames

    return fig


def create_mean_duration_graph(df_movies):
    df_movies["duration"] = df_movies["duration"].str.replace(' min', '')
    df_movies["duration"] = df_movies["duration"].astype(int)

    df_movies['date_added'] = pd.to_datetime(df_movies['date_added'])
    df_movies = df_movies[df_movies['date_added'].dt.year >= 2015]
    mean_duration = df_movies.groupby(df_movies['date_added'].dt.to_period('M'))['duration'].mean().reset_index()
    mean_duration['date_added'] = mean_duration['date_added'].astype(str)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=mean_duration['date_added'], y=mean_duration['duration'], mode='lines+markers', name='Mean Duration',
                             line=dict(color='blue', width=2)))

    fig.update_layout(title='Mean Duration of Netflix Movies by Month Added (Since 2015)',
                      xaxis_title='Month Added',
                      yaxis_title='Mean Duration (minutes)')

    return fig


def create_users_breakdown_histogram(df_users):
    fig = go.Figure(data=[go.Histogram(x=df_users["Age"])])

    # Update layout
    fig.update_layout(
        title="Users Age Breakdown",
        xaxis_title="Age",
        yaxis_title="Frequency"
    )

    return fig

def create_gender_distribution_pie_chart(df_users):
    gender_counts = df_users['Gender'].value_counts()
    fig = go.Figure(data=[go.Pie(labels=gender_counts.index, values=gender_counts)])

    # Update layout
    fig.update_layout(
        title="Gender Distribution",
        height=500,
        width=700
    )

    return fig

def create_subscription_pie_chart(df):
    import plotly.graph_objects as go
    
    subscription_counts = df['Subscription Type'].value_counts()
    
    fig = go.Figure(data=[go.Pie(labels=subscription_counts.index, values=subscription_counts, textinfo='label+percent')])

    custom_text = []
    for label in subscription_counts.index:
        if label == 'Basic':
            custom_text.append('$7 a month')
        elif label == 'Standard':
            custom_text.append('$10 a month')
        elif label == 'Premium':
            custom_text.append('$15 a month')
        else:
            custom_text.append('')

    fig.update_traces(text=custom_text, textposition='inside', textinfo='text+percent')

    fig.update_layout(
        title="Subscription Type Distribution",
        height=500,
        width=700
    )

    return fig

def create_subscription_revenue_bar_chart(df):
    import plotly.graph_objects as go
    
    grouped_df = df.groupby('Subscription Type')['Monthly Revenue'].sum().reset_index()

    fig = go.Figure(data=[go.Bar(
        x=grouped_df['Subscription Type'],
        y=grouped_df['Monthly Revenue'],
        marker_color='skyblue'
    )])

    # Update layout
    fig.update_layout(
        title="Monthly Revenue by Subscription Type",
        xaxis_title="Subscription Type",
        yaxis_title="Monthly Revenue",
        height=500,
        width=700
    )

    return fig


def plot_Q4_sub_growth(df_netflix_data):
    q4_mask = df_netflix_data['Just Quarter Value'] == 'Q4'
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_netflix_data['Quarter'], y=df_netflix_data['Sub Increase Q2Q M'],
                             mode='lines+markers', name='Netflix', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df_netflix_data[q4_mask]['Quarter'], y=df_netflix_data[q4_mask]['Sub Increase Q2Q M'],
                             mode='markers', name='Q4', marker=dict(color='blue', size=10, symbol='cross')))
    
    # Update layout
    fig.update_layout(title='Netflix Q4 Subscription Increase', xaxis_title='Quarter', yaxis_title='Subscription Increase')
    
    # Display the plot
    st.plotly_chart(fig)

def main():
    # Add CSS to set the theme to light mode
    st.markdown(
        """
        <style>
        body {
            color: black;
            background-color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.title("Navigation")
    # Create tabs in the sidebar
    tabs = ["Netflix Subscription Breakdown", "Genre Breakdown", "Region Breakdown", "Content Breakdown", "Users Breakdown", "Placeholder"]
    selected_tab = st.sidebar.radio("Select Analysis", tabs)

    if selected_tab == "Netflix Subscription Breakdown":
        # Placeholder for GitHub URL for subscription change over quarters data
        github_url = "https://github.com/mark-cotter/Graph_work/raw/d679935c202d14da6b62ef8eb2e9f0483f111f49/sub_change_Q2Q.csv"
        
        # Fetch data from GitHub for subscription change over quarters
        df_sub = fetch_data_from_github(github_url)
        if df_sub is not None:
            st.plotly_chart(create_subscription_growth_chart(df_sub))

            # Fetch data from GitHub for Netflix subscription breakdown
            df_netflix_data = fetch_data_from_github("https://github.com/mark-cotter/Graph_work/raw/39a76d55181e188933ea4b4b7a52db665831534a/just_netflix_data.csv")
            if df_netflix_data is not None:
                st.plotly_chart(create_netflix_subscription_breakdown_chart(df_netflix_data))
                st.write("## Analysis")
                st.write("Analysis about how the most related variable to netflix seems to be Disney+.")
                st.plotly_chart(create_netflix_subscription_growth_chart(df_netflix_data, df_sub))

                # Plot Netflix stock growth
                plot_netflix_stock_growth(df_netflix_data)
                
            else:
                st.warning("Please provide the GitHub URL for Netflix subscription breakdown data.")
        else:
            st.warning("Please provide the GitHub URL for subscription change over quarters data.")

    elif selected_tab == "Placeholder":
        # Fetch data from GitHub for Netflix subscription breakdown
        df_netflix_data = fetch_data_from_github("https://github.com/mark-cotter/Graph_work/raw/39a76d55181e188933ea4b4b7a52db665831534a/just_netflix_data.csv")
        if df_netflix_data is not None:
            st.plotly_chart(create_netflix_subscription_breakdown_chart(df_netflix_data))
            st.write("## General Observations")
            st.write("### Q4")
            st.markdown("""
            The first thing I noticed was that Q4 seems to have a consistenly higher number of new subscribers compared to the other
            quarters.
            """)
            plot_Q4_sub_growth(df_netflix_data)
            st.markdown("""
            I wanted to see if these differences were statistcally significant so I did an ANOVA (Analysis of Variance) Test in R to
            see if the mean values of Q4 and other quarters were signifcantly different
            """)
            st.image("https://github.com/mark-cotter/Graph_work/raw/8d24e9ac6a05e1539b528a6c414e3845b2a49b47/R%20Screenshot%20Q4%20Test.png")
            st.markdown("""
            The above output from the test in R has a highlighted p value of 0.02. This is lower than the 5% level of significance which allows
            me to reject the null hypothesis that the quarters are not significantly different.

            The fact that Q4 leads to higher subscription rates follows conventional wisdom that people watch more tv and movies during these
            months due to the worse weather and more time off from work for holidays
            """)


    elif selected_tab == "Genre Breakdown":
        # Load genre breakdown data
        df_genre = pd.read_csv("Netflix_Genre_Breakdown.csv")
        # Remove commas from "Hours Viewed" and convert to integer
        df_genre["Hours Viewed"] = df_genre["Hours Viewed"].str.replace(",", "").astype(int)

        fig_genre_total_hours, fig_genre_comparison = create_genre_breakdown_charts(df_genre)
        st.plotly_chart(fig_genre_total_hours)
        st.plotly_chart(fig_genre_comparison)

    elif selected_tab == "Region Breakdown":
        # Fetch data from GitHub
        df_region = fetch_data_from_github("https://github.com/mark-cotter/Graph_work/raw/d2608fd649be8cd2367a4a5a8c694651766c14e3/netflix_region_breakdown.csv")
        if df_region is not None:
            st.plotly_chart(create_region_breakdown_chart(df_region))

    elif selected_tab == "Content Breakdown":
        # Load Netflix movie details data
        df_netflix_movies_data = pd.read_csv("Netflix_movie_details.csv")
        # Create mean duration graph
        mean_duration_fig = create_mean_duration_graph(df_netflix_movies_data)
        # Display the graph
        st.plotly_chart(mean_duration_fig)
    
    elif selected_tab == "Users Breakdown":
        # Load user data and create histogram
        df_users = pd.read_csv("Netflix Userbase.csv")
        fig_users_histogram = create_users_breakdown_histogram(df_users)
        st.plotly_chart(fig_users_histogram)

        # Add pie chart for gender distribution
        fig_gender_distribution = create_gender_distribution_pie_chart(df_users)
        st.plotly_chart(fig_gender_distribution)
        
        # Add pie chart for subscription type distribution
        fig_subscription_distribution = create_subscription_pie_chart(df_users)
        st.plotly_chart(fig_subscription_distribution)
        
        # Add bar chart for subscription revenue
        fig_subscription_revenue = create_subscription_revenue_bar_chart(df_users)
        st.plotly_chart(fig_subscription_revenue)

if __name__ == "__main__":
    main()

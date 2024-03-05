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

def create_subscription_growth_chart(df_sub, selected_services):
    fig_sub = go.Figure()

    for service in selected_services:
        fig_sub.add_trace(go.Scatter(x=df_sub['Quarter'], y=df_sub[f'{service} Sub Change Q2Q'],
                                     mode='lines+markers', name=service,
                                     line=dict(color='red')))  # You can customize the color as needed

    fig_sub.update_layout(title_text='Subscription Growth Over Time',
                          xaxis_title='Quarter',
                          yaxis_title='Sub Increase in millions',
                          legend=dict(title='Services'))

    return fig_sub

def main():
    st.sidebar.title("Navigation")
    # Create tabs in the sidebar
    tabs = ["Netflix Subscription Breakdown", "Genre Breakdown", "Region Breakdown"]
    selected_tab = st.sidebar.radio("Select Analysis", tabs)

    if selected_tab == "Netflix Subscription Breakdown":
        # Placeholder for GitHub URL for subscription change over quarters data
        github_url = "https://github.com/mark-cotter/Graph_work/raw/d679935c202d14da6b62ef8eb2e9f0483f111f49/sub_change_Q2Q.csv"
        
        # Fetch data from GitHub for subscription change over quarters
        df_sub = fetch_data_from_github(github_url)
        if df_sub is not None:
            # Choose which subscription services to display
            selected_services = st.sidebar.multiselect('Select Services', df_sub.columns[1:])

            if len(selected_services) > 0:
                # Plot subscription growth over time for selected services
                fig_sub = create_subscription_growth_chart(df_sub, selected_services)
                st.plotly_chart(fig_sub)
            else:
                st.info("Please select at least one service to display.")
        else:
            st.warning("Please provide the GitHub URL for subscription change over quarters data.")

    elif selected_tab == "Genre Breakdown":
        # Load genre breakdown data
        df_genre = pd.read_csv("Netflix_Genre_Breakdown.csv")
        # Remove commas from "Hours Viewed" and convert to integer
        df_genre["Hours Viewed"] = df_genre["Hours Viewed"].str.replace(",", "").astype(int)
        # Aggregate the data by summing the hours viewed for each genre
        genre_sum = df_genre.groupby("Genre")["Hours Viewed"].sum().reset_index()
        # Sort the DataFrame by the sum of hours viewed in descending order
        genre_sum_sorted = genre_sum.sort_values(by="Hours Viewed", ascending=False)
        # Create the plot for total hours viewed by genre
        fig_genre_total_hours = go.Figure(
            data=[go.Bar(
                x=genre_sum_sorted["Genre"],  # X-axis: Genre
                y=genre_sum_sorted["Hours Viewed"],  # Y-axis: Sum of Hours Viewed
                name="Total Hours Viewed"
            )]
        )
        # Update layout for total hours viewed by genre
        fig_genre_total_hours.update_layout(
            title="Total Hours Viewed by Genre",
            xaxis_title="Genre",
            yaxis_title="Total Hours Viewed",
            yaxis=dict(range=[0, genre_sum_sorted["Hours Viewed"].max() + 1000000])  # Adjusting y-axis range
        )
        # Plot total hours viewed by genre
        st.plotly_chart(fig_genre_total_hours)

        # Subset the DataFrame for Genre equals Children
        df_children = df_genre[df_genre['Genre'] == 'Children']

        # Calculate combined viewing hours for CoComelon and PAW Patrol
        cocomelon_hours = df_children[df_children['Title'].str.contains('CoComelon', case=False)]['Hours Viewed'].sum()
        paw_patrol_hours = df_children[df_children['Title'].str.contains('PAW Patrol', case=False)]['Hours Viewed'].sum()

        # Calculate combined viewing hours for everything else
        other_hours = df_children[~df_children['Title'].str.contains('CoComelon|PAW Patrol', case=False)]['Hours Viewed'].sum()

        # Create bar chart for comparing CoComelon & PAW Patrol to all other children's TV shows
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

        # Plot comparison chart
        st.plotly_chart(fig_genre_comparison)

    elif selected_tab == "Region Breakdown":
        # Fetch data from GitHub
        df_region = fetch_data_from_github("https://github.com/mark-cotter/Graph_work/raw/d2608fd649be8cd2367a4a5a8c694651766c14e3/netflix_region_breakdown.csv")
        if df_region is not None:
            # Create and display region breakdown chart
            st.plotly_chart(create_region_breakdown_chart(df_region))

if __name__ == "__main__":
    main()


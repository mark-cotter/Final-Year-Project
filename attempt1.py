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
            # Plot subscription growth over time for subscription change over quarters data
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

            st.plotly_chart(fig_sub)

            # Fetch data from GitHub for Netflix subscription breakdown
            df_netflix_data = fetch_data_from_github("https://github.com/mark-cotter/Graph_work/raw/30874f3e1a3e36c2aa44f4bd5101818dbd7b1724/just_netflix_data_csv_error_tester.csv")
            if df_netflix_data is not None:
                # Plotting Netflix subscription breakdown
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

                st.plotly_chart(fig_netflix)
            else:
                st.warning("Please provide the GitHub URL for Netflix subscription breakdown data.")
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

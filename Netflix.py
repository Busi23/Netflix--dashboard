# Importing required libraries
import dash  
from dash import dcc, html, Input, Output  
import plotly.express as px 
import pandas as pd 

# Loading the Netflix dataset
netflix = pd.read_csv("https://raw.githubusercontent.com/Busi23/Netflix--dashboard/refs/heads/main/netflix_titles.csv")

# Extracting the years for dropdown filter 
year_options = [{'label': str(year), 'value': year} for year in sorted(netflix['release_year'].dropna().unique())]

# Extractting the content types
type_options = [{'label': t, 'value': t} for t in netflix['type'].dropna().unique()]

# Initializing  the Dash app
app = dash.Dash(__name__)
app.title = "Netflix Dashboard" 

# Layout of dashboard
app.layout = html.Div([

    # Dashboard title
    html.H1("Netflix dashboard", style={'text-align': 'center'}),
    #Creating the sidebar and its style
    html.Div([

       #Creating the filter drop downs
        html.Div([
            html.H2("Netflix filters", style={'color': 'white', 'textAlign': 'center'}),
            html.Hr(style={'borderColor': 'white'}),

           
            html.Label("Select Year", style={'color': 'white'}),
            dcc.Dropdown(id='year_filter', options=year_options, placeholder="Select a year"),
            html.Br(),

            # Type filter dropdown
            html.Label("Select Type", style={'color': 'white'}),
            dcc.Dropdown(id='type_filter', options=type_options, placeholder="Select type"),

        ], style={
            'backgroundColor': 'darkred',
            'padding': '20px',
            'width': '15%',
            'height': '100vh',
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'overflowY': 'auto'
        }),

        # Creating the style around the graphs
        html.Div([
            html.Div(dcc.Graph(id='genre_bar'), style={
                'border': '2px solid black',
                'padding': '10px',
                'margin-bottom': '20px',
                'box-shadow': '5px 5px 15px darkred',
            }),
            html.Div(dcc.Graph(id='line_content'), style={
                'border': '2px solid black',
                'padding': '10px',
                'margin-bottom': '20px',
                'box-shadow': '5px 5px 15px darkred',
            }),
            html.Div(dcc.Graph(id='pie_count'), style={
                'border': '2px solid black',
                'padding': '10px',
                'margin-bottom': '20px',
                'box-shadow': '5px 5px 15px darkred',
            }),
            html.Div(dcc.Graph(id='movies_extract'), style={
                'border': '2px solid black',
                'padding': '10px',
                'margin-bottom': '20px',
                'box-shadow': '5px 5px 15px darkred',
            }),
            html.Div(dcc.Graph(id='tv_extract'), style={
                'border': '2px solid black',
                'padding': '10px',
                'margin-bottom': '20px',
                'box-shadow': '5px 5px 15px darkred',
            }),
            html.Div(dcc.Graph(id='country_extract'), style={
                'border': '2px solid black',
                'padding': '10px',
                'margin-bottom': '20px',
                'box-shadow': '5px 5px 15px darkred',
            }),
        ], style={
            'width': '75%',
            'display': 'grid',
            'gridTemplateColumns': 'repeat(2, 1fr)',
            'gap': '20px',
            'padding': '20px',
            'margin-left': '20%'
        })
    ])
])

# Callback to update all graphs based on filter selections
@app.callback(
    [
        Output('genre_bar', 'figure'),
        Output('line_content', 'figure'),
        Output('pie_count', 'figure'),
        Output('movies_extract', 'figure'),
        Output('tv_extract', 'figure'),
        Output('country_extract', 'figure')
    ],
    [Input('year_filter', 'value'),
     Input('type_filter', 'value')]
)
def update_graphs(selected_year, selected_type):
    # Make a copy of the original dataframe to avoid modifying it directly to prevent an error
    netflix_2 = netflix.copy()

    # Filter by selected year if provided
    if selected_year:
        netflix_2 = netflix_2[netflix_2['release_year'] == selected_year]

    # Filter by selected type if provided
    if selected_type:
        netflix_2 = netflix_2[netflix_2['type'] == selected_type]

    #  Top 10 Genres Bar Chart 
    top_genres = netflix_2['listed_in'].str.split(', ', expand=True).stack().value_counts().head(10)
    genre_fig = px.bar(
        top_genres.reset_index(),
        x='count',
        y='index',
        title='Top 10 Genres',
        labels={'index': 'Genre', 'count': 'Count'},
        hover_data={'index': True, 'count': True},
        color_discrete_sequence=['#FF0000', '#FF3333', '#FF6666', '#FF9999', '#FFCCCC']
    )

    #  Content Release Timeline Line Chart 
    df_time = netflix_2.dropna(subset=['date_added']).copy()
    df_time['date_added'] = pd.to_datetime(df_time['date_added'].str.strip())
    timeline = df_time['date_added'].dt.to_period('M').value_counts().sort_index()
    timeline_fig = px.line(
        x=timeline.index.to_timestamp(),
        y=timeline.values,
        labels={'x': 'Date Added', 'y': 'Number of Titles'},
        title='Netflix Content Added Over Time'
    )
    timeline_fig.update_traces(line_color='red')

    #  Content Type Pie Chart 
    type_counts = netflix_2['type'].value_counts()
    pie_fig = px.pie(
        names=type_counts.index,
        values=type_counts.values,
        title='Movies vs TV Shows on Netflix',
        color_discrete_sequence=['#B22222', '#DC143C']
    )

    #  Movie Duration Scatter Plot
    df_movies = netflix_2[netflix_2['type'] == 'Movie'].copy()
     #Etracts the number of mintues and then converts that into a float type
    df_movies['duration_minutes'] = df_movies['duration'].str.extract(r'(\d+)').astype(float)
    movie_duration_fig = px.scatter(
        df_movies,
        x='release_year',
        y='duration_minutes',
        title='Movie Duration Over the Years',
        labels={'release_year': 'Release Year', 'duration_minutes': 'Duration (minutes)'},
        hover_data=['title'],
        color_discrete_sequence=['#FF6347']
    )

    # TV Show Seasons Scatter Plot
    df_tv = netflix_2[netflix_2['type'] == 'TV Show'].copy()
    #Etracts the number of seasons and then converts that into a float type
   
    df_tv['duration_seasons'] = df_tv['duration'].str.extract(r'(\d+)').astype(float)
    tv_show_duration_fig = px.scatter(
        df_tv,
        x='release_year',
        y='duration_seasons',
        title='TV Show Seasons Over the Years',
        labels={'release_year': 'Release Year', 'duration_seasons': 'Number of Seasons'},
        opacity=0.6,
        hover_data=['title'],
        color_discrete_sequence=['#CD5C5C']
    )

    #  Country Production Choropleth Map
    df_country = netflix_2.dropna(subset=['country']).copy()
    country_data = df_country['country'].str.split(', ').explode().value_counts().reset_index()
    country_data.columns = ['country', 'count']
    country_fig = px.choropleth(
        country_data,
        locations='country',
        locationmode='country names',
        color='count',
        color_continuous_scale='Reds',
        title='Netflix Content Production by Country'
    )

    # Return all visualizations
    return genre_fig, timeline_fig, pie_fig, movie_duration_fig, tv_show_duration_fig, country_fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

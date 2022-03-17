from dash import Dash, dcc, html, Input, Output
from penny_stock_scraper import *
import plotly.graph_objects as go
import pandas as pd

app = Dash(__name__)

# Get the top 5 stocks based on the 'Post Positive Polarity'
df = pd.DataFrame(get_sentiment_analyis()).nlargest(5, 'Post Positive Polarity')
df.reset_index(inplace=True)

def posts_graph(df):
    posts_data = [
        go.Bar(
            x=df['Ticker'],
            y=df['Post Negative Polarity'],
            name = 'Post Negative Polarity',
            hovertemplate = 'Negative Polarity: %{y}<extra></extra>',
            marker_color='red'
        ),
        go.Bar(
            x=df['Ticker'],
            y=df['Post Neutral Polarity'],
            name = 'Post Neutral Polarity',
            hovertemplate = 'Neutral Polarity: %{y}<extra></extra>',
            marker_color='lightskyblue'
        ),
        go.Bar(
            x=df['Ticker'],
            y=df['Post Positive Polarity'],
            name = 'Post Positive Polarity',
            hovertemplate = 'Positive Polarity: %{y}<extra></extra>',
            marker_color='green'
        ),
        go.Bar(
            x=df['Ticker'],
            y=df['Post Compound Polarity'],
            name = 'Post Compound Polarity',
            hovertemplate = 'Compound Polarity: %{y}<extra></extra>',
            marker_color='orange'
        )
    ]

    posts_layout = go.Layout(
        title='Post Polarities',
        title_x=0.465,
        xaxis_title='Tickers',
        yaxis_title='Score',
        legend_title='Polarities',
        barmode='group'
    )

    posts_fig = go.Figure(data=posts_data, layout=posts_layout)

    return posts_fig

def news_graph(df):
    news_data = [
        go.Bar(
            x=df['Ticker'],
            y=df['News Negative Polarity'],
            name = 'News Negative Polarity',
            hovertemplate = 'Negative Polarity: %{y}<extra></extra>',
            marker_color='red'
        ),
        go.Bar(
            x=df['Ticker'],
            y=df['News Neutral Polarity'],
            name = 'News Neutral Polarity',
            hovertemplate = 'Neutral Polarity: %{y}<extra></extra>',
            marker_color='lightskyblue'
        ),
        go.Bar(
            x=df['Ticker'],
            y=df['News Positive Polarity'],
            name = 'News Positive Polarity',
            hovertemplate = 'Positive Polarity: %{y}<extra></extra>',
            marker_color='green'
        ),
        go.Bar(
            x=df['Ticker'],
            y=df['News Compound Polarity'],
            name = 'News Compound Polarity',
            hovertemplate = 'Compound Polarity: %{y}<extra></extra>',
            marker_color='orange'
        )
    ]

    news_layout = go.Layout(
        title='News Polarities',
        title_x=0.465,
        xaxis_title='Tickers',
        yaxis_title='Score',
        legend_title='Polarities',
        barmode='group'
    )

    news_fig = go.Figure(data=news_data, layout=news_layout)

    return news_fig

app.layout = html.Div(children=[
    html.H1(children='Sentiment Analysis of the Top 5 Stocks Mentioned in r/pennystocks',
    style={'textAlign': 'center', 'font-family': 'Open Sans, verdana, arial, sans-serif'}),
    
    html.Div(children='This data includes the top 5 stocks in terms of positve sentiment in the r/pennystocks subreddit. ' +
        'The first graph show a tickers positive, neutral and negative sentiment based on post titles, post information, comments ' +  
        'and the second graph contains the sentiment analysis of news articles about the stock.', 
        style={'marginTop': 30, 'marginLeft': 300, 'marginBottom': 30, 'marginRight': 300, 
        'font-family': 'Open Sans, verdana, arial, sans-serif'}),

    dcc.Graph(
        id='posts-graph',
        figure=posts_graph(df)
    ),

    dcc.Graph(
        id='news-graph',
        figure=news_graph(df)
    ),

    html.Div([
        dcc.Dropdown([ticker for ticker in df['Ticker']], df['Ticker'].loc[0], clearable=False,
        id='ticker-dropdown', style = {'width': 120, 'font-family': 'Open Sans, verdana, arial, sans-serif'}),
    ], style={'marginTop': 20, 'display': 'flex', 'justifyContent': 'center'}),

    dcc.Graph(id='ticker-chart')
])

@app.callback(
    Output('ticker-chart', 'figure'),
    Input(component_id='ticker-dropdown', component_property='value')
)

def create_stock_chart(value):
    chart_data = get_chart_data(value)

    chart_layout = go.Layout(
        title=f'{value} Historical Price Data',
        title_x=0.5,
        yaxis_title='Price',
    )

    fig = go.Figure(data=go.Scatter(x=chart_data.index, y=chart_data['Close'],
    mode='lines'), layout=chart_layout)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
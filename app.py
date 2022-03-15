from dataclasses import dataclass
from dash import Dash, html, dcc
from matplotlib.pyplot import title
from penny_stock_scraper import *
import plotly.graph_objects as go
import pandas as pd

app = Dash(__name__)

# Get the top 5 stocks based on the 'Post Positive Polarity'
df = pd.DataFrame(get_sentiment_analyis()).nlargest(5, 'Post Positive Polarity')
df.reset_index(inplace=True)

data = [
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
        name = 'Compound Polarity',
        hovertemplate = 'Compound Polarity: %{y}<extra></extra>',
        marker_color='orange'
    )
]

layout = go.Layout(
    title='Post Polarities',
    title_x=0.465,
    xaxis_title='Tickers',
    yaxis_title='Score',
    legend_title='Polarities',
    barmode='group'
)

fig = go.Figure(data=data, layout=layout)

app.layout = html.Div(children=[
    html.H1(children='Sentiment Analysis of the Top 5 Stocks Mentioned in r/pennystocks',
    style={'textAlign': 'center', 'font-family': 'Open Sans, verdana, arial, sans-serif'}),
    
    html.Div(children='This data includes the top 5 stocks in terms of positve sentiment in the r/pennystocks subreddit. ' +
        'The first graph show a tickers positive, neutral and negative sentiment based on post titles, post information, comments ' +  
        'and the second graph contains the sentiment analysis of news articles about the stock.', 
        style={'marginTop': 30, 'marginLeft': 300, 'marginBottom': 30, 'marginRight': 300, 
        'font-family': 'Open Sans, verdana, arial, sans-serif'}),
    
    dcc.Graph(
        id='reddit-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)


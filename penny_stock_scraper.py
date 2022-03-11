from matplotlib.pyplot import polar
import pandas as pd
from config import reddit_key, reddit_secret, username, password
import praw
import re
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class Post:
    def __init__(self, ticker, title, content, comments):
        self.ticker = ticker
        self.title = title
        self.content = content
        self.comments = comments

    def get_ticker(self):
        return self.ticker

    def get_title(self):
        return self.title
    
    def get_content(self):
        return self.content

    def get_comments(self):
        return self.comments

def get_tickers():
    file = pd.read_csv('tickers.csv', usecols=[0])
    tickers = pd.DataFrame(file)
    return tickers

def reddit_login():
    reddit = praw.Reddit(
        client_id=reddit_key,
        client_secret=reddit_secret,
        password=password,
        user_agent="User-Agent",
        username=username
    )

    return reddit

def extract_ticker(string, tickers):
    string = re.sub('[^\w\s]', '', string)
    string = string.split(" ")

    for word in string:
        # Check a word in the title is a valid ticker
        if (word.isupper() and len(word) >= 4 and len(word) <= 5):
            ticker = tickers[tickers['Symbol'] == word]

            if len(ticker) > 0:
                return word

def get_news(title_ticker):
    # Get articles from the company via yahoo finance
    ticker = yf.Ticker(title_ticker)
    news = []

    for article in ticker.news:
        news.append(article['title'])

    return news

def get_posts():
    reddit = reddit_login()
    tickers = get_tickers()
    tickers_data = []
    ticker_info = {}

    # Get posts with tickers in the title and add to a dataframe
    for submission in reddit.subreddit('pennystocks').hot(limit=300):
        if(submission.upvote_ratio >= 0.65 and submission.num_comments > 1):
            title_ticker = (extract_ticker(submission.title, tickers))

            if(title_ticker != None):
                comments = []

                for comment in submission.comments:
                    comments.append(comment.body)

                news = get_news(title_ticker)
                post = Post(title_ticker, submission.title, submission.selftext, comments)

                ticker_info = {'Ticker': post.get_ticker(), 'Title': post.get_title(), 'Content': post.get_content(), 
                'Comments': post.get_comments(), 'News': news}

                tickers_data.append(ticker_info)
                
    return tickers_data

def combine_ticker_polarity(column, total_sentiment, ticker, occurrences, polarity):

    for key in polarity:
        total_sentiment.loc[total_sentiment['Ticker'] == ticker, total_sentiment.columns[column]] += polarity[key]
        total_sentiment.loc[total_sentiment['Ticker'] == ticker, total_sentiment.columns[column]] /= occurrences
        column += 1

def get_sentiment_analyis():
    tickers_data = get_posts()
    total_sentiment = pd.DataFrame(columns=['Ticker', 'Post Negative Polarity', 'Post Neutral Polarity', 'Post Positive Polarity',
    'Post Compound Polarity', 'News Negative Polarity', 'News Neutral Polarity', 'News Positive Polarity',
    'News Compound Polarity', 'Occurrences'])
    occurrences = 0
    
    extra_words = {
        'undervalued': 3.0,
        'overvalued': -3.0,
        'gem': 3.0,
        'moon' : 4.0,
        'rocket': 4.0,
        'explode': 4.0,
        'pump' : -4.0,
        'dump': -4.0
    }

    analyzer = SentimentIntensityAnalyzer()
    analyzer.lexicon.update(extra_words)

    for ticker_info in tickers_data:
        ticker = ticker_info['Ticker']
        title_polarity = analyzer.polarity_scores(ticker_info['Title'])
        content_polarity = analyzer.polarity_scores(ticker_info['Content'])
        comments_polarity = analyzer.polarity_scores(ticker_info['Comments'])
        news_polarity = analyzer.polarity_scores(ticker_info['News'])
        post_polarity = {'Title Sentiment': title_polarity, 'Content Sentiment': content_polarity, 
        'Comments Sentiment': comments_polarity}
        occurrences += 1

        #Combine polarity of post title, content and comments
        sum_post_polarity = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
        for values in post_polarity.values():
            sum_post_polarity['neg'] += values['neg']
            sum_post_polarity['neu'] += values['neu']
            sum_post_polarity['pos'] += values['pos']
            sum_post_polarity['compound'] += values['compound']

        # Combine duplicate tickers
        if any(total_sentiment.Ticker == ticker):
            occurrences += 1
            column = 1
            total_sentiment.loc[total_sentiment['Ticker'] == ticker, 'Occurrences'] = occurrences
            
            combine_ticker_polarity(column, total_sentiment, ticker, occurrences, sum_post_polarity)
            column = 5
            combine_ticker_polarity(column, total_sentiment, ticker, occurrences, news_polarity)
        else:
            row = {'Ticker': ticker, 'Posts Negative Polarity': round(sum_post_polarity['neg'], 2),
            'Post Neutral Polarity': round(sum_post_polarity['neu'], 2), 'Post Positive Polarity': round(sum_post_polarity['pos'], 2), 
            'Post Compound Polarity': round(sum_post_polarity['compound'], 2), 'News Negative Polarity': round(news_polarity['neg'], 2), 
            'News Neutral Polarity': round(news_polarity['neu'], 2), 'News Positive Polarity': round(news_polarity['pos'], 2), 
            'News Compound Polarity': round(news_polarity['compound'], 2), 'Occurrences': occurrences}

            total_sentiment = total_sentiment.append(row, ignore_index=True)

        occurrences = 0

    return total_sentiment


def get_chart_data(ticker):
    ticker_info = yf.Ticker(ticker)
    ticker_history = ticker_info.history(period='max')
    chart_df = pd.DataFrame(ticker_history)
    return chart_df

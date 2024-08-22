import csv
import re
import pandas as pd
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.express as px
import plotly.graph_objects as go
from colorama import Fore, Style
from typing import Dict
import streamlit as st

def extract_video_id(youtube_link: str) -> str:
    """
    Extracts the video ID from a YouTube link.
    
    Args:
    youtube_link (str): The YouTube URL or link.
    
    Returns:
    str: The extracted video ID or None if no valid ID is found.
    """
    video_id_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(video_id_regex, youtube_link)
    if match:
        return match.group(1)
    return None

def analyze_sentiment(csv_file: str) -> Dict[str, int]:
    """
    Analyzes the sentiment of comments in a CSV file.
    
    Args:
    csv_file (str): Path to the CSV file containing comments.
    
    Returns:
    Dict[str, int]: A dictionary with counts of neutral, positive, and negative comments.
    """
    # Initialize the sentiment analyzer
    sid = SentimentIntensityAnalyzer()

    # Read comments from the CSV file
    comments = []
    with open(csv_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            comments.append(row['Comment'])

    # Initialize sentiment counts
    num_neutral = 0
    num_positive = 0
    num_negative = 0

    # Analyze each comment's sentiment
    for comment in comments:
        sentiment_scores = sid.polarity_scores(comment)
        if sentiment_scores['compound'] == 0.0:
            num_neutral += 1
        elif sentiment_scores['compound'] > 0.0:
            num_positive += 1
        else:
            num_negative += 1

    return {'num_neutral': num_neutral, 'num_positive': num_positive, 'num_negative': num_negative}

def bar_chart(csv_file: str) -> None:
    """
    Creates and displays a bar chart of sentiment analysis results.
    
    Args:
    csv_file (str): Path to the CSV file containing comments.
    """
    # Get sentiment results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Create a DataFrame for the results
    df = pd.DataFrame({
        'Sentiment': ['Positive', 'Negative', 'Neutral'],
        'Number of Comments': [results['num_positive'], results['num_negative'], results['num_neutral']]
    })

    # Generate and display a bar chart using Plotly Express
    fig = px.bar(df, x='Sentiment', y='Number of Comments', color='Sentiment', 
                 color_discrete_sequence=['#87CEFA', '#FFA07A', '#D3D3D3'],
                 title='Sentiment Analysis Results')
    fig.update_layout(title_font=dict(size=20))
    st.plotly_chart(fig, use_container_width=True)    
    
def plot_sentiment(csv_file: str) -> None:
    """
    Creates and displays a pie chart of sentiment analysis results.
    
    Args:
    csv_file (str): Path to the CSV file containing comments.
    """
    # Get sentiment results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Define labels and values for the pie chart
    labels = ['Neutral', 'Positive', 'Negative']
    values = [results['num_neutral'], results['num_positive'], results['num_negative']]
    colors = ['yellow', 'green', 'red']

    # Generate and display a pie chart using Plotly Graph Objects
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent',
                                 marker=dict(colors=colors))])
    fig.update_layout(title={'text': 'Sentiment Analysis Results', 'font': {'size': 20, 'family': 'Arial', 'color': 'grey'},
                              'x': 0.5, 'y': 0.9},
                      font=dict(size=14))
    st.plotly_chart(fig)
    
def create_scatterplot(csv_file: str, x_column: str, y_column: str) -> None:
    """
    Creates and displays a scatter plot of data from a CSV file.
    
    Args:
    csv_file (str): Path to the CSV file containing data.
    x_column (str): The column name for the x-axis.
    y_column (str): The column name for the y-axis.
    """
    # Load data from CSV
    data = pd.read_csv(csv_file)

    # Generate and display a scatter plot using Plotly Express
    fig = px.scatter(data, x=x_column, y=y_column, color='Category')
    fig.update_layout(
        title='Scatter Plot',
        xaxis_title=x_column,
        yaxis_title=y_column,
        font=dict(size=18)
    )
    st.plotly_chart(fig, use_container_width=True)
    
def print_sentiment(csv_file: str) -> None:
    """
    Prints the overall sentiment based on the analysis of comments.
    
    Args:
    csv_file (str): Path to the CSV file containing comments.
    """
    # Get sentiment results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Determine overall sentiment
    if results['num_positive'] > results['num_negative']:
        overall_sentiment = 'POSITIVE'
        color = Fore.GREEN
    elif results['num_negative'] > results['num_positive']:
        overall_sentiment = 'NEGATIVE'
        color = Fore.RED
    else:
        overall_sentiment = 'NEUTRAL'
        color = Fore.YELLOW

    # Print overall sentiment with color formatting
    print('\n' + Style.BRIGHT + color + overall_sentiment.upper().center(50, ' ') + Style.RESET_ALL)
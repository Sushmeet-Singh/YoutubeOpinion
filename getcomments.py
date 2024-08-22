import csv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st
from sentiment import extract_video_id
import warnings

warnings.filterwarnings('ignore')

# Replace with your own API key
DEVELOPER_KEY = st.secrets["API_KEY"]
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Create a client object to interact with the YouTube API
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

def get_channel_id(video_id: str) -> str:
    """
    Retrieves the channel ID for a given video ID.
    
    Args:
    video_id (str): The ID of the YouTube video.
    
    Returns:
    str: The channel ID associated with the video.
    """
    response = youtube.videos().list(part='snippet', id=video_id).execute()
    channel_id = response['items'][0]['snippet']['channelId']
    return channel_id

def save_video_comments_to_csv(video_id: str) -> str:
    """
    Retrieves comments for a given video ID and saves them to a CSV file.
    
    Args:
    video_id (str): The ID of the YouTube video.
    
    Returns:
    str: The filename of the CSV file where comments are saved.
    """
    comments = []
    results = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText'
    ).execute()
    
    # Extract comments and usernames from API response
    while results:
        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            username = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comments.append([username, comment])
        
        # Handle pagination if there are more comments
        if 'nextPageToken' in results:
            nextPage = results['nextPageToken']
            results = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                pageToken=nextPage
            ).execute()
        else:
            break
    
    # Save comments to a CSV file
    filename = video_id + '.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Username', 'Comment'])
        writer.writerows(comments)
            
    return filename

def get_video_stats(video_id: str) -> dict:
    """
    Retrieves statistics for a given video ID.
    
    Args:
    video_id (str): The ID of the YouTube video.
    
    Returns:
    dict: A dictionary containing the video's statistics or None if an error occurs.
    """
    try:
        response = youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()
        return response['items'][0]['statistics']
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_channel_info(youtube, channel_id: str) -> dict:
    """
    Retrieves information about a channel using the channel ID.
    
    Args:
    youtube: The YouTube API client object.
    channel_id (str): The ID of the YouTube channel.
    
    Returns:
    dict: A dictionary containing channel information or None if an error occurs.
    """
    try:
        response = youtube.channels().list(
            part='snippet,statistics,brandingSettings',
            id=channel_id
        ).execute()

        channel_info = {
            'channel_title': response['items'][0]['snippet']['title'],
            'video_count': response['items'][0]['statistics']['videoCount'],
            'channel_logo_url': response['items'][0]['snippet']['thumbnails']['high']['url'],
            'channel_created_date': response['items'][0]['snippet']['publishedAt'],
            'subscriber_count': response['items'][0]['statistics']['subscriberCount'],
            'channel_description': response['items'][0]['snippet']['description']
        }

        return channel_info
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None
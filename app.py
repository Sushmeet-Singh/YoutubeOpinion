import streamlit as st
import os
from sentiment import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment
from getcomments import save_video_comments_to_csv, get_channel_info, youtube, get_channel_id, get_video_stats

def delete_non_matching_csv_files(directory_path, video_id):
    """
    Deletes all CSV files in the directory that do not match the specified video ID.
    
    Args:
    directory_path (str): Path to the directory containing CSV files.
    video_id (str): The video ID used to match the CSV file.
    """
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.csv') and file_name != f'{video_id}.csv':
            os.remove(os.path.join(directory_path, file_name))

# Streamlit configuration
st.set_page_config(page_title='Sushmeet Singh', page_icon='LOGO.png', initial_sidebar_state='auto')
st.sidebar.title("Sentimental Analysis")
st.sidebar.header("Enter YouTube Link")

# Input field for YouTube link
youtube_link = st.sidebar.text_input("Link")
directory_path = os.getcwd()

# Hide Streamlit style elements
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

if youtube_link:
    # Extract video ID from the provided YouTube link
    video_id = extract_video_id(youtube_link)
    
    if video_id:
        # Retrieve channel ID and save comments to CSV
        channel_id = get_channel_id(video_id)
        st.sidebar.write("The video ID is:", video_id)
        csv_file = save_video_comments_to_csv(video_id)
        delete_non_matching_csv_files(directory_path, video_id)
        st.sidebar.write("Comments saved to CSV!")
        st.sidebar.download_button(
            label="Download Comments",
            data=open(csv_file, 'rb').read(),
            file_name=os.path.basename(csv_file),
            mime="text/csv"
        )
        
        # Retrieve and display channel information
        channel_info = get_channel_info(youtube, channel_id)
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(channel_info['channel_logo_url'], width=250)
        
        with col2:
            st.title('YouTube Channel Name')
            st.subheader(channel_info['channel_title'])
        
        st.title(" ")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.header("Total Videos")
            st.subheader(channel_info['video_count'])
        
        with col4:
            st.header("Channel Created")
            st.subheader(channel_info['channel_created_date'][:10])
        
        with col5:
            st.header("Subscriber Count")
            st.subheader(channel_info['subscriber_count'])
        
        st.title(" ")
        
        # Retrieve and display video statistics
        stats = get_video_stats(video_id)
        st.title("Video Information:")
        col6, col7, col8 = st.columns(3)
        
        with col6:
            st.header("Total Views")
            st.subheader(stats["viewCount"])
        
        with col7:
            st.header("Like Count")
            st.subheader(stats["likeCount"])
        
        with col8:
            st.header("Comment Count")
            st.subheader(stats["commentCount"])
        
        st.header(" ")
        
        # Display the video
        _, container, _ = st.columns([10, 80, 10])
        container.video(data=youtube_link)
        
        # Analyze and display sentiment results
        results = analyze_sentiment(csv_file)
        col9, col10, col11 = st.columns(3)
        
        with col9:
            st.header("Positive Comments")
            st.subheader(results['num_positive'])
        
        with col10:
            st.header("Negative Comments")
            st.subheader(results['num_negative'])
        
        with col11:
            st.header("Neutral Comments")
            st.subheader(results['num_neutral'])
        
        bar_chart(csv_file)
        plot_sentiment(csv_file)
        
        st.subheader("Channel Description")
        st.write(channel_info['channel_description'])
    else:
        st.error("Invalid YouTube link")
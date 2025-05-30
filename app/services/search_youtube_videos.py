from openai import OpenAI
from pydantic import BaseModel
import os
from .youtube_search import search_in_youtube_by_query_text
from .youtube_link_summarizer import get_youtube_video_summary

def search_and_summarize_youtube_videos(query_text):
    video_urls = search_in_youtube_by_query_text(query_text)

    video_summary_list = []
    for video_url in video_urls:
        video_summary_list.append(get_youtube_video_summary(video_url))
    
    return video_summary_list

# print(search_and_summarize_youtube_videos("iphone 16 pro max"))
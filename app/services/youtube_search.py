from googleapiclient.discovery import build

def search_in_youtube_by_query_text(query_text):
    api_key = "AIzaSyAH3CAcPrNx4_Np4Gqc_5PmIo2uegfhSJg"
    yt = build("youtube", "v3", developerKey=api_key)

    resp = (
        yt.search()
        .list(part="snippet",
                q=query_text,
                type="video",
                order="relevance",
                maxResults=3)
        .execute()
    )

    video_urls = [f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                for item in resp["items"]]

    return video_urls

import google.generativeai as genai
from google.api_core.client_options import ClientOptions
from youtube_transcript_api import YouTubeTranscriptApi


def get_youtube_video_summary(video_url):
    ytt_api = YouTubeTranscriptApi()
    video_id = video_url.split("v=")[1].split("&")[0]
    try:
        transcription = ytt_api.get_transcript(video_id)
    except:
        return ""

    transcription_text = " ".join([entry['text'] for entry in transcription])
    print(transcription_text)

    genai.configure(api_key='tpsg-Y8I6IHw7blcJfxShj2do6iRk4r9Jzdb', transport='rest',
                    client_options=ClientOptions(api_endpoint="https://api.metisai.ir"))

    model = genai.GenerativeModel("gemini-2.0-flash")
    video_transcription = transcription_text
    response = model.generate_content(f"Please summarize the provided video transcription. The video is likely a review of a product or service. In your summary, highlight the main advantages and disadvantages discussed in the video, focusing on key points from the transcription. Ensure that the summary is clear, concise, and accurately reflects the content of the review. The video transcription is: {video_transcription}")
    
    return response.text
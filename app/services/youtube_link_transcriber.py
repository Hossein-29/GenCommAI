from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()
video_url = "https://www.youtube.com/watch?v=8TrVpzioPbg&ab_channel=TheTechChap"
video_id = video_url.split("v=")[1].split("&")[0]
transcription = ytt_api.get_transcript(video_id)
transcription_text = " ".join([entry['text'] for entry in transcription])
# print(transcription_text)
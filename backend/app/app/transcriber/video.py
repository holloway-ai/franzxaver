import yt_dlp
import openai
import os


def download_video(url,target_path):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        "outtmpl": str(target_path/"audio"),
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([url]) 
    if error_code != 0:
        raise Exception("Error downloading video")
    return target_path/"audio.mp3"

def transcribe(file_name):
    #openai.api_key = os.environ["OPENAI_API_KEY"]
    # response_format: 'json', 'text', 'vtt', 'srt', 'verbose_json'
    with open(file_name, "rb") as audio_file: 
        transcript = openai.Audio.transcribe("whisper-1", audio_file, response_format="verbose_json")
    return transcript

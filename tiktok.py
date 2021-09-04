# from TikTokApi import TikTokApi
# import requests
import youtube_dl


def download_tiktok(link, filename):
    try:
        ydl_opts = { 'outtmpl': filename }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])
        return True
    except Exception as e:
        return False

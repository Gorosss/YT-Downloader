import tkinter as tk
from tkinter import messagebox
from pytubefix import YouTube
from collections import defaultdict
from moviepy.editor import VideoFileClip, AudioFileClip
from tkinter.ttk import Progressbar

from PIL import Image, ImageTk
from io import BytesIO
import requests

from proglog import ProgressBarLogger





'''
python -m pip install -r requirements.txt

'''


class MyBarLogger(ProgressBarLogger):
    
    def callback(self, **changes):
        for (parameter, value) in changes.items():
            print ('Parameter %s is now %s' % (parameter, value))
    
    def bars_callback(self, bar, attr, value,old_value=None):
        percentage = (value / self.bars[bar]['total']) * 100
        print(f"Progress: {percentage}%")
        progress_var.set(percentage)  
        root.update_idletasks()  


def progress_bar_callback(current, total):
        progress = (current / total) * 100  
        progress_var.set(progress) 
        root.update_idletasks() 

def proceed():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return
    
    try:
        print(f"Downloading video from {url}")
        yt = YouTube(url)   


        thumbnail_url = yt.thumbnail_url
        if not thumbnail_url.lower().endswith('.jpg'):
            thumbnail_url += '.jpg'

        print(thumbnail_url)
        response = requests.get(thumbnail_url)
        img_data = response.content

        img = Image.open(BytesIO(img_data))

        thumbnail = ImageTk.PhotoImage(img)

        thumbnail_img.image = thumbnail

        thumbnail_img.config(image=thumbnail)
        
        video_title.config(text=f"Title: {yt.title}")
        video_title.pack(pady=10)
        video_author.config(text=f"Author: {yt.author}") 
        video_author.pack(pady=10)
        min, sec = divmod(yt.length, 60)
        video_duration.config(text=f"Duration: {min}:{sec} minutes") 
        video_duration.pack(pady=10) 


        streams = yt.streams  
        best_streams = {}

        streams_by_resolution = defaultdict(list)        

        best_resolution = 0

        for stream in streams:
            resolution = stream.resolution or "audio"  #
            streams_by_resolution[resolution].append(stream)

            if resolution != "audio":
                print(resolution[:-1])
                best_resolution = int(resolution[:-1]) if best_resolution < int(resolution[:-1]) else best_resolution


        best_resolution = str(best_resolution) + "p"
        option_var.set(best_resolution) 
        video_resolution = tk.OptionMenu(root, option_var, *streams_by_resolution.keys())
        video_resolution.pack(pady=10)
                
        for resolution, stream_list in streams_by_resolution.items():
            sorted_streams = sorted(
                stream_list,
                key=lambda s: (
                    s.mime_type == "video/webm",  
                    s.itag or 10000                
                )
            )

            best_streams[resolution] = sorted_streams[0]


        audio_stream = yt.streams.filter(only_audio=True, mime_type="audio/webm").first()

        download_button.config(command=lambda: download(best_streams, audio_stream))
        download_button.pack(pady=10)


         


    except Exception as e:
        print(f"Failed to download video: {e}")
    


def download (best_streams, audio_stream):
    
    try:
        target_resolution = option_var.get()

        if target_resolution in best_streams and target_resolution != "audio":
            
            video_file = best_streams[target_resolution].download(filename="video.mp4")
            audio_file = audio_stream.download(filename="audio.mp3")


            video_clip = VideoFileClip(video_file)
            audio_clip = AudioFileClip(audio_file)


            final_video = video_clip.set_audio(audio_clip)


            output_file = "output.mp4"

            final_video.write_videofile(output_file, codec="libx264", audio_codec="aac", 
                                            threads=4, logger=logger)   
        else:
            audio_stream.download(filename="audio.mp3")

    except Exception as e:
        print(f"Failed to download video: {e}")



# Create the main application window
root = tk.Tk()
root.title("YouTube Downloader")






        

url_label = tk.Label(root, text="YouTube URL:")
url_label.pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=10)


proceed_button = tk.Button(root, text="Proceed", command=proceed)
proceed_button.pack(pady=10)





thumbnail_img = tk.Label(root)
thumbnail_img.pack()

video_title = tk.Label(root)
video_author = tk.Label(root)
video_duration = tk.Label(root)

option_var = tk.StringVar()
video_resolution = tk.OptionMenu(root, option_var, [] )


download_button = tk.Button(root, text="Download")





logger = MyBarLogger()



progress_var = tk.DoubleVar()  
progress_bar = Progressbar(root, variable=progress_var, maximum=100)

root.mainloop()
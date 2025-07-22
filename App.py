import os
import threading
import subprocess
import moviepy as mp
import customtkinter as ctk
from tkinter import filedialog, Tk, PhotoImage

class VideoProcessorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Video Processing Tool")
        self.geometry("650x400")
        self.resizable(False, False)
        self.iconbitmap("icon.ico")
        
        self.message = "Waiting...To Files"
        self.tabs = ["Subtitle Extractor", "Video Spitter"]
        
        self.options = ctk.CTkSegmentedButton(self, values=self.tabs, command=self.toggle_time_segment)
        self.options.set(self.tabs[0])
        self.options.grid(row=0, column=1, pady=(20, 10))

        # Video File Selection
        self.video_label = ctk.CTkLabel(self, text="Select Video File:")
        self.video_label.grid(row=1, column=0, padx=10, pady=(40, 10), sticky="w")
        self.video_entry = ctk.CTkEntry(self, width=300)
        self.video_entry.grid(row=1, column=1, padx=10, pady=(40, 10))
        self.video_button = ctk.CTkButton(self, text="Browse", command=self.select_video)
        self.video_button.grid(row=1, column=2, padx=10, pady=(40, 10))
        
        # Output Folder Selection
        self.output_label = ctk.CTkLabel(self, text="Select Output Folder:")
        self.output_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.output_entry = ctk.CTkEntry(self, width=300)
        self.output_entry.grid(row=2, column=1, padx=10, pady=10)
        self.output_button = ctk.CTkButton(self, text="Browse", command=self.select_output_folder)
        self.output_button.grid(row=2, column=2, padx=10, pady=10)
        
        # Time Segment Input
        self.time_label = ctk.CTkLabel(self, text="Enter Time Segment (sec):")
        self.time_entry = ctk.CTkEntry(self, width=50)
        self.time_entry.insert(0, "40")  # Default value
        
        # Process Button
        self.process_button = ctk.CTkButton(self, text="Process Video", command=self.process_video)
        self.process_button.grid(row=4, column=0, pady=(60, 5), columnspan=10)
        
        # Loading Frame
        self.loading_frame = ctk.CTkFrame(self, width=300, height=50, bg_color="transparent", fg_color="transparent")
        self.loading_frame.grid(row=5, column=1, pady=10, padx=10)
        self.loading_label = ctk.CTkLabel(self.loading_frame, text=self.message)
        self.loading_label.pack(pady=10, padx=10)
        
        self.toggle_time_segment(self.options.get())
    
    def toggle_time_segment(self, selected_tab):
        if selected_tab == "Video Spitter":
            self.time_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
            self.time_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        else:
            self.time_label.grid_remove()
            self.time_entry.grid_remove()
            
    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")])
        if file_path:
            self.video_entry.delete(0, ctk.END)
            self.video_entry.insert(0, file_path)
    
    def select_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_entry.delete(0, ctk.END)
            self.output_entry.insert(0, folder_path)
    
    def split_video(self, time_segment, video_path, output_folder):
        video = mp.VideoFileClip(video_path)
        duration = video.duration
        highlights = [(i, min(i + time_segment, duration)) for i in range(0, int(duration), time_segment)]
        
        if duration != highlights[-1][-1] and (duration - highlights[-1][-1]) > 10:
            highlights.append((highlights[-1][-1], duration))
        
        for idx, (start, end) in enumerate(highlights):
            clip = video.subclipped(start, end)
            output_path = f"{output_folder}/clip_{idx + 1}.mp4"
            clip.write_videofile(output_path, codec="libx264")
            print(f"Saved: {output_path}")
        video.close()
    
    def process_video(self):
        video_path = self.video_entry.get()
        output_folder = self.output_entry.get()
                
        self.message = "Processing... Please wait"
        self.loading_label.configure(text=self.message)
        self.process_button.configure(state=ctk.DISABLED)
        
        if self.options.get() == self.tabs[1]:
            time_segment = self.time_entry.get()
            def task():
                self.split_video(int(time_segment), video_path, output_folder)
                self.process_button.configure(state=ctk.NORMAL)
                self.message = "Processing Completed!"
                self.loading_label.configure(text=self.message)
                
            threading.Thread(target=task, daemon=True).start()
                
        elif self.options.get() == self.tabs[0]:
            def task():
                self.subtitle_extractor(video_path, output_dir=output_folder)
                self.process_button.configure(state=ctk.NORMAL)
                self.message = "Processing Completed!"
                self.loading_label.configure(text=self.message)
            
            threading.Thread(target=task, daemon=True).start()
        
    def subtitle_extractor(self, video_path, output_format='srt', output_dir='subtitles'):
        os.makedirs(output_dir, exist_ok=True)
        
        ffmpeg_path = r'ffmpeg/bin/ffmpeg.exe'
        output_file = os.path.join(output_dir, f'subtitles.{output_format}')

        cmd = [ffmpeg_path, '-i', video_path, '-map', '0:s:0', output_file]
        try: subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError: 
            self.process_button.configure(state=ctk.NORMAL)
            self.message = "Processing Completed!"
            self.loading_label.configure(text=self.message)
        
if __name__ == "__main__":
    app = VideoProcessorApp()
    app.mainloop()
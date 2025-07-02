import customtkinter as ctk
from video_filter_app import VideoFilterApp

def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    VideoFilterApp(root, "Video Filter Studio")
    root.mainloop()

if __name__ == "__main__":
    main()

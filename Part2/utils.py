import os
import cv2
import datetime
from tkinter import messagebox

def ensure_screenshot_directory(folder_name="screenshots"):
    os.makedirs(folder_name, exist_ok=True)
    return folder_name

def save_screenshot(folder, original_frame, filtered_frame, filter_index, filter_params):
    from filters import apply_filter

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    original_filename = f"{folder}/original_{timestamp}.jpg"
    cv2.imwrite(original_filename, original_frame)

    if filtered_frame is None:
        filtered_frame = apply_filter(original_frame.copy(), filter_index, filter_params)

    filtered_filename = f"{folder}/filtered_{timestamp}.jpg"
    cv2.imwrite(filtered_filename, filtered_frame)

    return original_filename, filtered_filename

def show_error(message):
    messagebox.showerror("Error", message)

def calculate_fps(frame_count, last_time):
    frame_count += 1
    current_time = cv2.getTickCount() / cv2.getTickFrequency()

    if (current_time - last_time) >= 1.0:
        fps = frame_count / (current_time - last_time)
        frame_count = 0
        last_time = current_time
        return fps, frame_count, last_time

    return None, frame_count, last_time

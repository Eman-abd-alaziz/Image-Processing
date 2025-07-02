import cv2
import tkinter as tk
import customtkinter as ctk
from PIL import Image
import threading
import os

from filters import apply_filter
from ui_components import create_fonts, create_main_layout, create_video_displays, create_filter_selection
from utils import ensure_screenshot_directory, save_screenshot, show_error, calculate_fps
from filter_transitions import FadeTransition, WipeTransition, ZoomTransition, DissolveTransition

class VideoFilterApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.configure(bg="#f0f0f0")
        self.window.minsize(1200, 750)

        self.fonts = create_fonts()

        self.init_parameters()

        self.screenshot_folder = ensure_screenshot_directory()

        self.create_widgets()

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            show_error("Cannot open camera")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self.process_video)
        self.thread.daemon = True
        self.thread.start()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.fps = 0
        self.frame_count = 0
        self.last_time = cv2.getTickCount() / cv2.getTickFrequency()

        self.update_status()

    def init_parameters(self):
        self.current_filter = 0
        self.grayscale_levels = 8
        self.edge_threshold1 = 100
        self.edge_threshold2 = 200
        self.blur_kernel_size = 9
        self.cartoon_edges_threshold = 9
        self.cartoon_color_sigma = 250
        self.vignette_sigma = 200
        self.pixel_size = 15
        self.blur_level = 25

        self.transition = FadeTransition(transition_time=0.8)
        self.transition_type = "fade"
        overlays_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overlays')
        os.makedirs(overlays_dir, exist_ok=True)

    def create_widgets(self):
        self.frames = create_main_layout(self.window, self.fonts)

        self.video_displays = create_video_displays(self.frames['videos_frame'], self.fonts)

        self.filter_var = tk.IntVar(value=self.current_filter)

        create_filter_selection(self.frames['control_frame'], self.fonts, self.filter_var, self.set_filter)

        self.create_parameter_controls()

        self.create_transition_controls()

        self.create_action_buttons()

        self.create_help_section()

    def create_parameter_controls(self):
        param_frame = ctk.CTkFrame(
            self.frames['control_frame'],
            fg_color=("gray95", "gray15"),
            corner_radius=10
        )
        param_frame.pack(fill=tk.X, padx=10, pady=8)

        param_title = ctk.CTkLabel(
            param_frame,
            text="Filter Parameters",
            font=self.fonts['label'],
            anchor="w"
        )
        param_title.pack(fill=tk.X, padx=15, pady=(10, 5))

        params_container = ctk.CTkFrame(param_frame, fg_color="transparent")
        params_container.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.create_grayscale_controls(params_container)
        self.create_edge_controls(params_container)
        self.create_blur_controls(params_container)
        self.create_cartoon_controls(params_container)
        self.create_vignette_controls(params_container)
        self.create_face_filter_controls(params_container)

        self.update_parameter_visibility()

    def create_grayscale_controls(self, parent):
        self.grayscale_frame = ctk.CTkFrame(parent, fg_color="transparent")

        grayscale_label = ctk.CTkLabel(
            self.grayscale_frame,
            text="Grayscale Levels:",
            font=self.fonts['label'],
            anchor="w"
        )
        grayscale_label.pack(fill=tk.X, pady=(5, 0))

        levels_frame = ctk.CTkFrame(self.grayscale_frame, fg_color="transparent")
        levels_frame.pack(fill=tk.X, pady=(0, 5))

        self.levels_slider = ctk.CTkSlider(
            levels_frame,
            from_=2,
            to=32,
            number_of_steps=30,
            command=self.update_grayscale_levels
        )
        self.levels_slider.set(self.grayscale_levels)
        self.levels_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.levels_value = ctk.CTkLabel(levels_frame, text=str(self.grayscale_levels), width=30)
        self.levels_value.pack(side=tk.RIGHT)

    def create_edge_controls(self, parent):
        self.edge_frame = ctk.CTkFrame(parent, fg_color="transparent")

        edge_label = ctk.CTkLabel(
            self.edge_frame,
            text="Edge Detection:",
            font=self.fonts['label'],
            anchor="w"
        )
        edge_label.pack(fill=tk.X, pady=(5, 0))

        thresh1_frame = ctk.CTkFrame(self.edge_frame, fg_color="transparent")
        thresh1_frame.pack(fill=tk.X, pady=(5, 0))

        thresh1_label = ctk.CTkLabel(thresh1_frame, text="Threshold 1:", anchor="w")
        thresh1_label.pack(side=tk.LEFT, padx=(0, 10))

        self.edge_slider1 = ctk.CTkSlider(
            thresh1_frame,
            from_=0,
            to=255,
            number_of_steps=255,
            command=self.update_edge_threshold1
        )
        self.edge_slider1.set(self.edge_threshold1)
        self.edge_slider1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.edge_value1 = ctk.CTkLabel(thresh1_frame, text=str(self.edge_threshold1), width=30)
        self.edge_value1.pack(side=tk.RIGHT)

        thresh2_frame = ctk.CTkFrame(self.edge_frame, fg_color="transparent")
        thresh2_frame.pack(fill=tk.X, pady=(5, 5))

        thresh2_label = ctk.CTkLabel(thresh2_frame, text="Threshold 2:", anchor="w")
        thresh2_label.pack(side=tk.LEFT, padx=(0, 10))

        self.edge_slider2 = ctk.CTkSlider(
            thresh2_frame,
            from_=0,
            to=255,
            number_of_steps=255,
            command=self.update_edge_threshold2
        )
        self.edge_slider2.set(self.edge_threshold2)
        self.edge_slider2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.edge_value2 = ctk.CTkLabel(thresh2_frame, text=str(self.edge_threshold2), width=30)
        self.edge_value2.pack(side=tk.RIGHT)

    def create_blur_controls(self, parent):
        self.blur_frame = ctk.CTkFrame(parent, fg_color="transparent")

        blur_label = ctk.CTkLabel(
            self.blur_frame,
            text="Blur Strength:",
            font=self.fonts['label'],
            anchor="w"
        )
        blur_label.pack(fill=tk.X, pady=(5, 0))

        blur_control_frame = ctk.CTkFrame(self.blur_frame, fg_color="transparent")
        blur_control_frame.pack(fill=tk.X, pady=(5, 5))

        self.blur_slider = ctk.CTkSlider(
            blur_control_frame,
            from_=1,
            to=25,
            number_of_steps=12,
            command=self.update_blur_kernel
        )
        self.blur_slider.set(self.blur_kernel_size)
        self.blur_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.blur_value = ctk.CTkLabel(blur_control_frame, text=str(self.blur_kernel_size), width=30)
        self.blur_value.pack(side=tk.RIGHT)

    def create_cartoon_controls(self, parent):
        self.cartoon_frame = ctk.CTkFrame(parent, fg_color="transparent")

        cartoon_label = ctk.CTkLabel(
            self.cartoon_frame,
            text="Cartoon Effect:",
            font=self.fonts['label'],
            anchor="w"
        )
        cartoon_label.pack(fill=tk.X, pady=(5, 0))

        cartoon_edge_frame = ctk.CTkFrame(self.cartoon_frame, fg_color="transparent")
        cartoon_edge_frame.pack(fill=tk.X, pady=(5, 0))

        cartoon_edge_label = ctk.CTkLabel(cartoon_edge_frame, text="Edge Detail:", anchor="w")
        cartoon_edge_label.pack(side=tk.LEFT, padx=(0, 10))

        self.cartoon_edge_slider = ctk.CTkSlider(
            cartoon_edge_frame,
            from_=3,
            to=15,
            number_of_steps=6,
            command=self.update_cartoon_edge
        )
        self.cartoon_edge_slider.set(self.cartoon_edges_threshold)
        self.cartoon_edge_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.cartoon_edge_value = ctk.CTkLabel(cartoon_edge_frame, text=str(self.cartoon_edges_threshold), width=30)
        self.cartoon_edge_value.pack(side=tk.RIGHT)

        cartoon_color_frame = ctk.CTkFrame(self.cartoon_frame, fg_color="transparent")
        cartoon_color_frame.pack(fill=tk.X, pady=(5, 5))

        cartoon_color_label = ctk.CTkLabel(cartoon_color_frame, text="Color Smooth:", anchor="w")
        cartoon_color_label.pack(side=tk.LEFT, padx=(0, 10))

        self.cartoon_color_slider = ctk.CTkSlider(
            cartoon_color_frame,
            from_=50,
            to=300,
            number_of_steps=25,
            command=self.update_cartoon_color
        )
        self.cartoon_color_slider.set(self.cartoon_color_sigma)
        self.cartoon_color_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.cartoon_color_value = ctk.CTkLabel(cartoon_color_frame, text=str(self.cartoon_color_sigma), width=30)
        self.cartoon_color_value.pack(side=tk.RIGHT)

    def create_action_buttons(self):
        button_frame = ctk.CTkFrame(self.frames['control_frame'], fg_color="transparent")
        button_frame.pack(fill=tk.X, padx=10, pady=(8, 10))

        self.screenshot_btn = ctk.CTkButton(
            button_frame,
            text="Take Screenshot",
            command=self.take_screenshot,
            font=self.fonts['button'],
            height=40,
            corner_radius=8,
            fg_color=("#4f46e5", "#6366f1"),
            hover_color=("#4338ca", "#4f46e5")
        )
        self.screenshot_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        exit_btn = ctk.CTkButton(
            button_frame,
            text="Exit",
            command=self.on_closing,
            font=self.fonts['button'],
            height=40,
            corner_radius=8,
            fg_color=("#ef4444", "#dc2626"),
            hover_color=("#dc2626", "#b91c1c")
        )
        exit_btn.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)

    def create_help_section(self):
        help_frame = ctk.CTkFrame(
            self.frames['control_frame'],
            fg_color=("gray95", "gray15"),
            corner_radius=10
        )
        help_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        help_title = ctk.CTkLabel(
            help_frame,
            text="Instructions",
            font=self.fonts['label'],
            anchor="w"
        )
        help_title.pack(fill=tk.X, padx=15, pady=(10, 5))

        help_text = (
            "• Select a filter from the options above\n"
            "• Adjust parameters using the sliders\n"
            "• Take a screenshot to save the current frame\n"
            "• Screenshots are saved in the 'screenshots' folder\n"
            "• Ensure good lighting for best results"
        )

        help_content = ctk.CTkLabel(
            help_frame,
            text=help_text,
            justify=tk.LEFT,
            wraplength=280,
            anchor="w"
        )
        help_content.pack(fill=tk.X, padx=15, pady=(0, 10))

    def create_vignette_controls(self, parent):
        self.vignette_frame = ctk.CTkFrame(parent, fg_color="transparent")

        vignette_label = ctk.CTkLabel(
            self.vignette_frame,
            text="Vignette Effect:",
            font=self.fonts['label'],
            anchor="w"
        )
        vignette_label.pack(fill=tk.X, pady=(5, 0))

        vignette_control_frame = ctk.CTkFrame(self.vignette_frame, fg_color="transparent")
        vignette_control_frame.pack(fill=tk.X, pady=(5, 5))

        self.vignette_slider = ctk.CTkSlider(
            vignette_control_frame,
            from_=50,
            to=400,
            number_of_steps=35,
            command=self.update_vignette_sigma
        )
        self.vignette_slider.set(self.vignette_sigma)
        self.vignette_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.vignette_value = ctk.CTkLabel(vignette_control_frame, text=str(self.vignette_sigma), width=30)
        self.vignette_value.pack(side=tk.RIGHT)

    def create_face_filter_controls(self, parent):
        self.face_filter_frame = ctk.CTkFrame(parent, fg_color="transparent")

        face_filter_label = ctk.CTkLabel(
            self.face_filter_frame,
            text="Face Filter Settings:",
            font=self.fonts['label'],
            anchor="w"
        )
        face_filter_label.pack(fill=tk.X, pady=(5, 0))

        pixelate_frame = ctk.CTkFrame(self.face_filter_frame, fg_color="transparent")
        pixelate_frame.pack(fill=tk.X, pady=(5, 0))

        pixelate_label = ctk.CTkLabel(pixelate_frame, text="Pixel Size:", anchor="w")
        pixelate_label.pack(side=tk.LEFT, padx=(0, 10))

        self.pixel_slider = ctk.CTkSlider(
            pixelate_frame,
            from_=5,
            to=30,
            number_of_steps=25,
            command=self.update_pixel_size
        )
        self.pixel_slider.set(self.pixel_size)
        self.pixel_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.pixel_value = ctk.CTkLabel(pixelate_frame, text=str(self.pixel_size), width=30)
        self.pixel_value.pack(side=tk.RIGHT)

        blur_face_frame = ctk.CTkFrame(self.face_filter_frame, fg_color="transparent")
        blur_face_frame.pack(fill=tk.X, pady=(5, 5))

        blur_face_label = ctk.CTkLabel(blur_face_frame, text="Blur Level:", anchor="w")
        blur_face_label.pack(side=tk.LEFT, padx=(0, 10))

        self.blur_face_slider = ctk.CTkSlider(
            blur_face_frame,
            from_=5,
            to=45,
            number_of_steps=20,
            command=self.update_blur_level
        )
        self.blur_face_slider.set(self.blur_level)
        self.blur_face_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.blur_face_value = ctk.CTkLabel(blur_face_frame, text=str(self.blur_level), width=30)
        self.blur_face_value.pack(side=tk.RIGHT)

    def create_transition_controls(self):
        transition_frame = ctk.CTkFrame(
            self.frames['control_frame'],
            fg_color=("gray95", "gray15"),
            corner_radius=10
        )
        transition_frame.pack(fill=tk.X, padx=10, pady=8)

        transition_title = ctk.CTkLabel(
            transition_frame,
            text="Transition Effects",
            font=self.fonts['label'],
            anchor="w"
        )
        transition_title.pack(fill=tk.X, padx=15, pady=(10, 5))

        transition_options_frame = ctk.CTkFrame(transition_frame, fg_color="transparent")
        transition_options_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        transition_label = ctk.CTkLabel(
            transition_options_frame,
            text="Transition Type:",
            font=self.fonts['label'],
            anchor="w"
        )
        transition_label.pack(fill=tk.X, pady=(5, 0))

        self.transition_var = tk.StringVar(value="fade")

        transition_types = {
            "fade": "Fade",
            "wipe": "Wipe",
            "zoom": "Zoom",
            "dissolve": "Dissolve"
        }

        for value, text in transition_types.items():
            rb = ctk.CTkRadioButton(
                transition_options_frame,
                text=text,
                value=value,
                variable=self.transition_var,
                command=self.set_transition_type,
                font=self.fonts['label']
            )
            rb.pack(anchor=tk.W, padx=10, pady=2)

    def update_parameter_visibility(self):
        self.grayscale_frame.pack_forget()
        self.edge_frame.pack_forget()
        self.blur_frame.pack_forget()
        self.cartoon_frame.pack_forget()
        self.vignette_frame.pack_forget()
        self.face_filter_frame.pack_forget()
        if self.current_filter == 1:
            self.edge_frame.pack(fill=tk.X, pady=5)
        elif self.current_filter == 2:
            self.grayscale_frame.pack(fill=tk.X, pady=5)
        elif self.current_filter == 4:
            self.blur_frame.pack(fill=tk.X, pady=5)
        elif self.current_filter == 5:
            self.cartoon_frame.pack(fill=tk.X, pady=5)
        elif self.current_filter == 7:
            self.vignette_frame.pack(fill=tk.X, pady=5)
        elif self.current_filter >= 10 and self.current_filter < 20:
            self.face_filter_frame.pack(fill=tk.X, pady=5)

    def set_filter(self, filter_index):
        if self.current_filter != filter_index:
            params = self.get_current_params()

            self.transition.start_transition(
                from_filter=self.current_filter,
                to_filter=filter_index,
                from_params=params,
                to_params=params
            )

        self.current_filter = filter_index
        self.update_parameter_visibility()
        self.update_status_text()

    def set_transition_type(self):
        transition_type = self.transition_var.get()
        self.transition_type = transition_type

        if transition_type == "fade":
            self.transition = FadeTransition(transition_time=0.8)
        elif transition_type == "wipe":
            self.transition = WipeTransition(transition_time=0.8)
        elif transition_type == "zoom":
            self.transition = ZoomTransition(transition_time=1.0)
        elif transition_type == "dissolve":
            self.transition = DissolveTransition(transition_time=0.8)

    def update_vignette_sigma(self, value):
        self.vignette_sigma = int(float(value))
        self.vignette_value.configure(text=str(self.vignette_sigma))

    def update_pixel_size(self, value):
        self.pixel_size = int(float(value))
        self.pixel_value.configure(text=str(self.pixel_size))

    def update_blur_level(self, value):
        blur_level = int(float(value))
        if blur_level % 2 == 0:
            blur_level += 1
        self.blur_level = blur_level
        self.blur_face_value.configure(text=str(self.blur_level))

    def get_current_params(self):
        return {
            'grayscale_levels': self.grayscale_levels,
            'edge_threshold1': self.edge_threshold1,
            'edge_threshold2': self.edge_threshold2,
            'blur_kernel_size': self.blur_kernel_size,
            'cartoon_edges_threshold': self.cartoon_edges_threshold,
            'cartoon_color_sigma': self.cartoon_color_sigma,
            'vignette_sigma': self.vignette_sigma,
            'pixel_size': self.pixel_size,
            'blur_level': self.blur_level
        }

    def update_grayscale_levels(self, value):
        self.grayscale_levels = int(float(value))
        self.levels_value.configure(text=str(self.grayscale_levels))

    def update_edge_threshold1(self, value):
        self.edge_threshold1 = int(float(value))
        self.edge_value1.configure(text=str(self.edge_threshold1))

    def update_edge_threshold2(self, value):
        self.edge_threshold2 = int(float(value))
        self.edge_value2.configure(text=str(self.edge_threshold2))

    def update_blur_kernel(self, value):
        kernel_size = int(float(value))
        if kernel_size % 2 == 0:
            kernel_size += 1
        self.blur_kernel_size = kernel_size
        self.blur_value.configure(text=str(self.blur_kernel_size))

    def update_cartoon_edge(self, value):
        threshold = int(float(value))
        if threshold % 2 == 0:
            threshold += 1
        self.cartoon_edges_threshold = threshold
        self.cartoon_edge_value.configure(text=str(self.cartoon_edges_threshold))

    def update_cartoon_color(self, value):
        self.cartoon_color_sigma = int(float(value))
        self.cartoon_color_value.configure(text=str(self.cartoon_color_sigma))

    def update_status_text(self):
        filter_names = [
            "Original Video",
            "Edge Detection",
            "Grayscale Quantization",
            "Contrast Enhancement",
            "Soft and Polished",
            "Cartoon Filter",
            "Sepia Tone",
            "Vignette Effect",
            "Reserved",
            "Reserved",
            "Sunglasses Filter",
            "Hat Filter",
            "Mustache Filter",
            "Pixelate Face",
            "Blur Face",
            "Cartoon Face",
            "Negative Face",
            "Sepia Face",
            "Face Only (B&W Background)",
            "Edge Detection Face"
        ]

        if self.current_filter < len(filter_names):
            filter_name = filter_names[self.current_filter]
        else:
            filter_name = "Unknown Filter"

        self.video_displays['status_label'].configure(text=f"Status: Applying {filter_name}")

    def update_status(self):
        if self.is_running:
            self.video_displays['fps_label'].configure(text=f"FPS: {self.fps:.1f}")
            self.window.after(1000, self.update_status)

    def take_screenshot(self):
        if hasattr(self, 'current_frame'):
            params = {
                'grayscale_levels': self.grayscale_levels,
                'edge_threshold1': self.edge_threshold1,
                'edge_threshold2': self.edge_threshold2,
                'blur_kernel_size': self.blur_kernel_size,
                'cartoon_edges_threshold': self.cartoon_edges_threshold,
                'cartoon_color_sigma': self.cartoon_color_sigma
            }

            save_screenshot(self.screenshot_folder, self.current_frame, None, self.current_filter, params)

            self.video_displays['status_label'].configure(text=f"Status: Screenshots saved successfully")

            original_color = self.screenshot_btn.cget("fg_color")
            self.screenshot_btn.configure(fg_color=("green", "green"))
            self.window.after(500, lambda: self.screenshot_btn.configure(fg_color=original_color))

    def process_video(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                show_error("Can't receive frame from camera")
                break

            self.current_frame = frame.copy()

            frame = cv2.resize(frame, (480, 360))

            original_display = frame.copy()

            # Get all current parameters
            params = self.get_current_params()

            # Check if we're in a transition
            if self.transition.is_transitioning:
                # Update transition state
                self.transition.update()

                # Apply transition effect
                output = self.transition.apply(frame)

                # If transition returned None, it's complete, so apply the current filter
                if output is None:
                    output = apply_filter(frame, self.current_filter, params)
            else:
                # Apply the current filter
                output = apply_filter(frame, self.current_filter, params)

            # Calculate FPS
            fps_result, self.frame_count, self.last_time = calculate_fps(
                self.frame_count, self.last_time
            )
            if fps_result is not None:
                self.fps = fps_result

            # Convert frames to format for display
            original_rgb = cv2.cvtColor(original_display, cv2.COLOR_BGR2RGB)
            original_img = Image.fromarray(original_rgb)
            original_imgtk = ctk.CTkImage(light_image=original_img, dark_image=original_img, size=(480, 360))

            filtered_rgb = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
            filtered_img = Image.fromarray(filtered_rgb)
            filtered_imgtk = ctk.CTkImage(light_image=filtered_img, dark_image=filtered_img, size=(480, 360))

            # Update the UI
            self.window.after(0, self.update_video_labels, original_imgtk, filtered_imgtk)

    def update_video_labels(self, original_imgtk, filtered_imgtk):
        self.video_displays['original_video_label'].imgtk = original_imgtk
        self.video_displays['original_video_label'].configure(image=original_imgtk)

        self.video_displays['filtered_video_label'].imgtk = filtered_imgtk
        self.video_displays['filtered_video_label'].configure(image=filtered_imgtk)

    def on_closing(self):
        self.is_running = False
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        self.window.destroy()

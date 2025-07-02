import tkinter as tk
import customtkinter as ctk

def create_fonts():
    fonts = {
        'title': ctk.CTkFont(family="Roboto", size=18, weight="bold"),
        'subtitle': ctk.CTkFont(family="Roboto", size=14, weight="bold"),
        'label': ctk.CTkFont(family="Roboto", size=12),
        'button': ctk.CTkFont(family="Roboto", size=12)
    }
    return fonts

def create_main_layout(window, fonts):
    main_frame = ctk.CTkFrame(window, fg_color=("#f5f5f7", "#1e1e1e"))
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

    app_title = ctk.CTkLabel(
        header_frame,
        text="Video Filter Studio",
        font=fonts['title'],
        text_color=("#333", "#fff")
    )
    app_title.pack(side=tk.LEFT)

    theme_button = ctk.CTkButton(
        header_frame,
        text="Toggle Dark Mode",
        command=toggle_theme,
        width=140,
        font=fonts['button']
    )
    theme_button.pack(side=tk.RIGHT)

    content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    videos_frame = ctk.CTkFrame(content_frame, fg_color=("white", "#2d2d2d"), corner_radius=15)
    videos_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    # Create a container frame for the control panel
    control_container = ctk.CTkFrame(
        content_frame,
        width=320,
        fg_color=("white", "#2d2d2d"),
        corner_radius=15
    )
    control_container.pack(side=tk.RIGHT, fill=tk.Y)
    control_container.pack_propagate(False)

    # Create a scrollable frame inside the container
    scrollable_frame = ctk.CTkScrollableFrame(
        control_container,
        fg_color="transparent",
        corner_radius=0,
        scrollbar_fg_color=("gray75", "gray25"),
        scrollbar_button_color=("gray85", "gray30"),
        scrollbar_button_hover_color=("gray95", "gray40")
    )
    scrollable_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

    # This is the actual frame where controls will be placed
    control_frame = scrollable_frame

    return {
        'main_frame': main_frame,
        'header_frame': header_frame,
        'content_frame': content_frame,
        'videos_frame': videos_frame,
        'control_frame': control_frame,
        'control_container': control_container,
        'scrollable_frame': scrollable_frame,
        'theme_button': theme_button
    }

def create_video_displays(parent_frame, fonts):
    video_displays_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    video_displays_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    original_video_frame = ctk.CTkFrame(video_displays_frame, fg_color="transparent")
    original_video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

    original_title = ctk.CTkLabel(
        original_video_frame,
        text="Original Video",
        font=fonts['subtitle']
    )
    original_title.pack(pady=(0, 10))

    original_container = ctk.CTkFrame(
        original_video_frame,
        corner_radius=10,
        border_width=1,
        border_color=("gray80", "gray30"),
        fg_color=("gray95", "gray10")
    )
    original_container.pack(fill=tk.BOTH, expand=True)

    original_video_label = ctk.CTkLabel(original_container, text="")
    original_video_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    filtered_video_frame = ctk.CTkFrame(video_displays_frame, fg_color="transparent")
    filtered_video_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

    filtered_title = ctk.CTkLabel(
        filtered_video_frame,
        text="Filtered Video",
        font=fonts['subtitle']
    )
    filtered_title.pack(pady=(0, 10))

    filtered_container = ctk.CTkFrame(
        filtered_video_frame,
        corner_radius=10,
        border_width=1,
        border_color=("gray80", "gray30"),
        fg_color=("gray95", "gray10")
    )
    filtered_container.pack(fill=tk.BOTH, expand=True)

    filtered_video_label = ctk.CTkLabel(filtered_container, text="")
    filtered_video_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    status_frame = ctk.CTkFrame(parent_frame, fg_color=("gray90", "gray20"), height=30, corner_radius=8)
    status_frame.pack(fill=tk.X, padx=15, pady=(10, 15))

    status_label = ctk.CTkLabel(
        status_frame,
        text="Status: Ready",
        font=fonts['label'],
        text_color=("gray30", "gray80")
    )
    status_label.pack(side=tk.LEFT, padx=10)

    fps_label = ctk.CTkLabel(
        status_frame,
        text="FPS: 0",
        font=fonts['label'],
        text_color=("gray30", "gray80")
    )
    fps_label.pack(side=tk.RIGHT, padx=10)

    return {
        'original_video_label': original_video_label,
        'filtered_video_label': filtered_video_label,
        'status_label': status_label,
        'fps_label': fps_label
    }

def create_filter_selection(parent_frame, fonts, filter_var, set_filter_callback):
    filter_frame = ctk.CTkFrame(
        parent_frame,
        fg_color=("gray95", "gray15"),
        corner_radius=10
    )
    filter_frame.pack(fill=tk.X, padx=20, pady=10)

    filter_title = ctk.CTkLabel(
        filter_frame,
        text="Select Filter",
        font=fonts['label'],
        anchor="w"
    )
    filter_title.pack(fill=tk.X, padx=15, pady=(10, 5))

    basic_filters = [
        "Original Video",
        "Edge Detection",
        "Grayscale Quantization",
        "Contrast Enhancement",
        "Soft and Polished",
        "Cartoon Filter",
        "Sepia Tone",
        "Vignette Effect"
    ]

    face_filters = [
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

    filter_tabs = ctk.CTkTabview(filter_frame, height=350)
    filter_tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
    basic_tab = filter_tabs.add("Basic")
    face_tab = filter_tabs.add("Face")

    basic_frame = ctk.CTkFrame(basic_tab, fg_color="transparent")
    basic_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    for i, filter_name in enumerate(basic_filters):
        rb = ctk.CTkRadioButton(
            basic_frame,
            text=filter_name,
            value=i,
            variable=filter_var,
            command=lambda idx=i: set_filter_callback(idx),
            font=fonts['label']
        )
        rb.pack(anchor=tk.W, padx=10, pady=2)

    face_frame = ctk.CTkFrame(face_tab, fg_color="transparent")
    face_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    for i, filter_name in enumerate(face_filters):
        filter_index = i + 10
        rb = ctk.CTkRadioButton(
            face_frame,
            text=filter_name,
            value=filter_index,
            variable=filter_var,
            command=lambda idx=filter_index: set_filter_callback(idx),
            font=fonts['label']
        )
        rb.pack(anchor=tk.W, padx=10, pady=2)

    return filter_frame

def toggle_theme():
    if ctk.get_appearance_mode() == "Dark":
        ctk.set_appearance_mode("Light")
    else:
        ctk.set_appearance_mode("Dark")

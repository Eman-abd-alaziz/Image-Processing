import cv2
import numpy as np
import matplotlib.pyplot as plt
import random
from tkinter import Tk, Button, Label, Frame, BOTH, LEFT, RIGHT, TOP, BOTTOM, filedialog, Scale, StringVar, OptionMenu
from tkinter import ttk, Canvas, PhotoImage, HORIZONTAL, DISABLED, NORMAL, RIDGE, GROOVE, RAISED, SUNKEN
from PIL import Image, ImageTk
import os
import sys

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing Application")
        self.root.geometry("1200x750")
        self.root.configure(bg="#f8f9fa")
        
        # Initialize variables
        self.original_img = None
        self.original_rgb = None
        self.gray_img = None
        self.noisy_img = None
        self.current_img = None
        self.current_operation = "No Operation"
        self.brightness_value = 1.0
        
        # Create main frames
        self.create_frames()
        
        # Create UI elements
        self.create_ui_elements()
        
        # Add status bar
        self.create_status_bar()
        
        # Set theme colors
        self.set_theme()
        
    def create_frames(self):
        # Main frame
        self.main_frame = Frame(self.root, bg="#f8f9fa")
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Header frame
        self.header_frame = Frame(self.main_frame, bg="#4361ee", height=60)
        self.header_frame.pack(fill="x", pady=(0, 10))
        
        # Image frame
        self.image_frame = Frame(self.main_frame, bg="#ffffff", bd=2, relief=RIDGE)
        self.image_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        # Control frame
        self.control_frame = Frame(self.main_frame, bg="#ffffff", width=300, bd=2, relief=RIDGE)
        self.control_frame.pack(side=RIGHT, fill="y", padx=(0, 0))
        
        # Control sub-frames
        self.basic_controls = Frame(self.control_frame, bg="#ffffff")
        self.basic_controls.pack(fill="x", padx=10, pady=10)
        
        self.filter_controls = Frame(self.control_frame, bg="#ffffff")
        self.filter_controls.pack(fill="x", padx=10, pady=10)
        
        self.advanced_controls = Frame(self.control_frame, bg="#ffffff")
        self.advanced_controls.pack(fill="x", padx=10, pady=5)  # Reduced padding

    def load_image(self):
        """Load image from file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")]
        )
        if file_path:
            try:
                self.original_img = cv2.imread(file_path)
                if self.original_img is None:
                    self.update_status("Failed to load image")
                    return
                    
                self.original_rgb = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2RGB)
                self.gray_img = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2GRAY)
                
                self.display_image(self.original_img)
                self.current_img = self.original_img.copy()
                
                self.update_status(f"Image loaded: {os.path.basename(file_path)}")
                self.update_operation("Original Image")
            except Exception as e:
                self.update_status(f"Error loading image: {str(e)}")

    def convert_to_grayscale(self):
        """Convert image to grayscale"""
        if self.original_img is None:
            self.update_status("Please load an image first")
            return
        
        self.display_image(self.gray_img, is_grayscale=True)
        self.current_img = self.gray_img.copy()
        self.update_status("Image converted to grayscale")
        self.update_operation("Grayscale")

    def add_watermark(self):
        """Add watermark to image"""
        if self.current_img is None:
            self.update_status("Please load an image first")
            return
        
        watermarked_img = self.current_img.copy()
        
        if len(watermarked_img.shape) == 3:
            watermarked_img = cv2.cvtColor(watermarked_img, cv2.COLOR_BGR2GRAY)
        
        x_pos = random.randint(0, watermarked_img.shape[1] - 100)
        y_pos = random.randint(50, watermarked_img.shape[0] - 10)
        
        cv2.putText(
            watermarked_img, 
            "Eman(12113148),Ibrahim(12112090)", 
            (x_pos, y_pos), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            255, 
            2
        )
        
        self.display_image(watermarked_img, is_grayscale=True)
        self.current_img = watermarked_img.copy()
        self.update_status("Watermark added")
        self.update_operation("Watermark")

    def adjust_brightness(self):
        """Adjust image brightness"""
        if self.current_img is None:
            self.update_status("Please load an image first")
            return
        
        brightness_factor = self.brightness_value
        
        if len(self.current_img.shape) == 3:
            img_to_adjust = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)
        else:
            img_to_adjust = self.current_img.copy()
        
        bright_img = cv2.convertScaleAbs(img_to_adjust, alpha=brightness_factor, beta=0)
        self.display_image(bright_img, is_grayscale=True)
        self.current_img = bright_img.copy()
        
        self.update_status(f"Brightness adjusted to {brightness_factor:.1f}")
        self.update_operation(f"Brightness {brightness_factor:.1f}")
        
        plt.figure(figsize=(5, 3))
        plt.title(f"Histogram after Brightness Adjustment ({brightness_factor:.1f})")
        plt.hist(bright_img.ravel(), bins=256, range=[0, 256])
        plt.grid()
        plt.tight_layout()
        plt.show()

    def apply_equalization(self):
        """Apply histogram equalization"""
        if self.current_img is None:
            self.update_status("Please load an image first")
            return
        
        if len(self.current_img.shape) == 3:
            img_to_equalize = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)
        else:
            img_to_equalize = self.current_img.copy()
        
        equalized_img = cv2.equalizeHist(img_to_equalize)
        self.display_image(equalized_img, is_grayscale=True)
        self.current_img = equalized_img.copy()
        
        self.update_status("Histogram equalization applied")
        self.update_operation("Histogram Equalization")
        
        plt.figure(figsize=(12, 5))
        
        plt.subplot(2, 2, 1)
        plt.title("Before Equalization")
        plt.imshow(img_to_equalize, cmap='gray')
        plt.axis('off')
        
        plt.subplot(2, 2, 3)
        plt.title("Before Histogram")
        plt.hist(img_to_equalize.ravel(), bins=256, range=[0, 256], color='b')
        plt.xlim([0, 256])
        plt.grid(True)
        
        plt.subplot(2, 2, 2)
        plt.title("After Equalization")
        plt.imshow(equalized_img, cmap='gray')
        plt.axis('off')
        
        plt.subplot(2, 2, 4)
        plt.title("After Histogram")
        plt.hist(equalized_img.ravel(), bins=256, range=[0, 256], color='r')
        plt.xlim([0, 256])
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()

    def add_salt_pepper_noise(self):
        """Add salt and pepper noise to image"""
        if self.current_img is None:
            self.update_status("Please load an image first")
            return
        
        if len(self.current_img.shape) == 3:
            img_for_noise = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)
        else:
            img_for_noise = self.current_img.copy()
        
        def apply_noise(img, noise_prob=0.02):
            noisy_output = np.copy(img)
            probabilities = np.random.rand(*img.shape)
            noisy_output[probabilities < noise_prob] = 0
            noisy_output[probabilities > 1 - noise_prob] = 255
            return noisy_output
        
        self.noisy_img = apply_noise(img_for_noise)
        self.display_image(self.noisy_img, is_grayscale=True)
        self.current_img = self.noisy_img.copy()
        
        self.update_status("Salt & pepper noise added")
        self.update_operation("Salt & Pepper Noise")

    def apply_mean_filter(self):
        """Apply mean filter"""
        if self.noisy_img is None:
            self.update_status("Please add noise first")
            return
        
        filtered_img = cv2.blur(self.noisy_img, (3, 3))
        self.display_image(filtered_img, is_grayscale=True)
        self.current_img = filtered_img.copy()
        
        self.update_status("Mean filter applied")
        self.update_operation("Mean Filter")

    def apply_median_filter(self):
        """Apply median filter"""
        if self.noisy_img is None:
            self.update_status("Please add noise first")
            return
        
        filtered_img = cv2.medianBlur(self.noisy_img, 3)
        self.display_image(filtered_img, is_grayscale=True)
        self.current_img = filtered_img.copy()
        
        self.update_status("Median filter applied")
        self.update_operation("Median Filter")

    def sharpen_image(self):
        """Apply sharpening filter"""
        if self.current_img is None:
            self.update_status("Please load an image first")
            return
        
        if len(self.current_img.shape) == 3:
            img_to_sharpen = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)
        else:
            img_to_sharpen = self.current_img.copy()
        
        sharpening_kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        
        sharpened_img = cv2.filter2D(img_to_sharpen, -1, sharpening_kernel)
        self.display_image(sharpened_img, is_grayscale=True)
        self.current_img = sharpened_img.copy()
        
        self.update_status("Sharpening filter applied")
        self.update_operation("Sharpening Filter")

    def apply_gaussian_filter(self):
        """Apply Gaussian filter"""
        if self.current_img is None:
            self.update_status("Please load an image first")
            return
        
        if len(self.current_img.shape) == 3:
            img_to_blur = cv2.cvtColor(self.current_img, cv2.COLOR_BGR2GRAY)
        else:
            img_to_blur = self.current_img.copy()
        
        blurred_img = cv2.GaussianBlur(img_to_blur, (5, 5), 0)
        self.display_image(blurred_img, is_grayscale=True)
        self.current_img = blurred_img.copy()
        
        self.update_status("Gaussian filter applied")
        self.update_operation("Gaussian Filter")

    def compare_images(self):
        """Compare original and processed images"""
        if self.original_img is None or self.gray_img is None:
            self.update_status("Please load an image first")
            return
        
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.imshow(cv2.cvtColor(self.original_img, cv2.COLOR_BGR2RGB))
        plt.title("Original Image")
        plt.axis('off')
        
        plt.subplot(1, 2, 2)
        if len(self.current_img.shape) == 3:
            plt.imshow(cv2.cvtColor(self.current_img, cv2.COLOR_BGR2RGB))
        else:
            plt.imshow(self.current_img, cmap="gray")
        plt.title("Processed Image")
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        self.update_status("Comparing images")

    def display_image(self, img, is_grayscale=False):
        """Display the image in the UI"""
        if self.placeholder_text.winfo_exists():
            self.placeholder_text.pack_forget()
            
        img = self.resize_image(img.copy())
        
        if not is_grayscale and len(img.shape) == 3:
            img_display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            img_display = img
            
        img_pil = Image.fromarray(img_display)
        img_tk = ImageTk.PhotoImage(img_pil)
        self.image_panel.config(image=img_tk)
        self.image_panel.image = img_tk

    def resize_image(self, img, max_size=600):
        """Resize the image while maintaining aspect ratio if it exceeds max_size"""
        height, width = img.shape[:2]
        scale = min(max_size / width, max_size / height, 1.0)
        if scale < 1.0:
            img = cv2.resize(img, (int(width * scale), int(height * scale)))
        return img

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def update_operation(self, operation):
        self.current_operation = operation
        self.operation_var.set(f"Current Operation: {operation}")
    
    def update_brightness(self, val):
        self.brightness_value = float(val)

    def create_ui_elements(self):
        # Application title
        title_label = Label(self.header_frame, text="Image Processing Application", 
                           font=("Arial", 18, "bold"), bg="#4361ee", fg="white")
        title_label.pack(pady=15)
        
        # Image display area
        self.image_panel = Label(self.image_frame, bg="#f8f9fa")
        self.image_panel.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Initial message
        self.placeholder_text = Label(self.image_panel, 
                                     text="Select an image to start processing", 
                                     font=("Arial", 14), bg="#f8f9fa", fg="#495057")
        self.placeholder_text.pack(fill=BOTH, expand=True)
        
        # Basic tools section
        basic_title = Label(self.basic_controls, text="Basic Tools", 
                           font=("Arial", 12, "bold"), bg="#ffffff", fg="#4361ee")
        basic_title.pack(anchor="w", pady=(0, 3))
        
        ttk.Separator(self.basic_controls).pack(fill="x", pady=3)
        
        # Basic tools buttons
        self.create_button(self.basic_controls, "Load Image", self.load_image, "#4cc9f0")
        self.create_button(self.basic_controls, "Convert to Grayscale", self.convert_to_grayscale, "#4895ef")
        self.create_button(self.basic_controls, "Add Watermark", self.add_watermark, "#4361ee")
        
        # Brightness control
        brightness_frame = Frame(self.basic_controls, bg="#ffffff")
        brightness_frame.pack(fill="x", pady=5)
        
        brightness_label = Label(brightness_frame, text="Brightness:", bg="#ffffff")
        brightness_label.pack(side=LEFT)
        
        self.brightness_scale = Scale(brightness_frame, from_=0.1, to=3.0, resolution=0.1,
                                     orient=HORIZONTAL, length=150, bg="#ffffff", 
                                     highlightthickness=0, command=self.update_brightness)
        self.brightness_scale.set(1.0)
        self.brightness_scale.pack(side=RIGHT)
        
        self.create_button(self.basic_controls, "Apply Brightness", self.adjust_brightness, "#3a0ca3")
        
        # Filters section
        filter_title = Label(self.filter_controls, text="Filters & Effects", 
                            font=("Arial", 12, "bold"), bg="#ffffff", fg="#4361ee")
        filter_title.pack(anchor="w", pady=(5, 3))
        
        ttk.Separator(self.filter_controls).pack(fill="x", pady=3)
        
        # Filter buttons
        self.create_button(self.filter_controls, "Add Salt & Pepper Noise", self.add_salt_pepper_noise, "#7209b7")
        self.create_button(self.filter_controls, "Apply Mean Filter", self.apply_mean_filter, "#560bad")
        self.create_button(self.filter_controls, "Apply Median Filter", self.apply_median_filter, "#480ca8")
        self.create_button(self.filter_controls, "Apply Sharpening Filter", self.sharpen_image, "#3a0ca3")
        self.create_button(self.filter_controls, "Apply Gaussian Filter", self.apply_gaussian_filter, "#3f37c9")
        
        # Advanced tools section
        advanced_title = Label(self.advanced_controls, text="Advanced Tools", 
                              font=("Arial", 12, "bold"), bg="#ffffff", fg="#4361ee")
        advanced_title.pack(anchor="w", pady=(5, 3))
        
        ttk.Separator(self.advanced_controls).pack(fill="x", pady=3)
        
        # Advanced tools buttons with smaller padding
        self.create_button_small(self.advanced_controls, "Histogram Equalization", self.apply_equalization, "#4895ef")
        self.create_button_small(self.advanced_controls, "Compare Images", self.compare_images, "#4cc9f0")
        
        # Developer information
        dev_frame = Frame(self.control_frame, bg="#e9ecef", bd=1, relief=GROOVE)
        dev_frame.pack(fill="x", side=BOTTOM, padx=10, pady=10)
        
        dev_label = Label(dev_frame, text="Developed by: Eman(12113148), Ibrahim(12112090)", 
                         font=("Arial", 8), bg="#e9ecef", fg="#495057")
        dev_label.pack(pady=5)

    def create_button_small(self, parent, text, command, color="#4361ee"):
        """Create buttons with smaller padding for advanced tools section"""
        btn = Button(parent, text=text, command=command,
                    bg=color, fg="white", font=("Arial", 9, "bold"),
                    relief=RAISED, borderwidth=1, padx=5, pady=3)
        btn.pack(fill="x", pady=2)
        return btn

    def create_status_bar(self):
        # Status bar
        self.status_frame = Frame(self.root, bg="#4361ee", height=25)
        self.status_frame.pack(side=BOTTOM, fill="x")
        
        self.status_var = StringVar()
        self.status_var.set("Ready")
        
        self.status_label = Label(self.status_frame, textvariable=self.status_var, 
                                 font=("Arial", 9), bg="#4361ee", fg="white", anchor="w")
        self.status_label.pack(side=LEFT, padx=10)
        
        self.operation_var = StringVar()
        self.operation_var.set("Current Operation: None")
        
        self.operation_label = Label(self.status_frame, textvariable=self.operation_var, 
                                    font=("Arial", 9), bg="#4361ee", fg="white", anchor="e")
        self.operation_label.pack(side=RIGHT, padx=10)
        
    def set_theme(self):
        # Set button style
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), borderwidth=1)
        style.configure("TScale", background="#ffffff")
        
    def create_button(self, parent, text, command, color="#4361ee"):
        button_frame = Frame(parent, bg="#ffffff")
        button_frame.pack(fill="x", pady=3)
        
        button = Button(button_frame, text=text, command=command, 
                       bg=color, fg="white", font=("Arial", 10, "bold"),
                       relief=RAISED, borderwidth=1, padx=5, pady=5)
        button.pack(fill="x")
        return button

# Run the application
if __name__ == "__main__":
    root = Tk()
    app = ImageProcessingApp(root)
    root.mainloop()

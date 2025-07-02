# 🖼️ Image Processing App

![Image Processing Banner](assets/banner.png)

Image Processing App is a Python-based educational and practical toolkit that enables users to explore and apply essential image processing techniques through an interactive interface or real-time camera feed. Designed with students and developers in mind, the app combines GUI interactivity with real-time computer vision to demonstrate how various filters affect digital images and video frames.

The application consists of two main modules:

- 🖼️ **Part 1** – Upload image from device and apply processing filters via GUI.
- 📷 **Part 2** – Apply filters to live webcam feed (global or face-only).

---

## 🧩 Table of Contents

- [🚀 Core Features](#-core-features)
- [🛠️ Technologies Used](#-technologies-used)
- [⚙️ Getting Started](#-getting-started)
- [📂 Project Structure](#-project-structure)
- [🧠 Learning Outcomes](#-learning-outcomes)
- [📸 Demo Screenshots](#-demo-screenshots)
- [📬 Contact](#-contact)

---

## 🚀 Core Features

### 🧾 Image Upload and Processing (GUI)
Users can upload images and apply filters interactively through a Tkinter-based GUI. Features include:
- 🖤 Grayscale Conversion  
- 🌞 Brightness Adjustment  
- 📊 Histogram Equalization  
- ⚫ Salt & Pepper Noise Addition  
- 🧹 Mean & Median Filters for Noise Removal  
- 🌀 Gaussian Blur  
- ✨ Image Sharpening  
- 💧 Watermark Insertion  
- 🔁 Before/After Image Comparison  

### 📷 Real-Time Camera Filters
The second module accesses the webcam and allows users to:
- Apply filters globally on all video frames.
- Detect faces using Haar cascades and apply filters to face regions only.
- View live camera feed with dynamic processing.

---

## 🛠️ Technologies Used

| Library / Tool      | Description                                      |
|---------------------|--------------------------------------------------|
| 🐍 Python           | Primary programming language                     |
| 🖼️ OpenCV           | Image and video processing                       |
| 🧱 Tkinter          | Graphical user interface for desktop interaction |
| 🧾 PIL (Pillow)     | Image conversions and rendering                  |
| 📁 os, sys          | File and path management                         |

Install required packages:
```bash
pip install opencv-python Pillow

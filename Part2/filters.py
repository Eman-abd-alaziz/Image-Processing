import cv2
import numpy as np

def edge_detection(frame, threshold1, threshold2):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, threshold1, threshold2)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

def grayscale_quantization(frame, levels):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    quantized = (gray // (256 // levels)) * (256 // levels)
    return cv2.cvtColor(quantized, cv2.COLOR_GRAY2BGR)

def contrast_enhancement(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    enhanced_lab = cv2.merge((cl, a, b))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

def soft_polished(frame, kernel_size):
    return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)

def cartoon_filter(frame, edges_threshold, color_sigma):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    gray_blurred = cv2.medianBlur(gray, 7)

    edges = cv2.adaptiveThreshold(
        gray_blurred,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        edges_threshold,
        edges_threshold
    )

    color = cv2.bilateralFilter(
        frame,
        d=9,
        sigmaColor=color_sigma,
        sigmaSpace=color_sigma
    )

    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

def sepia_filter(frame):
    sepia_kernel = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])

    sepia = cv2.transform(frame, sepia_kernel)
    sepia = np.clip(sepia, 0, 255).astype(np.uint8)
    return sepia

def vignette_filter(frame, sigma=200):
    height, width = frame.shape[:2]

    X_resultant, Y_resultant = np.meshgrid(np.arange(width), np.arange(height))
    centerX, centerY = width // 2, height // 2

    dist = np.sqrt((X_resultant - centerX) ** 2 + (Y_resultant - centerY) ** 2)

    dist = dist / np.max(dist)

    mask = np.exp(-dist ** 2 / (2 * (sigma / 1000) ** 2))
    mask = np.dstack([mask] * 3)
    vignette = frame * mask
    return vignette.astype(np.uint8)

def apply_filter(frame, filter_index, params):
    if filter_index == 1:
        return edge_detection(frame, params['edge_threshold1'], params['edge_threshold2'])
    elif filter_index == 2:
        return grayscale_quantization(frame, params['grayscale_levels'])
    elif filter_index == 3:
        return contrast_enhancement(frame)
    elif filter_index == 4:
        return soft_polished(frame, params['blur_kernel_size'])
    elif filter_index == 5:
        return cartoon_filter(frame, params['cartoon_edges_threshold'], params['cartoon_color_sigma'])
    elif filter_index == 6:
        return sepia_filter(frame)
    elif filter_index == 7:
        sigma = params.get('vignette_sigma', 200)
        return vignette_filter(frame, sigma)
    elif filter_index >= 10 and filter_index < 20:
        from face_detection import apply_face_filter

        face_filter_types = {
            10: "sunglasses",
            11: "hat",
            12: "mustache",
            13: "pixelate",
            14: "blur",
            15: "cartoon_face",
            16: "negative",
            17: "sepia_face",
            18: "face_only",
            19: "edge_face"
        }

        face_filter_type = face_filter_types.get(filter_index, "blur")
        return apply_face_filter(frame, face_filter_type, params)



    return frame.copy()

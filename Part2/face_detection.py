import cv2
import numpy as np
import os

face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'

face_cascade = cv2.CascadeClassifier(face_cascade_path)
eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

def load_overlay(overlay_name):
    overlay_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overlays')
    os.makedirs(overlay_dir, exist_ok=True)

    overlay_path = os.path.join(overlay_dir, f"{overlay_name}.png")

    if not os.path.exists(overlay_path):
        return None

    overlay = cv2.imread(overlay_path, cv2.IMREAD_UNCHANGED)
    return overlay

def apply_overlay(frame, overlay, x, y, w, h):
    if overlay is None:
        return frame

    overlay_resized = cv2.resize(overlay, (w, h))

    if overlay_resized.shape[2] == 4:
        alpha = overlay_resized[:, :, 3] / 255.0
        alpha = np.expand_dims(alpha, axis=2)

        overlay_rgb = overlay_resized[:, :, 0:3]

        roi = frame[y:y+h, x:x+w]

        blended = (1.0 - alpha) * roi + alpha * overlay_rgb

        frame[y:y+h, x:x+w] = blended

    return frame

def apply_face_filter(frame, filter_type, params=None):
    if params is None:
        params = {}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    result = frame.copy()
    for (x, y, w, h) in faces:
        if filter_type == "sunglasses":
            roi_gray = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)

            if len(eyes) >= 2:
                eyes = sorted(eyes, key=lambda e: e[0])

                eye_x = x + eyes[0][0]
                eye_y = y + eyes[0][1]
                eye_w = eyes[1][0] + eyes[1][2] - eyes[0][0]
                eye_h = int(eye_w * 0.5)

                sunglasses = load_overlay("sunglasses")
                if sunglasses is not None:
                    result = apply_overlay(result, sunglasses, eye_x, eye_y, eye_w, eye_h)

        elif filter_type == "hat":
            hat_w = int(w * 1.2)
            hat_h = int(h * 0.6)
            hat_x = x - int((hat_w - w) / 2)
            hat_y = y - hat_h + int(0.1 * h)

            hat = load_overlay("hat")
            if hat is not None:
                result = apply_overlay(result, hat, hat_x, hat_y, hat_w, hat_h)

        elif filter_type == "mustache":
            mustache_w = int(w * 0.6)
            mustache_h = int(h * 0.15)
            mustache_x = x + int(w * 0.2)
            mustache_y = y + int(h * 0.65)

            mustache = load_overlay("mustache")
            if mustache is not None:
                result = apply_overlay(result, mustache, mustache_x, mustache_y, mustache_w, mustache_h)

        elif filter_type == "pixelate":
            face_roi = result[y:y+h, x:x+w]

            pixel_size = params.get('pixel_size', 15)

            h_face, w_face = face_roi.shape[:2]
            temp = cv2.resize(face_roi, (w_face // pixel_size, h_face // pixel_size),
                             interpolation=cv2.INTER_LINEAR)
            pixelated_face = cv2.resize(temp, (w_face, h_face),
                                       interpolation=cv2.INTER_NEAREST)

            result[y:y+h, x:x+w] = pixelated_face

        elif filter_type == "blur":
            face_roi = result[y:y+h, x:x+w]

            blur_level = params.get('blur_level', 25)

            blurred_face = cv2.GaussianBlur(face_roi, (blur_level, blur_level), 0)

            result[y:y+h, x:x+w] = blurred_face

        elif filter_type == "cartoon_face":
            face_roi = result[y:y+h, x:x+w]

            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            gray_blurred = cv2.medianBlur(gray_face, 5)

            edges = cv2.adaptiveThreshold(
                gray_blurred, 255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY, 9, 9
            )

            color = cv2.bilateralFilter(face_roi, 9, 300, 300)

            cartoon_face = cv2.bitwise_and(color, color, mask=edges)

            result[y:y+h, x:x+w] = cartoon_face

        elif filter_type == "negative":
            face_roi = result[y:y+h, x:x+w]

            negative_face = 255 - face_roi

            result[y:y+h, x:x+w] = negative_face

        elif filter_type == "sepia_face":
            face_roi = result[y:y+h, x:x+w]

            sepia_kernel = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])

            sepia_face = cv2.transform(face_roi, sepia_kernel)
            sepia_face = np.clip(sepia_face, 0, 255).astype(np.uint8)

            result[y:y+h, x:x+w] = sepia_face

        elif filter_type == "face_only":
            gray_frame = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2BGR)

            mask = np.zeros_like(result)
            mask[y:y+h, x:x+w] = 255

            result = np.where(mask > 0, result, gray_frame)

        elif filter_type == "edge_face":
            face_roi = result[y:y+h, x:x+w]

            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray_face, 100, 200)
            edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

            result[y:y+h, x:x+w] = edges_colored

    return result

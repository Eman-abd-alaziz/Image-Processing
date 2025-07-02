import cv2
import numpy as np
import time
from filters import apply_filter

class FilterTransition:
    def __init__(self, transition_time=1.0):
        self.transition_time = transition_time
        self.transition_start_time = None
        self.is_transitioning = False
        self.from_filter = None
        self.to_filter = None
        self.from_params = None
        self.to_params = None
        self.from_custom_filter = None
        self.to_custom_filter = None

    def start_transition(self, from_filter, to_filter, from_params=None, to_params=None,
                         from_custom_filter=None, to_custom_filter=None):
        self.transition_start_time = time.time()
        self.is_transitioning = True
        self.from_filter = from_filter
        self.to_filter = to_filter
        self.from_params = from_params if from_params else {}
        self.to_params = to_params if to_params else {}
        self.from_custom_filter = from_custom_filter
        self.to_custom_filter = to_custom_filter

    def update(self):
        if not self.is_transitioning:
            return

        current_time = time.time()
        elapsed = current_time - self.transition_start_time


        if elapsed >= self.transition_time:
            self.is_transitioning = False

    def apply(self, frame):
        if not self.is_transitioning:
            return None

        current_time = time.time()
        elapsed = current_time - self.transition_start_time


        progress = min(elapsed / self.transition_time, 1.0)


        if self.from_custom_filter:
            from_result = self.from_custom_filter.apply(frame.copy())
        else:
            from_result = apply_filter(frame.copy(), self.from_filter, self.from_params)


        if self.to_custom_filter:
            to_result = self.to_custom_filter.apply(frame.copy())
        else:
            to_result = apply_filter(frame.copy(), self.to_filter, self.to_params)


        blended = self.blend_frames(from_result, to_result, progress)

        return blended

    def blend_frames(self, frame1, frame2, alpha):
        return cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)

class FadeTransition(FilterTransition):
    def blend_frames(self, frame1, frame2, alpha):
        return cv2.addWeighted(frame1, 1 - alpha, frame2, alpha, 0)

class WipeTransition(FilterTransition):
    def blend_frames(self, frame1, frame2, alpha):
        _, w = frame1.shape[:2]
        wipe_position = int(w * alpha)

        result = frame1.copy()
        result[:, :wipe_position] = frame2[:, :wipe_position]


        gradient_width = 10
        if wipe_position > gradient_width and wipe_position < w - gradient_width:
            for i in range(gradient_width):
                blend_alpha = i / gradient_width
                col_pos = wipe_position - gradient_width + i
                result[:, col_pos] = cv2.addWeighted(
                    frame1[:, col_pos], 1 - blend_alpha,
                    frame2[:, col_pos], blend_alpha, 0
                )

        return result

class ZoomTransition(FilterTransition):
    def blend_frames(self, frame1, frame2, alpha):
        h, w = frame1.shape[:2]


        if alpha <= 0.5:
            normalized_alpha = alpha * 2

            scale = 1.0 - (normalized_alpha * 0.2)

            scaled_h, scaled_w = int(h * scale), int(w * scale)
            resized = cv2.resize(frame1, (scaled_w, scaled_h))

            result = np.zeros_like(frame1)

            y_offset = (h - scaled_h) // 2
            x_offset = (w - scaled_w) // 2

            result[y_offset:y_offset+scaled_h, x_offset:x_offset+scaled_w] = resized

            return result

        else:
            normalized_alpha = (alpha - 0.5) * 2

            scale = 0.8 + (normalized_alpha * 0.2)

            scaled_h, scaled_w = int(h * scale), int(w * scale)

            crop_h = min(h, int(h / scale))
            crop_w = min(w, int(w / scale))

            y_start = (h - crop_h) // 2
            x_start = (w - crop_w) // 2

            cropped = frame2[y_start:y_start+crop_h, x_start:x_start+crop_w]

            result = cv2.resize(cropped, (w, h))

            return result

class DissolveTransition(FilterTransition):
    def __init__(self, transition_time=1.0, noise_factor=0.5):
        super().__init__(transition_time)
        self.noise_factor = noise_factor
        self.noise_mask = None

    def start_transition(self, from_filter, to_filter, from_params=None, to_params=None,
                         from_custom_filter=None, to_custom_filter=None):
        super().start_transition(from_filter, to_filter, from_params, to_params,
                                from_custom_filter, to_custom_filter)
        self.noise_mask = None

    def blend_frames(self, frame1, frame2, alpha):
        h, w = frame1.shape[:2]


        if self.noise_mask is None:
            self.noise_mask = np.random.random((h, w))

        mask = self.noise_mask < alpha
        mask = np.expand_dims(mask, axis=2).repeat(3, axis=2)
        result = np.where(mask, frame2, frame1)

        return result

"""
Drawing utilities
==================
Functions to draw bounding boxes, labels, tracking IDs,
and the real-time info panel on each video frame.
"""

import cv2
import numpy as np
import time

# FPS calculation
_prev_time = time.time()
_fps_display = 0.0

def draw_boxes(frame, objects):
    """
    Draw bounding boxes with tracking ID and label for each object.

    objects: list of (x1, y1, x2, y2, track_id, label, color)
    """
    for obj in objects:
        x1, y1, x2, y2, track_id, label, color = obj
        r, g, b = color

        # Bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (r, g, b), 2)

        # Label background
        tag      = f"ID:{track_id}  {label}"
        (tw, th), baseline = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        tag_y    = max(y1 - 10, th + 10)
        tag_x1   = x1
        tag_y1   = tag_y - th - baseline
        tag_x2   = x1 + tw + 8
        tag_y2   = tag_y + baseline

        cv2.rectangle(frame, (tag_x1, tag_y1), (tag_x2, tag_y2), (r, g, b), -1)

        # Label text
        text_color = (0, 0, 0) if sum(color) > 400 else (255, 255, 255)
        cv2.putText(
            frame, tag,
            (x1 + 4, tag_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55,
            text_color, 2, cv2.LINE_AA
        )

        # Corner decorations (makes boxes look cleaner)
        length = 15
        thick  = 3
        # Top-left
        cv2.line(frame, (x1, y1), (x1 + length, y1), (255,255,255), thick)
        cv2.line(frame, (x1, y1), (x1, y1 + length), (255,255,255), thick)
        # Top-right
        cv2.line(frame, (x2, y1), (x2 - length, y1), (255,255,255), thick)
        cv2.line(frame, (x2, y1), (x2, y1 + length), (255,255,255), thick)
        # Bottom-left
        cv2.line(frame, (x1, y2), (x1 + length, y2), (255,255,255), thick)
        cv2.line(frame, (x1, y2), (x1, y2 - length), (255,255,255), thick)
        # Bottom-right
        cv2.line(frame, (x2, y2), (x2 - length, y2), (255,255,255), thick)
        cv2.line(frame, (x2, y2), (x2, y2 - length), (255,255,255), thick)

    return frame


def draw_info_panel(frame, fps, obj_count, total_ids, model_name, tracking=True):
    """
    Draw a semi-transparent info panel in the top-left corner.
    Shows FPS, object count, total unique IDs, and model name.
    """
    global _prev_time, _fps_display

    # Calculate real FPS
    now        = time.time()
    _fps_display = 1.0 / (now - _prev_time + 1e-6)
    _prev_time = now

    # Panel dimensions
    panel_w = 260
    panel_h = 115
    margin  = 10

    # Semi-transparent overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (margin, margin), (margin + panel_w, margin + panel_h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    # Panel border
    cv2.rectangle(frame, (margin, margin), (margin + panel_w, margin + panel_h), (80, 80, 80), 1)

    font  = cv2.FONT_HERSHEY_SIMPLEX
    x     = margin + 10
    lines = [
        (f"FPS:      {_fps_display:.1f}",                 (100, 220, 100)),
        (f"Objects:  {obj_count}",                        (100, 180, 255)),
        (f"Total IDs:{total_ids}",                        (255, 180, 100)),
        (f"Model:    {model_name}",                       (200, 200, 200)),
        (f"Tracking: {'SORT' if tracking else 'OFF'}",    (180, 100, 255)),
    ]

    for i, (text, color) in enumerate(lines):
        y = margin + 22 + i * 19
        cv2.putText(frame, text, (x, y), font, 0.48, color, 1, cv2.LINE_AA)

    return frame

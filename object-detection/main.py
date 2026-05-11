"""
Object Detection and Tracking
==============================
Uses YOLOv8 for detection + SORT algorithm for tracking.
Run with webcam:     python main.py
Run with video file: python main.py --source video.mp4
"""

import cv2
import argparse
import numpy as np
from ultralytics import YOLO
from tracker.sort import Sort
from utils.draw import draw_boxes, draw_info_panel


def compute_iou(boxA, boxB):
    """Compute Intersection over Union between two boxes."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    if interArea == 0:
        return 0
    boxAArea = (boxA[2]-boxA[0]) * (boxA[3]-boxA[1])
    boxBArea = (boxB[2]-boxB[0]) * (boxB[3]-boxB[1])
    return interArea / float(boxAArea + boxBArea - interArea)

# ── ARGUMENT PARSER ─────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Real-Time Object Detection & Tracking")
parser.add_argument("--source",     type=str,   default="0",   help="0=webcam, or path to video file")
parser.add_argument("--model",      type=str,   default="yolov8n.pt", help="YOLO model (yolov8n/s/m/l/x.pt)")
parser.add_argument("--conf",       type=float, default=0.4,   help="Confidence threshold (0.0 - 1.0)")
parser.add_argument("--classes",    nargs="+",  type=int,      help="Filter specific class IDs (e.g. 0 2 for person+car)")
parser.add_argument("--no-track",   action="store_true",       help="Disable tracking, detection only")
parser.add_argument("--save",       action="store_true",       help="Save output to output.mp4")
args = parser.parse_args()

# ── LOAD MODEL ──────────────────────────────────────────────────────────────
print(f"[INFO] Loading YOLO model: {args.model}")
model = YOLO(args.model)

# ── OPEN VIDEO SOURCE ────────────────────────────────────────────────────────
source = int(args.source) if args.source.isdigit() else args.source
cap    = cv2.VideoCapture(source)

if not cap.isOpened():
    print(f"[ERROR] Could not open source: {args.source}")
    exit(1)

W   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
H   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
FPS = cap.get(cv2.CAP_PROP_FPS) or 30
if FPS > 60 or FPS < 1:   # sanity check for weird sources
    FPS = 30

print(f"[INFO] Source opened — {W}x{H} @ {FPS:.0f} FPS")

# ── VIDEO WRITER (optional) ──────────────────────────────────────────────────
writer = None
if args.save:
    import os
    from datetime import datetime
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_name = os.path.splitext(os.path.basename(str(args.source)))[0]
    if args.source.isdigit():
        source_name = "webcam"
    output_name = f"{source_name}_output_{timestamp}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_name, fourcc, FPS, (W, H))
    print(f"[INFO] Saving output to {output_name}")

# ── SORT TRACKER ─────────────────────────────────────────────────────────────
tracker = Sort(max_age=30, min_hits=2, iou_threshold=0.3)

# ── CLASS COLORS (consistent per class ID) ───────────────────────────────────
rng    = np.random.default_rng(42)
COLORS = rng.integers(100, 255, size=(100, 3), dtype=int).tolist()

# ── STATS ────────────────────────────────────────────────────────────────────
frame_count   = 0
active_ids    = set()
is_fullscreen = False

# ── WINDOW SETUP ─────────────────────────────────────────────────────────────
WIN_NAME = "Object Detection & Tracking  |  Q=quit  F=fullscreen"
cv2.namedWindow(WIN_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WIN_NAME, 960, 540)

def fit_frame(frame, target_w, target_h):
    """Resize frame keeping aspect ratio, pad with black bars."""
    h, w   = frame.shape[:2]
    scale  = min(target_w / w, target_h / h)
    new_w  = int(w * scale)
    new_h  = int(h * scale)
    resized = cv2.resize(frame, (new_w, new_h))
    canvas  = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    x_off   = (target_w - new_w) // 2
    y_off   = (target_h - new_h) // 2
    canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized
    return canvas

print("[INFO] Starting detection... Press Q to quit | F to toggle fullscreen")

while True:
    ret, frame = cap.read()
    if not ret:
        print("[INFO] End of stream.")
        break

    frame_count += 1

    # ── YOLO DETECTION ──────────────────────────────────────────────────────
    results = model(
        frame,
        conf=args.conf,
        classes=args.classes,
        verbose=False
    )[0]

    detections = []   # [x1, y1, x2, y2, conf, class_id]

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf     = float(box.conf[0])
        class_id = int(box.cls[0])
        detections.append([x1, y1, x2, y2, conf, class_id])

    # ── SORT TRACKING ────────────────────────────────────────────────────────
    tracked_objects = []

    if not args.no_track and len(detections) > 0:
        # SORT needs [x1, y1, x2, y2, score]
        dets_for_sort = np.array([[d[0], d[1], d[2], d[3], d[4]] for d in detections])
        tracked       = tracker.update(dets_for_sort)

        # Match tracked boxes back to class IDs
        for trk in tracked:
            x1, y1, x2, y2, track_id = map(int, trk)
            # Find best matching detection for class label
            class_id = 0
            best_iou  = 0
            for det in detections:
                iou = compute_iou([x1,y1,x2,y2], det[:4])
                if iou > best_iou:
                    best_iou = iou
                    class_id = det[5]

            label    = model.names[class_id]
            color    = COLORS[class_id % len(COLORS)]
            tracked_objects.append((x1, y1, x2, y2, track_id, label, color))
            active_ids.add(track_id)

    elif args.no_track:
        # Detection only — no tracking IDs
        for i, det in enumerate(detections):
            x1, y1, x2, y2, conf, class_id = det
            label = model.names[class_id]
            color = COLORS[class_id % len(COLORS)]
            tracked_objects.append((x1, y1, x2, y2, i+1, label, color))

    # ── DRAW ────────────────────────────────────────────────────────────────
    frame = draw_boxes(frame, tracked_objects)
    frame = draw_info_panel(
        frame,
        fps=frame_count,
        obj_count=len(tracked_objects),
        total_ids=len(active_ids),
        model_name=args.model,
        tracking=not args.no_track
    )

    # ── SHOW ────────────────────────────────────────────────────────────────
    if is_fullscreen:
        display = fit_frame(frame, 1920, 1080)
    else:
        display = fit_frame(frame, 960, 540)

    cv2.imshow(WIN_NAME, display)

    if writer:
        writer.write(frame)

    key = cv2.waitKey(int(1000 / FPS)) & 0xFF
    if key == ord("q"):
        print("[INFO] Quit signal received.")
        break
    elif key == ord("f"):
        is_fullscreen = not is_fullscreen
        if is_fullscreen:
            cv2.setWindowProperty(WIN_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty(WIN_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WIN_NAME, 960, 540)

# ── CLEANUP ──────────────────────────────────────────────────────────────────
cap.release()
if writer:
    writer.release()
cv2.destroyAllWindows()
print(f"[INFO] Done. Processed {frame_count} frames. Total unique IDs: {len(active_ids)}")
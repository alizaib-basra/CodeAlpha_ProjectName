# 🎯 Real-Time Object Detection & Tracking

A Python project that uses **YOLOv8** for object detection and the **SORT algorithm** for real-time multi-object tracking via webcam or video file.

## ✨ Features

- ✅ Real-time object detection using YOLOv8
- ✅ Multi-object tracking with SORT (Kalman Filter + Hungarian Algorithm)
- ✅ Unique tracking IDs per object across frames
- ✅ Bounding boxes with labels and tracking IDs
- ✅ Live info panel (FPS, object count, total IDs)
- ✅ Works with webcam or any video file
- ✅ Optional save output to video file
- ✅ Filter specific object classes

## 📁 Project Structure

```
object-detection/
│
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md
│
├── tracker/
│   ├── __init__.py
│   └── sort.py             # SORT tracking algorithm
│
└── utils/
    ├── __init__.py
    └── draw.py             # Drawing bounding boxes & info panel
```

## 🚀 Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/object-detection.git
cd object-detection
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run with webcam
```bash
python main.py
```

### 4. Run with a video file
```bash
python main.py --source video.mp4
```

### 5. Save output to file
```bash
python main.py --save
```

## ⚙️ Command-Line Options

| Argument | Default | Description |
|---|---|---|
| `--source` | `0` | `0` = webcam, or path to video file |
| `--model` | `yolov8n.pt` | YOLO model size (n/s/m/l/x) |
| `--conf` | `0.4` | Detection confidence threshold |
| `--classes` | all | Filter class IDs (e.g. `--classes 0 2` for person+car) |
| `--no-track` | off | Disable tracking (detection only) |
| `--save` | off | Save output to `output.mp4` |

## 📦 YOLO Model Sizes

| Model | Speed | Accuracy |
|---|---|---|
| `yolov8n.pt` | ⚡ Fastest | Lower |
| `yolov8s.pt` | Fast | Good |
| `yolov8m.pt` | Medium | Better |
| `yolov8l.pt` | Slow | High |
| `yolov8x.pt` | Slowest | Highest |

> Models download automatically on first run.

## 🔧 Common Class IDs (COCO dataset)

| ID | Class | ID | Class |
|---|---|---|---|
| 0 | person | 7 | truck |
| 1 | bicycle | 14 | bird |
| 2 | car | 15 | cat |
| 3 | motorcycle | 16 | dog |
| 5 | bus | 62 | laptop |

## 🛠️ Built With

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [OpenCV](https://opencv.org/)
- [SORT Algorithm](https://arxiv.org/abs/1602.00763)
- [FilterPy](https://github.com/rlabbe/filterpy) (Kalman Filter)
- [SciPy](https://scipy.org/) (Hungarian algorithm)

## 📄 License

MIT

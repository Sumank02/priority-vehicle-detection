import os
import cv2
from typing import Optional

_MODEL = None


def _find_custom_model() -> Optional[str]:
    """Look for a custom YOLO model in Traffic_Monitoring folder (e.g., best.pt)."""
    candidates = [
        os.path.join('Traffic_Monitoring', 'best.pt'),
        os.path.join('Traffic_Monitoring', 'runs', 'detect', 'train', 'weights', 'best.pt'),
        os.path.join('Traffic_Monitoring', 'weights', 'best.pt'),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    try:
        from ultralytics import YOLO
    except Exception as e:
        raise RuntimeError("Ultralytics not installed. Please install 'ultralytics'.") from e

    custom = _find_custom_model()
    weights = custom if custom else 'yolov8n.pt'
    _MODEL = YOLO(weights)
    return _MODEL


def _is_priority_vehicle(name: str) -> bool:
    if not name:
        return False
    n = name.lower()
    # Accept common labels for emergency vehicles
    keywords = [
        'ambul',            # ambulance, ambulance_on, ambulance_off
        'firetruck', 'fire_truck', 'fire-truck', 'fire engine', 'fire_engine',
        'police', 'policecar', 'police_car', 'police-car'
    ]
    return any(k in n for k in keywords)


def _allowed_class_ids(model) -> list:
    """Return class ids from the model whose names match priority vehicle keywords."""
    names = None
    if hasattr(model, 'model') and hasattr(model.model, 'names'):
        names = model.model.names
    else:
        names = getattr(model, 'names', None)
    if not names:
        return []
    allowed = []
    # names can be dict {id: name}
    for cid, cname in (names.items() if isinstance(names, dict) else enumerate(names)):
        if _is_priority_vehicle(str(cname)):
            allowed.append(int(cid))
    return allowed


def _draw_labelled_box(img, x1, y1, x2, y2, label='Detected Vehicle', color=(0, 255, 0)):
    h, w = img.shape[:2]
    # Scale thickness and font by image size for clarity
    base = max(1, min(w, h))
    thickness = max(2, base // 150)         # thicker boxes on larger images
    font_scale = max(0.7, base / 700.0)     # larger text on larger images
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Draw bounding box
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

    # Measure text and draw solid background for readability
    (tw, th), baseline = cv2.getTextSize(label, font, font_scale, thickness)
    tx1, ty1 = x1, max(0, y1 - th - baseline - 6)
    tx2, ty2 = x1 + tw + 10, y1
    cv2.rectangle(img, (tx1, ty1), (tx2, ty2), (0, 0, 0), -1)  # black background
    cv2.putText(img, label, (x1 + 5, y1 - 6), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)


def annotate_image(input_path: str, output_path: str) -> None:
    img = cv2.imread(input_path)
    if img is None:
        raise RuntimeError(f"Could not read image: {input_path}")
    model = _load_model()
    allowed = _allowed_class_ids(model)
    res = model.predict(source=img, imgsz=640, conf=0.6, iou=0.45, classes=allowed if allowed else None, verbose=False)[0]
    # Draw detections
    if res.boxes is not None and len(res.boxes) > 0:
        names = model.model.names if hasattr(model, 'model') else getattr(model, 'names', {})
        for b in res.boxes:
            xyxy = b.xyxy[0].tolist()
            x1, y1, x2, y2 = map(int, xyxy)
            cls_id = int(b.cls.item()) if b.cls is not None else -1
            conf = float(b.conf.item()) if b.conf is not None else 0.0
            cls_name = names.get(cls_id, str(cls_id))
            if not _is_priority_vehicle(cls_name):
                continue
            # Filter tiny boxes (likely false positives)
            h, w = img.shape[:2]
            box_area = max(0, (x2 - x1)) * max(0, (y2 - y1))
            if box_area < 0.005 * (w * h):  # <0.5% of image area
                continue
            label = f"{cls_name} {conf:.2f}"
            _draw_labelled_box(img, x1, y1, x2, y2, label)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)


def annotate_video(input_path: str, output_path: str) -> None:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {input_path}")

    # Write H.264/MP4 for better browser compatibility
    # If H.264 is unavailable in your OpenCV build, fallback to MP4V
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1:
        fps = 20.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    if not out.isOpened():
        # fallback to mp4v if avc1 not available
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    model = _load_model()
    names = model.model.names if hasattr(model, 'model') else getattr(model, 'names', {})
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        allowed = _allowed_class_ids(model)
        res = model.predict(source=frame, imgsz=640, conf=0.6, iou=0.45, classes=allowed if allowed else None, verbose=False)[0]
        if res.boxes is not None and len(res.boxes) > 0:
            for b in res.boxes:
                xyxy = b.xyxy[0].tolist()
                x1, y1, x2, y2 = map(int, xyxy)
                cls_id = int(b.cls.item()) if b.cls is not None else -1
                conf = float(b.conf.item()) if b.conf is not None else 0.0
                cls_name = names.get(cls_id, str(cls_id))
                if not _is_priority_vehicle(cls_name):
                    continue
                # Filter tiny boxes
                box_area = max(0, (x2 - x1)) * max(0, (y2 - y1))
                if box_area < 0.005 * (w * h):
                    continue
                label = f"{cls_name} {conf:.2f}"
                _draw_labelled_box(frame, x1, y1, x2, y2, label)
        out.write(frame)
        frame_idx += 1

    out.release()
    cap.release()

    cap.release()
    out.release()



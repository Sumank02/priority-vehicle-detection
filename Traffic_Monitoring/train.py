from ultralytics import YOLO
model = YOLO('yolov5n.pt')
model.train(data='dataset/data.yaml', epochs=50, imgsz=320)

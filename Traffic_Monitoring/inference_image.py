import cv2
from ultralytics import YOLO

model_path = "runs/detect/train/weights/best.pt"
input_path = "test_resources/test1.jpg"
output_path = "test_resources/test1_output.jpg"

model = YOLO(model_path)

results = model(input_path)
annotated = results[0].plot()

cv2.imwrite(output_path, annotated)
print(f"Saved result as: {output_path}")

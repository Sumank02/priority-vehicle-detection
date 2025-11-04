from ultralytics import YOLO
import cv2

model = YOLO("runs/detect/train/weights/best.pt")
video_path = "test_resource/ambulance_driveby.mp4"
cap = cv2.VideoCapture(video_path)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('test_resource/output.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS), 
                      (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                       int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Done!")
        break

    results = model(frame, verbose=False)

    annotated_frame = results[0].plot()

    out.write(annotated_frame)

cap.release()
out.release()
cv2.destroyAllWindows()

from ultralytics import YOLO

model = YOLO("yolo11m.pt")

# Fixed the syntax errors and corrected the argument names
model.train(data="dataset_custom.yaml", imgsz=640, batch=8, epochs=2, workers=1, device="cpu")

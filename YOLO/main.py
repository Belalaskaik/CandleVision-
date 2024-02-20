from ultralytics import YOLO

# Load a model
model = YOLO("yolov8.yaml") # build a new model from scratch

# Use the model
results = model.train(data="config.yaml", epochs=1) # train the model


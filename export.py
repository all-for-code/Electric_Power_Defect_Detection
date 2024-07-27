from ultralytics import YOLO

model = YOLO("train/1226_48_1024_l_240b_100e/weights/best.pt")  # load a pretrained model (recommended for training)

model.export(format="engine", device=0, imgsz = 1024, half=True, batch=8)  #  export the model to ONNX format
'''
model = YOLO("weights/yolov8l_cls_256_bjbp/weights/best.pt")  # load a pretrained model (recommended for training)

model.export(format="engine",device=1, half=True)  #  export the model to ONNX format

model = YOLO("weights/yolov8l_cls_256_bjds3/weights/best.pt")  # load a pretrained model (recommended for training)

model.export(format="engine",device=1, half=True)  #  export the model to ONNX format

model = YOLO("weights/yolov8l_cls_256_fhz/weights/best.pt")  # load a pretrained model (recommended for training)

model.export(format="engine",device=1, half=True)  #  export the model to ONNX format

model = YOLO("weights/yolov8l_cls_256_gcc/weights/best.pt")  # load a pretrained model (recommended for training)

model.export(format="engine",device=1, half=True)  #  export the model to ONNX format

model = YOLO("weights/yolov8l_cls_256_hxq_gj/weights/best.pt")  # load a pretrained model (recommended for training)

model.export(format="engine",device=1, half=True)  #  export the model to ONNX format

model = YOLO("weights/yolov8l_cls_256_hxq_gjt/weights/best.pt")  # load a pretrained model (recommended for training)

model.export(format="engine",device=1, half=True)  #  export the model to ONNX format

model = YOLO("weights/yolov8l_cls_256_ywzt/weights/best.pt")  # load a pretrained model (recommended for training)

model.export(format="engine",device=1, half=True)  #  export the model to ONNX format
'''

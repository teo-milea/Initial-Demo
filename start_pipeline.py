import argparse
import cv2

from yolo import YOLO
from control import control_interface, init_interface, reset_object
import tensorflow as tf
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('-n', '--network', default="normal", help='Network Type: normal / tiny / prn')
ap.add_argument('-d', '--device', default=0, help='Device to use')
ap.add_argument('-s', '--size', default=416, help='Size for yolo')
ap.add_argument('-c', '--confidence', default=0.2, help='Confidence for yolo')
ap.add_argument('-p', '--port', default=10000, help='Port for Bleder')
args = ap.parse_args()

if args.network == "normal":
    print("loading yolo...")
    yolo = YOLO("models/cross-hands.cfg", "models/cross-hands.weights", ["hand"])
elif args.network == "prn":
    print("loading yolo-tiny-prn...")
    yolo = YOLO("models/cross-hands-tiny-prn.cfg", "models/cross-hands-tiny-prn.weights", ["hand"])
elif args.network == "tiny":
    print("loading yolo-tiny...")
    yolo = YOLO("models/cross-hands-tiny.cfg", "models/cross-hands-tiny.weights", ["hand"])
else:
    print('ERROR NETWORK ARGUMENT INVALID')
    exit()

physical_devices = tf.config.experimental.list_physical_devices('GPU') 
for physical_device in physical_devices: 
    tf.config.experimental.set_memory_growth(physical_device, True)



yolo.size = int(args.size)
yolo.confidence = float(args.confidence)

classifier = tf.keras.models.load_model("./resnet_v2_50_1")

port = int(args.port)
init_interface(port)

print("starting webcam...")
cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

labels = ['fist', 'ok', 'palm', 'thumb down', 'thumb up']

if vc.isOpened():  # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    width, height, inference_time, results = yolo.inference(frame)
    # print(width, height)
    for detection in results:
        id, name, confidence, x, y, w, h = detection
        
        # draw a bounding box rectangle and label on the image
        color = (0, 255, 0)
        # print(x, y)
        width_margin = int(width / 10)
        height_margin = int(height / 10)
        seg = frame[max(y - height_margin,0):y+h + height_margin, max(x - width_margin,0):x+w + width_margin]
        cv2.imshow('seg', seg)

        resize = cv2.resize(seg, dsize=(224,224))
        batch_img = np.expand_dims(cv2.cvtColor(resize, cv2.COLOR_BGR2RGB)/255, axis=0)
        scores = classifier.predict(batch_img)


        label = labels[np.argmax(scores)]
        # print(label)

        control_interface(x, y, w, h, width, height, label)


        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        text = "%s (%s)" % (label, round(confidence, 2))
        cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, color, 2)

    cv2.imshow("preview", frame)

    rval, frame = vc.read()

    key = cv2.waitKey(20)
    if key == 27:  # exit on ESC
        break
    if key == ord('r'):
        reset_object()


cv2.destroyWindow("preview")
vc.release()

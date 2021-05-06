from imutils.video import VideoStream
import face_recognition
import imutils
import pickle
import time
import cv2
import numpy as np
import requests
import base64
import threading
import merger
from datetime import datetime
from register import config

cascade = "haarcascade.xml"
encodes = "encodings.pickle"
display = 1

name_counter = ""
current_id = ""
detected = False
img = np.zeros((1080, 1920, 3), np.uint8)

print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodes, "rb").read())
detector = cv2.CascadeClassifier(cascade)


print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()

r = requests.get("http://{}/sendreq/get-names?admin={}&password={}".format(config.site, config.admin, config.password))
dict_names = r.json()

time.sleep(2.0)


def send_request(url, data):
    r = requests.post(url, data=data)
    f = open("error.html",  "w+", encoding="utf-8")
    f.write(r.text)


while True:
    frame = vs.read()
    img[:] = (0, 0, 0)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                                      minNeighbors=5, minSize=(30, 30),
                                      flags=cv2.CASCADE_SCALE_IMAGE)

    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []
    output = "Look at the camera!"

    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"],
                                                 encoding)
        name = "Unknown"

        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            name = max(counts, key=counts.get)
            if name_counter == 0 and current_id == "":
                current_id = name
                detected = False

        names.append(name)
        if current_id in names:
            name_counter += 1
        else:
            name_counter = 0
            current_id = ""

        if current_id != "":
            current_name = dict_names[current_id]

        if name_counter > 5:
            if not detected:
                now = datetime.now()
                print(current_name + " has been detected!" + str(now))
                retval, buffer = cv2.imencode('.jpg', frame)
                base_image = base64.b64encode(buffer)
                post_name = current_id + " " + \
                    now.strftime("%d-%m-%Y_%H-%M-%S") + ".jpg"
                post_data = {'admin': config.admin, "password": config.password,
                             "id": current_id, "name": post_name, "image": base_image}
                url = "http://"+config.site+"/sendreq/register-face"
                threading.Thread(target=send_request,
                                 args=(url, post_data,)).start()
                detected = True
            img[:] = (21, 156, 84)
            output = str.title(current_name) + " has been detected!"

        elif name_counter > 0:
            img[:] = (4, 187, 255)
            output = "Detecting : " + str.title(current_name) + "!"

    font = cv2.FONT_HERSHEY_SIMPLEX
    text = output

    textsize = cv2.getTextSize(text, font, 2.5, 8)[0]

    textX = int((img.shape[1] - textsize[0]) / 2)
    textY = int((img.shape[0] + textsize[1]) / 2)

    cv2.putText(img, text, (textX, textY), font, 2.5, (255, 255, 255), 8)

    if display > 0:
        cv2.namedWindow('Frame', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(
            'Frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Frame", img)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

cv2.destroyAllWindows()
vs.stop()

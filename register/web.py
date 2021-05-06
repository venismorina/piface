# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

# import the necessary packages
#from pyimagesearch.motion_detection import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template, redirect, session, url_for

import threading
import argparse
import datetime
import imutils
import time
import cv2
import dlib
import numpy as np
import math
import os
from imutils import paths
import face_recognition
import pickle
import html
import sys
from subprocess import Popen, PIPE, STDOUT, DEVNULL
from textwrap import dedent
import shutil
import config

from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import requests


# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful for multiple browsers/tabs
# are viewing tthe stream)

lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)
app.config['SECRET_KEY'] = 'pie'


detector = cv2.CascadeClassifier("haarcascade.xml")

path = ""


class LoginForm(FlaskForm):
    name = StringField('Emri')
    myChoices = [
        ('1', 'Prishtine'),
        ('2', 'Drenas'),
        ('3', 'Ferizaj'),
    ]
    place = SelectField("Vendpunimi", choices=myChoices)
    submit = SubmitField('Submit')


# initialize the video stream and allow the camera sensor to
# warmup
vs = VideoStream(src=0).stop()


@app.route("/", methods=['GET', 'POST'])
def index():
    global path
    try:
        vs.stop()
    except Exception as e:
        print(e)
    # return the rendered template
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        place = form.place.data
        url = "http://{}/sendreq/register-user?name={}&place={}&admin={}&password={}".format(
            config.site, name, place, config.admin, config.password)
        r = requests.get(url)
        path = r.text
        try:
            print(os.getcwd())
            os.mkdir("../dataset/images/"+path)
        except Exception as e:
            print(os.getcwd())
            print(e)
        return redirect("/cam")
    return render_template("index.html", title="Home", form=form)


@app.route("/cam", methods=['GET', 'POST'])
def cam():
    return render_template("cam.html", title='Cam')


def generate(vs, data, dict):

    skip = data['skip']
    i = data['i']

    while True:
        frame = vs.read()

        skip += 1
        i += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        gray2 = cv2.filter2D(frame, -1, kernel)

        rects = detector.detectMultiScale(gray, scaleFactor=1.1,
                                      minNeighbors=5, minSize=(30, 30),
                                      flags=cv2.CASCADE_SCALE_IMAGE)
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        for (top, right, bottom, left) in boxes:
		# draw the predicted face name on the image
            x = left - 20
            y = top - 40
            w = right - x + 10
            h = bottom - y + 20
            # cv2.rectangle(frame,(x,y),(w + x,h +y),(0,255,0),3)

            crop_img = frame[y:y+h, x:x+w]

            if skip > 40:
                cv2.imwrite("../dataset/images/"+path+"/"+str(i)+".jpg", crop_img)
                dict -= 1
                skip = 0

        # grab the current timestamp and draw it on the frame
        timestamp = datetime.datetime.now()
        cv2.putText(frame, str(dict), (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

        # if the total number of frames has reached a sufficient
        # number to construct a reasonable background model, then
        # continue to process the frame

        if dict < 1:
            vs.stop()
            break
        # update the background model and increment the total number
        # of frames read thus far

        # acquire the lock, set the output frame, and release the
        # lock
        (flag, encodedImage) = cv2.imencode(".jpg", frame)

        if not flag:
            continue

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    global vs
    vs = VideoStream(src=0).start()
    i = 0
    skip = 0
    dict = 15
    direction = "None"
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(vs, {'skip': skip, 'i': i, 'direction': direction}, dict), mimetype="multipart/x-mixed-replace; boundary=frame")


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, default="127.0.0.1",
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, default="5000",
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    # start a thread that will perform motion detection

    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)

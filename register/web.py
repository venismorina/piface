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
import glob

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
video_done = False


class LoginForm(FlaskForm):
    name = StringField('Emri dhe Mbiemri')
    myChoices = [
        ('1', 'Prishtinë'),
        ('2', 'Drenas'),
        ('3', 'Skenderaj')
    ]
    place = SelectField("Vendpunimi", choices=myChoices)
    submit = SubmitField('Regjistro')


vs = VideoStream(src=0).stop()


@app.route("/", methods=['GET', 'POST'])
def index():
    global path
    try:
        vs.stop()
    except Exception as e:
        print(e)
    form = LoginForm()
    # encode = len(os.walk("../dataset/images")) > 0
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
            x = left - 20
            y = top - 40
            w = right - x + 10
            h = bottom - y + 20

            crop_img = frame[y:y+h, x:x+w]

            if skip > 25:
                cv2.imwrite("../dataset/images/"+path +
                            "/"+str(i)+".jpg", crop_img)
                dict -= 1
                skip = 0

        timestamp = datetime.datetime.now()
        cv2.putText(frame, str(dict), (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 123, 0), 1)

        if dict < 1:
            vs.stop()
            break

        (flag, encodedImage) = cv2.imencode(".jpg", frame)

        if not flag:
            continue

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedImage) + b'\r\n')


def g():
    now = datetime.datetime.now()

    yield """
    <!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta name="author" content="Kodinger">
	<meta name="viewport" content="width=device-width,initial-scale=1">
	<title>My Login Page</title>
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
	<link rel="stylesheet" type="text/css" href="/static/css/my-login.css">
    <style>
/* width */
::-webkit-scrollbar {
  width: 8px;
}

/* Track */
::-webkit-scrollbar-track {
  border-radius: 10px;
}
 
/* Handle */
::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.3);
  opacity: 0.2; 
  border-radius: 10px;
}

/* Handle on hover */
::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.5);
}

code {
    color: rgb(65,157,255)
}
</style>
</head>

<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
	<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
	<script>
    function bottom(){
        var console = document.querySelector('#console');
    console.scrollTop = console.scrollHeight - console.clientHeight;
    }
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.28.0/feather.min.js" integrity="sha512-7x3zila4t2qNycrtZ31HO0NnJr8kg2VI67YLoRSyi9hGhRN66FHYWr7Axa9Y1J9tGYHVBPqIjSE1ogHrJTz51g==" crossorigin="anonymous"></script>
	
<body class="my-login-page">
	<section class="h-100">
		<div class="container h-100">
			<div class="row justify-content-md-center" style="padding-top: 100px;">
				
					<div class="card fat pb-5 px-4" >
						<div class="card-body">
							<div class="card-wrapper-lg">
                <a href="/" style="width: 120px;" class="btn btn-primary btn-block mb-4"><i width="18px" data-feather="home"></i></span> Shtëpia</a>
                <script>
  feather.replace()
</script>
               <div id="console" style="overflow: auto;background-color: #1d1e1f;height: 400px;padding: 20px;border-radius: 15px;" id="content">
               """
    for i in os.walk("../dataset/images"):
        for path in i[1]:

            url = 'http://{}/sendreq/get-name?id={}&admin={}&password={}'.format(
                config.site, path, config.admin, config.password)
            r = requests.get(url)

            dataset = "..\\dataset\\images\\" + path
            encodes = "../dataset/pickles/{}({}).pickle".format(path, r.text)
            method = "cnn"

            yield "<code>"
            yield("[MESAZH] duke u procesuar {}({}) ...".format(path, r.text))
            yield "</code><br>"
            yield "<script>bottom();</script>"

            yield "<code>"
            yield("[MESAZH] duke i numëruar fytyrat...")
            yield "</code><br>"
            yield "<script>bottom();</script>"

            imagePaths = list(paths.list_images(dataset))

            knownEncodings = []
            knownNames = []

            for (i, imagePath) in enumerate(imagePaths):

                yield "<code>"
                yield("[MESAZH] duke procesuar foton {}/{}".format(i + 1,
                                                             len(imagePaths)))
                yield "</code><br>"
                yield "<script>bottom();</script>"

                name = imagePath.split(os.path.sep)[-2]

                image = cv2.imread(imagePath)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                boxes = face_recognition.face_locations(rgb,
                                                        model=method)

                encodings = face_recognition.face_encodings(rgb, boxes)

                for encoding in encodings:
                    knownEncodings.append(encoding)
                    knownNames.append(name)

            yield "<code>"
            yield("[MESAZH] duke i renditur enkodimet...")
            yield "</code><br>"
            yield "<script>bottom();</script>"

            data = {"encodings": knownEncodings, "names": knownNames}
            f = open(encodes, "wb")
            f.write(pickle.dumps(data))
            f.close()

            yield "<code>"
            yield("[MESAZH] {} përfundoi!".format(path))
            yield "</code><br>"
            yield "<script>bottom();</script>"

            shutil.rmtree("../dataset/images/{}".format(path))

            yield("\n")

    def dict_append(dict, dict1):
        for i, j in dict.items():
            dict[i] += dict1[i]
        return dict

    main = {"pickle": [], "encodings": [], 'names': []}

    yield "<code>"
    yield("[MESAZH] duke i bashkuar enkodimet...")
    yield "</code><br>"
    yield "<script>bottom();</script>"

    for i in glob.glob("../dataset/pickles/*.pickle"):
        data = pickle.loads(open(i, "rb").read())
        data['pickle'] = [i]
        dict_append(main,data)

    yield "<code>"
    yield("[MESAZH] enkodimet u bashkuan.")
    yield "</code><br>"
    yield "<script>bottom();</script>"

    f = open("encodings.pickle", "wb")
    f.write(pickle.dumps(main))
    f.close()
    f = open("encodings1.pickle", "wb")
    f.write(pickle.dumps(main))
    f.close()
    
    dt_string = now.strftime("%d-%m-%Y %H %M %S")
    shutil.move('encodings1.pickle',
                '../dataset/backup/encodings{}.pickle'.format(dt_string))

    r = requests.post('http://{}/sendreq/upload-encodings'.format(config.site), data={"title" : 'encodings{}'.format(dt_string)} ,files={'file': open("encodings.pickle", 'rb')})
    print(r)
    yield "<code>"
    yield("[MESAZH] enkodimet u derguan në databazë.")
    yield "</code><br>"
    yield "<script>bottom();</script>"


@app.route("/encode")
def encode():
    try:
        vs.stop()
    except Exception as e:
        print(e)
    return Response(g(), mimetype='text/html')


@app.route("/video_feed")
def video_feed():
    global vs, video_done
    vs = VideoStream(src=0).start()
    i = 0
    skip = 0
    dict = 15
    direction = "None"
    return Response(generate(vs, {'skip': skip, 'i': i, 'direction': direction}, dict), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, default="127.0.0.1",
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, default="5000",
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)

from imutils import paths
import face_recognition
import pickle
import cv2
import os
import requests
import shutil
from register import config


for i in os.walk("dataset/images"):
	for path in i[1]:
		
		url = 'http://{}/sendreq/get-name?id={}&admin={}&password={}'.format(config.site, path, config.admin, config.password)
		r = requests.get(url)

		dataset = "dataset\\images\\" + path
		encodes = "dataset/pickles/{}({}).pickle".format(path,r.text)
		method = "hog"

		print("[INFO] Encoding {}({}) ...".format(path,r.text))

		print("[INFO] quantifying faces...")
		imagePaths = list(paths.list_images(dataset))

		knownEncodings = []
		knownNames = []

		for (i, imagePath) in enumerate(imagePaths):

			print("[INFO] processing image {}/{}".format(i + 1,
				len(imagePaths)))
			name = imagePath.split(os.path.sep)[-2]

			image = cv2.imread(imagePath)
			rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

			boxes = face_recognition.face_locations(rgb,
				model=method)

			encodings = face_recognition.face_encodings(rgb, boxes)

			for encoding in encodings:
				knownEncodings.append(encoding)
				knownNames.append(name)

		print("[INFO] serializing encodings...")
		data = {"encodings": knownEncodings, "names": knownNames}
		f = open(encodes, "wb")
		f.write(pickle.dumps(data))
		f.close()

		print("[INFO] ({}) Done!...".format(path))

		shutil.rmtree("dataset/images/{}".format(path))

		print("[INFO] Successfully deleted images/{}...".format(path))

		print("\n")

import merger
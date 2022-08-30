#source: https://www.youtube.com/watch?v=PmZ29Vta7Vc&list=PLptyD7Up77t9GmbgvuVZ8eDK6clCgXrmt&index=50&t=759s&ab_channel=CodingEntrepreneurs
import os
import cv2
from PIL import Image
from PIL.Image import Resampling
import numpy as np
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
img_dir = os.path.join(BASE_DIR, "images")

face_cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_alt2.xml')
#source:  https://www.google.com/search?q=lLBPH&oq=lLBPH&aqs=chrome..69i57j0i433i512j0i512j0i131i433i512j46i131i199i433i465i512j0i131i433i512j0i433i512l2j0i10i512j0i512.5293j0j7&sourceid=chrome&ie=UTF-8
recogniser = cv2.face.LBPHFaceRecognizer_create()

current_id = 0
label_ids = {}
y_labels = []
x_train = []

for root, dirs, files in os.walk(img_dir):
    for file in files:
        if file.endswith("png") or file.endswith("jpeg"):
            path = os.path.join(root, file)
            label = os.path.basename(os.path.dirname(path)).replace(" ", "-").lower()
            #print("Label:", label,"Path:", path)
            if not label in label_ids:
                label_ids[label] = current_id
                current_id+=1

            id_ = label_ids[label]

            #use numbers for labelling
            #verify images, convert to greyscale and then turn them into numpy arrays
            pil_img = Image.open(path).convert("L")# converts image to grayscale
            
            #resize all images before training for consistency
            
            #size = 550,550
            #final_img = pil_img.resize(size,Resampling.LANCZOS)
            img_array = np.array(pil_img, "uint8")# convert to numpy array

            faces = face_cascade.detectMultiScale(img_array,scaleFactor=1.5,minNeighbors=5)

            for (x,y,w,h) in faces:
                roi = img_array[y:y+h,x:x+w]
                x_train.append(roi)
                y_labels.append(id_)

with open("labels.pickle", "wb") as f:
    pickle.dump(label_ids,f)

recogniser.train(x_train,np.array(y_labels))
recogniser.save("trainer.yml")
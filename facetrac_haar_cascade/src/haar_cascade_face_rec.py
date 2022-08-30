#source: https://www.youtube.com/watch?v=PmZ29Vta7Vc&list=PLptyD7Up77t9GmbgvuVZ8eDK6clCgXrmt&index=50&t=759s&ab_channel=CodingEntrepreneurs
import cv2
import pickle
face_cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_alt2.xml')

recogniser = cv2.face.LBPHFaceRecognizer_create()
recogniser.read("trainer.yml")

labels = {}
with open("labels.pickle", "rb") as f:
    og_labels = pickle.load(f)
    #invert labels and id
    labels = {v:k for k,v in og_labels.items()}

cap = cv2.VideoCapture(0)

print(cv2.__file__)
while(True):
    ret,frame = cap.read()
    grey = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(grey,scaleFactor=1.5,minNeighbors=5)
    for(x,y,w,h) in faces:
        #print(x,y,w,h)
        roi_gray = grey[y:y+h, x:x+h]
        roi_color = frame[y:y+h, x:x+h] #(coord1-height, coord2-height)
        
        #Recogniser predict region of interest in gray faces
        id_, conf = recogniser.predict(roi_gray)
        print(labels[id_],conf)
        font = cv2.FONT_HERSHEY_SIMPLEX
        name = labels[id_]
        color = (255,255,255)
        stroke = 2

        cv2.putText(frame,name+" "+str(conf),(x,y),font,1,color,stroke,cv2.LINE_AA)
        img_item = "my-image.png"
        cv2.imwrite(img_item,roi_gray)

        color = (255,0,0) #BGR line color
        stroke = 2 #line thickness
        end_cord_x = x+w
        end_cord_y = y+h
        cv2.rectangle(frame, (x,y),(end_cord_x,end_cord_y), color, stroke)
    #Display resulting frame 
    cv2.imshow('frame',frame)
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
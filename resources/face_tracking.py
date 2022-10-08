#Source: https://www.youtube.com/watch?v=P2wl3N2JW9c
from djitellopy import Tello
import numpy as np
import cv2
#additions for detection with svm
import face_recognition
#additions for detection with haar_cascade
import os
import pickle

#HAARCASCADE DEPENDENCIES
facecascade = cv2.CascadeClassifier('/home/thinkpad/Desktop/Tello_ai_with_face_recognition/resources/cascades/haarcascade_frontalface_alt2.xml')
recogniser = cv2.face.LBPHFaceRecognizer_create()
recogniser.read("/home/thinkpad/Desktop/Tello_ai_with_face_recognition/resources/trainer.yml")
labels = {}
with open("/home/thinkpad/Desktop/Tello_ai_with_face_recognition/resources/labels.pickle", "rb") as f:
    og_labels = pickle.load(f)
    #invert labels and id
    labels = {v:k for k,v in og_labels.items()}
#YOLO DEPENDENCIES
net = cv2.dnn.readNetFromDarknet("/home/thinkpad/Desktop/Tello_ai_with_face_recognition/facetrac_yolo/src/yolov3_custom.cfg","/home/thinkpad/Desktop/Tello_ai_with_face_recognition/facetrac_yolo/src/backup/yolov3_custom_6000.weights")
# Change here for custom classes for trained model this is really important because if the names are not in the correct order it will appear like improper classification
classes = ['Dog','Barak Obama','Stephen','Jack Sparrow']


def initialisetello():
    tello = Tello()

    tello.connect()
    #set velocities to zero, can be between -100~100
    tello.for_back_velocity = 0
    tello.left_right_velocity = 0
    tello.up_down_velocity = 0
    tello.yaw_velocity = 0 
    tello.speed = 10

    tello.set_speed(tello.speed)
    print("Tello battery at ",tello.get_battery(),"%")
    tello.streamoff()
    tello.streamon()

    return tello

def telloGetFrame(tello, w, h):
    tello_cam = tello.get_frame_read()
    tello_cam = tello_cam.frame
    img = cv2.resize(tello_cam,(w,h))
    return img

################################################################HAAR_CASCADE######################################################
def findfacehaar(img):

    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = facecascade.detectMultiScale(image=imgGray, scaleFactor=1.2, minNeighbors=8)#scale and minimum factor
    
    facecoords = []
    facecoordsArea = []

    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        cx = x + w//2 
        cy = y + h //2
        area = w*h
        roi_gray = imgGray[y:y+h, x:x+h]
        roi_color = img[y:y+h, x:x+h] #(coord1-height, coord2-height)
        #Recogniser predict region of interest in gray faces
        id_, conf = recogniser.predict(roi_gray)

        font = cv2.FONT_HERSHEY_SIMPLEX
        name = labels[id_]
        cv2.putText(img,name+" "+str(conf),(x,y),font,1,(255,255,255),2,cv2.LINE_AA)
        #cv2.circle(img,(cx,cy),5,(0,255,0),cv2.FILLED)

        facecoordsArea.append(area)
        facecoords.append([cx,cy])

    if len(facecoords) != 0:
        i = facecoordsArea.index(max(facecoordsArea))
        return img, [facecoords[i],facecoordsArea[i]],name
    else:
        return img,[[0,0],0],0

###############################################################YOLO####################################################################
def findfaceyolo(img):

    hight,width,_ = img.shape
    blob = cv2.dnn.blobFromImage(img, 1/255,(416,416),(0,0,0),swapRB = True,crop= False)
    net.setInput(blob)
    output_layers_name = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_name)
    facecoords = []
    facecoordsArea = []
    boxes = []
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            score = detection[5:]
            class_id = np.argmax(score)
            confidence = score[class_id]
            if confidence > 0.7:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * hight)
                w = int(detection[2] * width)
                h = int(detection[3]* hight)
                x = int(center_x - w/2)
                y = int(center_y - h/2)
                cx = x + w//2 
                cy = y + h //2
                area = w*h
                boxes.append([x,y,w,h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)
                facecoordsArea.append(area)
                facecoords.append([cx,cy])
    indexes = cv2.dnn.NMSBoxes(boxes,confidences,.5,.4)
    #Not sure why this is repeated
    boxes =[]
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            score = detection[5:]
            class_id = np.argmax(score)
            confidence = score[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * hight)
                w = int(detection[2] * width)
                h = int(detection[3]* hight)
                x = int(center_x - w/2)
                y = int(center_y - h/2)
                boxes.append([x,y,w,h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)
    indexes = cv2.dnn.NMSBoxes(boxes,confidences,.8,.4)
    
    font = cv2.FONT_HERSHEY_PLAIN
    color = (255,255,0)
    if  len(indexes)>0:
        for i in indexes.flatten():
            x,y,w,h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i],2))
            cv2.rectangle(img,(x,y),(x+w,y+h),color,2)
            cv2.putText(img,label + " " + confidence, (x,y+400),font,2,color,2)

    if len(facecoords) != 0:
        i = facecoordsArea.index(max(facecoordsArea))
        return img, [facecoords[i],facecoordsArea[i]],label
    else:
        return img,[[0,0],0],0

#################################################################SVM#######################################################################################
def findfaceSVM(frame):

    #load a target image relative to code location
    #cwd = os.getcwd()
    default_folder = "/home/thinkpad/Desktop/msc_face_recognition_project/examples/target_image/"
    target_folder = "/home/thinkpad/Desktop/Tello_ai_with_face_recognition/resources/target/"
    try:
        tmp = os.listdir(target_folder)

        target_image = face_recognition.load_image_file(target_folder+tmp[0])
        target_face_encoding = face_recognition.face_encodings(target_image)[0]

        #get name from Target folder and strip file extension
        file_extension = '.'
        stripped_file_name = tmp[0].split(file_extension,1)[0]

        # Create arrays of known face encodings and their names
        known_face_encodings = [
            target_face_encoding
        ]
        known_face_names = [
            str(stripped_file_name)
        ]

        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True
        
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            facecoords = []
            facecoordsArea = []
            face_names = []

            for (x,y,w,h) in face_locations:
                cx = x + w//2 
                cy = y + h //2
                area = w*h

                facecoordsArea.append(area)
                facecoords.append([cx,cy])

            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame
        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to w and h size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name+" "+str(face_distances[0]), (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        #get the right index for the face area from the known names array
        if len(facecoords) != 0:
            #Checking for strings in a string array https://www.askpython.com/python/list/find-string-in-list-python

                # get index of name to match to area of face https://stackoverflow.com/questions/176918/finding-the-index-of-an-item-in-a-list
            i = facecoordsArea.index(max(facecoordsArea))
            return frame, [facecoords[i],facecoordsArea[i]],face_names[i] 
        else:
            return frame, [[0,0],0],0
      
    except Exception as e:
        if not tmp:
            print("No target set...", e)
            print("looking for target(s)...")
            tmp = os.listdir(default_folder)
            
def trackface(tello, info,w,h,pid= [0.5,0.5,0],pErrorLR=0,pErrorUD=0,safe_distance = [6200,6800],name=0):
    
    #---- RECOGNISED FACES ---- If named target detected, go to target
    if isinstance(name,str): 
        
        #---------------------------------PID control------------------------------------------------
        x,y = info[0]
        area = info[1]
        speedFB = 0
        #PID controller for YAW left and right---------------------------------------------------------
        #subtract object detected distance from screen centre to find the difference for correction

        errorLR  = x - w//2
        speedLR =  ((pid[0] *errorLR) + pid[1] * (errorLR-pErrorLR))
        speedLR = int(np.clip(speedLR,-100,100))#constraints the values for yaw between -100 and 100 where 0 is do nothing

        #PID for moving drone up and down---------------------------------------------------------------
        errorUD = y - h//2
        speedUD = ((pid[0] *errorUD) + pid[1] * (errorUD-pErrorUD))*-1
        speedUD = int(np.clip(speedUD,-100,100))
        
        #PID for moving drone forward and backward------------------------------------------------------
    
        if area > safe_distance[0] and area < safe_distance[1]:
            speedFB = 0
        #move backwards
        elif area > safe_distance[1]:
            speedFB = -40
        #move forwards
        elif area < safe_distance[0] and area != 0:
            speedFB = 40
        #---------------------------------PID control---------------------------------------------------

        #check if face detected in frame
        if x != 0:
            # face_found = True
            #sending velocity commands to both YAW AND LEFT_RIGHT at the same time results in poor control, pick one and comment out the other
            tello.yaw_velocity = speedLR
            tello.up_down_velocity = speedUD
            #tello.left_right_velocity = speedLR
            tello.for_back_velocity = speedFB
        else:
            tello.for_back_velocity = 0
            tello.left_right_velocity = 0
            tello.up_down_velocity = 0
            tello.yaw_velocity = 0
            errorLR = 0
            errorUD = 0
            speedFB = 0
        #if no face in frame and no body then look for people
        # if x == 0 and body_found == False:
        #     search_for_target(tello,target_lost=True)
            
        tello.send_rc_control(tello.left_right_velocity,
        tello.for_back_velocity,
        tello.up_down_velocity,
        tello.yaw_velocity)

        return [errorLR,errorUD]

    #---- UNRECOGNISED FACES ----If no target is detected get no closer than safe distance to closest face 
    elif isinstance(name,int):

        x,y = info[0]
        area = info[1]
        speedFB = 0

        if area > safe_distance[0] and area < safe_distance[1]:
            speedFB = 0
        #move backwards
        elif area > safe_distance[1]:
            speedFB = -40
        
        #check if face detected in frame
        if x != 0:
            # face_found = True
            tello.for_back_velocity = speedFB
        else:
            tello.for_back_velocity = 0
            tello.left_right_velocity = 0
            tello.up_down_velocity = 0
            tello.yaw_velocity = 0
            errorLR = 0
            errorUD = 0
            speedFB = 0
        #if no face in frame and no body then look for people
        # if x == 0 and body_found == False:
        #     search_for_target(tello,target_lost=True)

        tello.send_rc_control(tello.left_right_velocity,
        tello.for_back_velocity,
        tello.up_down_velocity,
        tello.yaw_velocity)
        return [errorLR,errorUD]
    else:
        pass


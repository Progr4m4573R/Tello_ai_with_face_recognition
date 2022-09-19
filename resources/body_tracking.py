#Source: https://www.goeduhub.com/10026/detect-humans-in-an-image-using-haar-cascade
import numpy as np
import cv2
#from behaviours import *

bodycascade = cv2.CascadeClassifier('/home/thinkpad/Desktop/Tello_ai_with_face_recognition/resources/cascades/haarcascade_fullbody.xml')
def findpeople(img):
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    bodies = bodycascade.detectMultiScale(image=imgGray, scaleFactor=1.2, minNeighbors=3)#scale and minimum factor

    bodycoords = []
    bodycoordsArea = []

    for (x,y,w,h) in bodies:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
        cx = x + w//2 
        cy = y + h //2
        area = w*h

        font = cv2.FONT_HERSHEY_SIMPLEX

        cv2.putText(img,"unknown_person",(x,y),font,1,(255,255,255),2,cv2.LINE_AA)
        #cv2.circle(img,(cx,cy),5,(0,255,0),cv2.FILLED)

        bodycoordsArea.append(area)
        bodycoords.append([cx,cy])
        
    # gets area of closest person
    if len(bodycoords) != 0:
        i = bodycoordsArea.index(max(bodycoordsArea))
        return img, [bodycoords[i],bodycoordsArea[i]]
    else:
        return img,[[0,0],0]
        
def trackbodies(tello, info,w,h,pid= [0.5,0.5,0],pErrorLR=0,pErrorUD=0,safe_distance = [6200,6800]):
    #body_found = False
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

    #check if body detected in frame
    if x != 0:
        #body_found = True
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
    #if no bodies in frame call the autonomous movement script
    # if x == 0 and face_found == False:
    #     body_found = False
    #     search_for_target(tello,target_lost=True)
        
    tello.send_rc_control(tello.left_right_velocity,
    tello.for_back_velocity,
    tello.up_down_velocity,
    tello.yaw_velocity)

    return [errorLR,errorUD]

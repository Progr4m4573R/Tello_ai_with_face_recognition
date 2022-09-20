import cv2
import time
#Source: https://www.geeksforgeeks.org/python-import-module-from-different-directory/ I USED  THE COMMAND IN TERMINAL TO ADD MY IMPORTS TO THE PYTHON PATH export PYTHONPATH=’path/to/directory’
import sys
sys.path.insert(1,'/home/thinkpad/Desktop/Tello_ai_with_face_recognition/resources')
from face_tracking import *
from body_tracking import *
import keyboardControl as kbc
import mapping
#initialise keyboard control
kbc.init()
#Configurations------------------------------ 
tello_fly = False
w,h = kbc.w,kbc.h
pid = [0.5,0.5,0]#change these values to make the movement smoother Proportional Intergral Derivitate

#safe distance
safe_distance = [6200,6800] #smaller values mean drone is closer; 6200 is about 2 metres equivalent
body_safe_distance = [6200,6800]
#PID previous error for face tracking
pErrorLR = 0
pErrorUD = 0
#PID previous error for body tracking
BodypErrorLR = 0
BodypErrorUD = 0
#initialise tello---------------------------
tello = initialisetello()
#Run the code in loop so each frame can be processed---------

while True:
    ##initial step
    if tello_fly == True:
        tello.takeoff()
        tello_fly = False
    
    ##Step 1 get frame from drone cam
    cap = telloGetFrame(tello,w,h)#360 240
    
    #step 2 find face in frame with yolo
    frame,info,name = findfaceyolo(cap)
    _,body_location = findpeople(cap)
    #step 3 track the face with PID
    pErrorLR, pErrorUD = trackbodies(tello,body_location,w,h,pid,BodypErrorLR,BodypErrorUD,body_safe_distance)
    pErrorLR, pErrorUD = trackface(tello,info,w,h,pid,pErrorLR,pErrorUD,safe_distance,name)
    cv2.imshow("TelloYOLO",frame)
    #step 4 optional-------control drone with keyboard, set to true to enable keyboard control
    vals = kbc.action(frame)
    tello.send_rc_control(vals[0],vals[1],vals[2],vals[3])
    time.sleep(0.05)
    #Can record videos by pressing v or take pictures with p    
    kbc.getVideoFrames(frame)

    #step 5 optional-------control drone with ble devices i.e phones and watches
    
    #maping
    #map = np.zeros((1000,1000,3),np.uint8)#3 representscolored image
    #mapping.drawPoints(map)

    print("Battery at: ",tello.get_battery(),"%")
    print("Signal at: ",tello.query_wifi_signal_noise_ratio(),"%")
    print("Height at: ", tello.get_height()/100,"m")
    if cv2.waitKey(1) & kbc.getKey("c"):
        print("Communication Terminated....")
        break
#call to deallocate resources
tello.end()
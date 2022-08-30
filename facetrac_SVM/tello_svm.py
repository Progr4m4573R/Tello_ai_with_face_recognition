import cv2
import time
import sys
#source: https://stackoverflow.com/questions/12280143/how-to-move-to-one-folder-back-in-python
sys.path.insert(1,'/home/thinkpad/Desktop/Tello_ai_face_recognition/tello-ai/resources/')#'/home/thinkpad/Desktop/Tello_Drone_Control/tello-ai/'
#import face tracking module
from face_tracking import *
#import keyboard module
import keyboardControl as kbc
#initialise keyboard control
kbc.init()
#Configurations------------------------------ 
tello_fly = False
keyboard_control = True
facetracking = True

#set frame size for processing-----------------
w,h = 720,480
pid = [0.5,0.5,0]#change these values to make the movement smoother Proportional Intergral Derivitate

#safe distance
safe_distance = [6200,6800] #smaller values mean drone is closer; 6200 is about 2 metres equivalent

#Actual error
pErrorLR = 0
pErrorUD = 0
#initialise tello---------------------------
tello = initialisetello()
#Run the code in loop so each frame can be processed---------
while True:
    ##initial step
    if tello_fly == True:
        tello.takeoff()
        tello_fly = False
    
    ##Step 1 get frame from drone cam
    tello_cam = tello.get_frame_read()
    tello_cam = tello_cam.frame
    #step 2 find face in frame with yolo
    frame,info,name = findfaceSVM(tello_cam)

    #step 3 track the face with PID  error in x ais, y axis and front back
    pErrorLR, pErrorUD = trackface(tello,info,w,h,pid,pErrorLR,pErrorUD,safe_distance,facetracking,name)
    cv2.imshow('TelloSVM',frame)
    
    #step 4 optional-------control drone with keyboard, set to true to enable keyboard control
    vals = kbc.action(keyboard_control,frame)
    tello.send_rc_control(vals[0],vals[1],vals[2],vals[3])    #print("lr,fb,ud,yv commands from keyboard: ",vals)
    time.sleep(0.05)
    #Can record videos by pressing v or take pictures with p    
    kbc.getVideoFrames(frame)

    print("target: ",name)
    #step 5 optional-------control drone with ble devices i.e phones and watches
    print("Battery at: ",tello.get_battery(),"%")
    if cv2.waitKey(1) & kbc.getKey("c"):
        print("Communication Terminated....")
        break

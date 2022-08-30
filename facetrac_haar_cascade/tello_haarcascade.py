#Source: https://www.youtube.com/watch?v=P2wl3N2JW9c
import cv2
import time
import sys
#import scripts from different directories: https://www.codegrepper.com/code-examples/python/python+how+to+include+script+from+different+directory
sys.path.insert(1,'/home/thinkpad/Desktop/Tello_ai_face_recognition/tello-ai/resources/')
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
w,h = 720,480#360,240
pid = [0.5,0.5,0]#change these values to make the movement smoother Proportional Intergral Derivitate

#safe distance
safe_distance = [6200,6800] #smaller values mean drone is closer about 2 metres equivalent

#Actual error
pErrorLR = 0
pErrorUD = 0
#initialise tello---------------------------
tello = initialisetello()

while True:

    ##initial step
    if tello_fly == True:
        tello.takeoff()
        tello_fly = False
    
    ##Step 1 get frame from drone cam
    img = telloGetFrame(tello,w,h)

    #step 2 find face in frame with viola jones haar cascade method
    img,info,name = findfacehaar(img)
    #print("Centre:", info[0], "Face Area:", info[1])

    #step 3 track the face with PID
    #error in x ais, y axis and front back
    pErrorLR, pErrorUD = trackface(tello,info,w,h,pid,pErrorLR,pErrorUD,safe_distance,facetracking,name)
    cv2.imshow("TelloHAAR",img)
    
    #step 4 optional------control drone with keyboard, set to true to enable keyboard control
    vals = kbc.action(keyboard_control,img)     #print("lr,fb,ud,yv commands from keyboard: ",vals)
    tello.send_rc_control(vals[0],vals[1],vals[2],vals[3])
    time.sleep(0.05)

    #Can record videos by pressing v or take pictures with p    
    kbc.getVideoFrames(img)
    #step 5 optional------control drone with ble devices i.e phones and watches
    print("Battery at: ",tello.get_battery(),"%")
    if cv2.waitKey(1) & kbc.getKey("c"):
        print("Communication Terminated....")
        break
        


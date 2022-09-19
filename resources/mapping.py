#get the speed of the drone and time taken to plot x an y in cartesian coordinates
import numpy as np
import time
import cv2
import math
# from face_tracking import initialisetello

# tello = initialisetello()
from djitellopy import Tello

tello = Tello()
####---------------default parameters for configuration--------------####

fSpeed = 117/10 #forward speed cm/s
aSpeed = 360/10 # angular speed degrees/s
interval = 0.25 # how often to check tello speed/ lower is more accurate

#units of tello actual movement represented in map for every unit of movement
dInterval = fSpeed * interval
aInterval = aSpeed * interval
###--------------------------################-----------------------######
#coords to represent Tello coordinates
tello_x, tello_y = 500,500
a = 0
yaw = 0

coordinates = [(0,0), (0,0)]

def drawPoints(img):
    global tello_x,tello_y, yaw, a
    d = 0

    speedLR = tello.get_acceleration_x()
    speedFB = tello.get_acceleration_y()
    tello_yaw = tello.get_yaw() 
    height = tello.get_height()
    # the accelerations fluctuate when drone is at a stand still so there is a need for ignoring noise
    positive_threshold = 10
    negative_thrreshold = -10

    if speedLR < negative_thrreshold:
        d = dInterval
        a = -180
        #print("moving left: ", speedLR)
    elif speedLR > positive_threshold:
        d = -dInterval
        a = 180
        #print("moving right: ", speedLR)
    if speedFB > positive_threshold:
        d = dInterval
        a = 270
        #print("moving foward: ", speedFB)
    elif speedFB < negative_thrreshold:
        d = -dInterval
        a = -90
        #print("moving backward: ", speedFB)

    if tello_yaw > positive_threshold:
        yaw += aInterval
        #print("Rotating clockwise: ", tello_yaw)
    if tello_yaw < negative_thrreshold:
        yaw -= aInterval
        #print("Rotating anti-clockwise: ", tello_yaw)
    
    time.sleep(interval)
    a += yaw
    tello_x += int(d*math.cos(math.radians(a)))
    tello_y += int(d*math.sin(math.radians(a)))
    coordinates.append([tello_x,tello_y])
    for coords in coordinates:
        cv2.circle(img,(coords),5,(0,0,255),cv2.FILLED)#BGR

    cv2.circle(img,(coordinates[-1]),8,(0,255,0),cv2.FILLED)#BGR
    cv2.putText(img,"Tello", (tello_x,tello_y),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    cv2.putText(img,(f'x = {(coordinates[-1][0]-500)/100},y = {(coordinates[-1][1]-500)/100},z = {height}) Metres'),(coordinates[-1][0]+10,coordinates[-1][1] + 30),cv2.FONT_HERSHEY_PLAIN,1,(255,0,255),1)
    cv2.imshow("Tello map", img)
def mapping():
    img = np.zeros((1000,1000,3),np.uint8)#3 representscolored image
    
    drawPoints(img)
    #cv2.imshow("Tello map", img)


def main():
    mapping()
if __name__ == '__main__':

    while True:
        main()
        if cv2.waitKey(1) & 0xFF ==ord('q'):
            print("Exit mapping...")
            break

#get the speed of the drone and time taken to plot x an y in cartesian coordinates
import numpy as np
import time
import cv2
import math

from PIL import Image
from PIL.Image import Resampling

from djitellopy import Tello

tello = Tello()
####---------------default parameters for configuration--------------####

fSpeed = 117/10 #forward speed cm/s 11.7cm per second
aSpeed = 360/10 # angular speed degrees/s
interval = 0.25 # how often to check tello speed/ lower is more accurate

#units of tello actual movement represented in map for every unit of movement
#speed = distance / time
dInterval = fSpeed * interval
aInterval = aSpeed * interval
###--------------------------################-----------------------######
#Map grid size
grid_width = 1000
grid_height = 1000

#coords to represent Tello coordinates (centre o the grid)
startcords_x_y = 500,500
tello_x, tello_y = startcords_x_y
#angle
a = 0
#rotation about the x axis
yaw = 0

coordinates = [(0,0), (0,0)]

def drawPoints(img):
    global tello_x,tello_y, yaw, a
    #distance
    d = 0
    #DRONE READINGS TO DRAW
    speedLR = tello.get_speed_x() # between -500 and 500
    #multiply by -1 one to make north go up as grid points start at (0,0) in top left not bottom left
    speedFB = -1*(tello.get_speed_y()) # between -500 and 500 
    tello_yaw = tello.get_yaw() # between -360 and 360
    height = tello.get_height()
    # the acceleration values fluctuate when drone is at a stand still so there is a need for ignoring noise
    positive_threshold = 0
    negative_threshold = -0

    #MOVING LEFT  
    if speedLR < negative_threshold:
        d = dInterval
        a = -180
        #print("moving left: ", speedLR)
    #ROTATING RIGHT
    elif speedLR > positive_threshold:
        d = -dInterval
        a = 180
        #print("moving right: ", speedLR)
    #MOVING FORWARD
    if speedFB > positive_threshold:
        d = -dInterval
        a = 270
        #print("moving foward: ", speedFB)
    #MOVING BACKWARD
    elif speedFB < negative_threshold:
        d = dInterval
        a = -90
        #print("moving backward: ", speedFB)
    #ROTATING RIGHT
    if tello_yaw > positive_threshold:
        if yaw < tello_yaw:
            yaw += aInterval
        #print("Rotating clockwise: ", tello_yaw)
    #ROTATING LEFT  
    if tello_yaw < negative_threshold:
        if yaw > tello_yaw:
            yaw -= aInterval
        #print("Rotating anti-clockwise: ", tello_yaw)
    
    time.sleep(interval)
    a += yaw
    #Update the tello coordinates relative to the tello symbol location
    if tello_x < startcords_x_y[0]+speedLR:
        tello_x += int(d*math.cos(math.radians(a)))
    elif tello_x > startcords_x_y[0]+speedLR:
        tello_x += int(d*math.cos(math.radians(a)))
    if tello_y < startcords_x_y[1]+speedFB:
        tello_y += int(d*math.sin(math.radians(a)))
    elif tello_y > startcords_x_y[1]+speedFB:
        tello_y += int(d*math.sin(math.radians(a)))

    coordinates.append([tello_x,tello_y])
    for coords in coordinates:
        cv2.circle(img,(coords),5,(0,0,255),cv2.FILLED)#BGR

    cv2.circle(img,(coordinates[-1]),8,(0,255,0),cv2.FILLED)#BGR
    cv2.putText(img,"Tello", (tello_x,tello_y),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    cv2.putText(img,(f'x = {(coordinates[-1][0]-grid_width/2)/100},y = {(coordinates[-1][1]-grid_height/2)/100},yaw = {yaw} degrees,z = {height} metres'),(coordinates[-1][0]+10,coordinates[-1][1] + 30),cv2.FONT_HERSHEY_PLAIN,1,(0,0,255),1)
    cv2.imshow("Tello map", img)
def mapping():
    img_shape = (grid_width,grid_height,4)
    img = np.zeros(img_shape,np.uint8)#3 representscolored image
    #source https://www.adamsmith.haus/python/answers/how-to-convert-an-image-to-an-array-in-python
    temp = Image.open("Tello map template 2.0.png")
    map = temp.resize((grid_width,grid_height),Resampling.LANCZOS)
    image_sequence = map.getdata()
    map_array = np.array(image_sequence)
    #source https://stackoverflow.com/questions/60028853/cannot-reshape-array-of-size-into-shape
    map_image = np.reshape(map_array,img_shape)
    # print("blank image shape",img.shape)
    # print("map image shape", map_array.shape)
    # print("map image reshaped", map_image.shape)
    #source https://stackoverflow.com/questions/23830618/python-opencv-typeerror-layout-of-the-output-array-incompatible-with-cvmat
    image = np.ascontiguousarray(map_image, dtype=np.uint8)
    drawPoints(image)
    #cv2.imshow("Tello map", map_image)

def main():
    mapping()
if __name__ == '__main__':
    main()
    while True:
        main()
        if cv2.waitKey(1) & 0xFF ==ord('q'):
            print("Exit mapping...")
            break

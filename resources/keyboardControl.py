import pygame
import time
import cv2

global set_target_img

#prep for saving videos
w,h = 960,720
fourcc = cv2.VideoWriter_fourcc(*'XVID')
video_frames = cv2.VideoWriter(f'/home/thinkpad/Desktop/TelloAI_face_recognition/tello-ai/tello_videos/{time.time()}.avi',fourcc,20.0,(w,h))

def init():
    pygame.init()
    pygame.display.set_mode((400,400))

def getKey(keyName):

    ans = False

    for event in pygame.event.get():
        pass
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame,'K_{}'.format(keyName))
    if keyInput[myKey]:
        ans = True

    pygame.display.update()

    return ans 

def getVideoFrames(img):
    
    video_frames.write(img)

def action(tello,img):

    lr,fb,ud,yv = 0,0,0,0
    speed = 50 #-500 to 500 best to only use 500 outside

    #move left right
    if getKey("d"): lr = speed
    elif getKey("a"): lr = -speed
    #up down
    if getKey("UP"): ud = speed
    elif getKey("DOWN"): ud = -speed
    # move forward back
    if getKey("w"): fb = speed
    elif getKey("s"): fb = -speed
    #rotate clockwise and anticlockwise
    if getKey("RIGHT"): yv = speed
    elif getKey("LEFT"): yv = -speed
    #take off
    if getKey("e"): tello.takeoff(); time.sleep(3)
    #land
    if getKey("q"): tello.land()

    #Take a picture
    if getKey("p"):
        print("Picture taken")
        cv2.imwrite(f'/home/thinkpad/Desktop/Tello_ai_with_face_recognition/tello_photos/{time.time()}.jpeg',img)
        time.sleep(0.3)
    
    #Take a video
    if getKey("v"):
        getVideoFrames(img)

    #set a new target for the drone to follow
    if getKey("t"):
        set_target_img = img
        cv2.imwrite(f"/home/thinkpad/Desktop/Tello_ai_with_face_recognition/resources/target/new_target.jpeg",set_target_img)
    
    return [lr,fb,ud,yv]


def main():
    #testing key detection
    if getKey("LEFT"): print("Left key pressed")
    if getKey("RIGHT"): print("Right key pressed")
    if getKey("UP"): print("UP key pressed")
    if getKey("DOWN"): print("Down key pressed")

    if getKey("w"): print("w key pressed")
    if getKey("a"): print("a key pressed")
    if getKey("s"): print("s key pressed")
    if getKey("d"): print("d key pressed")

if __name__ == '__main__':
    init()
    print("Keboard control called")
    while True:
        main()
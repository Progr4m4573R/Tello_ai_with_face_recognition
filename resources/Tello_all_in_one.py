import cv2
import pygame
import numpy as np
import time
from face_tracking import telloGetFrame,findfacehaar,findfaceSVM,findfaceyolo,initialisetello,trackface
#from body_tracking import *
#import mapping
# Speed of the drone
# 无人机的速度
S = 60
# Frames per second of the pygame window display
# A low number also results in input lag, as input information is processed once per frame.
# pygame窗口显示的帧数
# 较低的帧数会导致输入延迟，因为一帧只会处理一次输入信息
FPS = 120

global set_target_img
#prep for saving videos
#-------------------set w and h for processing
w,h = 960,720


class FrontEnd(object):
    Current_Face_Recognition_output = " "
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - e: Takeoff
            - q: Land
            - Arrow keys: UP, DOWN, ROTATE COUNTER CLOCKWISE, ROTATE CLOCKWISE
            - A and D: LEFT, RIGHT
            - W and S: FORWARD, BACKWARD.
            - P: Take picture
            - V: Take video

        保持Tello画面显示并用键盘移动它
        按下ESC键退出
        操作说明：
            E：起飞
            Q：降落
            方向键：前后左右
            LEFT和RIGHT：逆时针与顺时针转向
            FORWARD和BACK：上升与下降

    """

    def __init__(self):
        # Init pygame
        # 初始化pygame
        pygame.init()

        # Creat pygame window
        # 创建pygame窗口
        pygame.display.set_caption(self.Current_Face_Recognition_output)
        self.screen = pygame.display.set_mode([w, h])

        # Init Tello object that interacts with the Tello drone
        # 初始化与Tello交互的Tello对象
        self.tello = initialisetello()

        # Drone velocities between -100~100
        # 无人机各方向速度在-100~100之间
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.send_rc_control = False

        # create update timer
        # 创建上传定时器
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000 // FPS)
        self.pid = [0.5,0.5,0]#change these values to make the movement smoother Proportional Intergral Derivitate
        #Actual error
        self.pErrorLR = 0
        self.pErrorUD = 0
        #safe distance
        self.safe_distance = [6200,6800] #smaller values mean drone is closer; 6200 is about 2 metres equivalent

    def getKey(self,keyName):

        ans = False

        for event in pygame.event.get():
            pass
        keyInput = pygame.key.get_pressed()
        myKey = getattr(pygame,'K_{}'.format(keyName))
        if keyInput[myKey]:
            ans = True

        pygame.display.update()

        return ans 

    def getVideoFrames(self,img):
        #This can interfer with the drone receiving commands from keyboard if defined globally
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_frames = cv2.VideoWriter(f'/home/thinkpad/Desktop/Tello_ai_with_face_recognition/tello_videos/{time.time()}.avi',fourcc,20.0,(w,h))
        video_frames.write(img)

    def action(self,method):

        should_stop = False

        while not should_stop:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.update()
                elif event.type == pygame.QUIT:
                    should_stop = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        should_stop = True
                    else:
                        self.keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyup(event.key)

            if should_stop==True:
                break

            #Take a picture
            if self.getKey('p'):
                print("Picture taken")
                cv2.imwrite(f'/home/thinkpad/Desktop/Tello_ai_with_face_recognition/tello_photos/{time.time()}.jpeg',img)
                time.sleep(0.3)
            
            #Take a video
            if self.getKey('v'):
                self.getVideoFrames(img)

            #set a new target for the drone to follow
            if self.getKey('t'):
                set_target_img = img
                cv2.imwrite(f"/home/thinkpad/Desktop/Tello_ai_with_face_recognition/resources/target/new_target.jpeg",set_target_img)

            self.screen.fill([0, 0, 0])
            img = telloGetFrame(self.tello,w,h)
            #step 2 find faces in frame with viola jones haar cascade method, YOLO or SVM
            if method =="HAAR":
                frame,info,name = findfacehaar(img)
            elif method == "SVM":
                frame,info,name = findfaceSVM(img)
            elif method == "YOLO":
                frame,info,name = findfaceyolo(img)
            else:
                #DEFAULT TO NO FACE RECOGNITION IF ONE IS NOT SET
                frame,_,_= img
                #step 3 track the face with PID
            #self.pErrorLR, self.pErrorUD = trackbodies(self.tello,info,w,h,self.pid,self.pErrorLR,self.pErrorUD,self.safe_distance)
            #self.pErrorLR, self.pErrorUD = trackface(self.tello,info,w,h,self.pid,self.pErrorLR,self.pErrorUD,self.safe_distance,name)
            
            #mapping
            #mapping.mapping()
            
            # battery, signal strength, drone height 电池
            battery_text = "Battery: {}%".format(self.tello.get_battery())
            # drone_signal = "Signal: {}%".format(self.tello.query_wifi_signal_noise_ratio())
            # drone_height = "Height: {} m".format((self.tello.get_height())/100)
            
            #THESE SLOW THE FRAME RATE A LITTLE SO CONSIDER DISPLAYING IN CMD ONLY
            cv2.putText(frame, battery_text, (5, 720 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            # cv2.putText(frame, drone_signal, (225, 720 - 5),
            #     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            # cv2.putText(frame, drone_height, (430, 720 - 5),
            #     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)

            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            pygame.display.update()
            #print("FPS rate in modified rate is at:",FPS)
            time.sleep(1 / FPS)
        # Call it always before finishing. To deallocate resources.
        # 通常在结束前调用它以释放资源
        self.tello.end()

    def keydown(self, key):
        """ Update velocities based on key pressed
        Arguments:
            key: pygame key

        基于键的按下上传各个方向的速度
        参数：
            key：pygame事件循环中的键事件
        """
        if key == pygame.K_w:  # set forward velocity
            self.for_back_velocity = S
        elif key == pygame.K_s:  # set backward velocity
            self.for_back_velocity = -S
        elif key == pygame.K_a:  # set left velocity
            self.left_right_velocity = -S
        elif key == pygame.K_d:  # set right velocity
            self.left_right_velocity = S
        elif key == pygame.K_UP:  # set up velocity
            self.up_down_velocity = S
        elif key == pygame.K_DOWN:  # set down velocity
            self.up_down_velocity = -S
        elif key == pygame.K_LEFT:  # set yaw counter clockwise velocity
            self.yaw_velocity = -S
        elif key == pygame.K_RIGHT:  # set yaw clockwise velocity
            self.yaw_velocity = S

    def keyup(self, key):
        """ Update velocities based on key released
        Arguments:
            key: pygame key

        基于键的松开上传各个方向的速度
        参数：
            key：pygame事件循环中的键事件
        """
        if key == pygame.K_w or key == pygame.K_s:  # set zero forward/backward velocity
            self.for_back_velocity = 0
        elif key == pygame.K_a or key == pygame.K_d:  # set zero left/right velocity
            self.left_right_velocity = 0
        elif key == pygame.K_UP or key == pygame.K_DOWN:  # set zero up/down velocity
            self.up_down_velocity = 0
        elif key == pygame.K_LEFT or key == pygame.K_RIGHT:  # set zero yaw velocity
            self.yaw_velocity = 0
        elif key == pygame.K_e:  # takeoff
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == pygame.K_q:  # land
            not self.tello.land()
            self.send_rc_control = False

    def update(self):
        """ Update routine. Send velocities to Tello.

            向Tello发送各方向速度信息
        """
        if self.send_rc_control:
            self.tello.send_rc_control(self.left_right_velocity, self.for_back_velocity,
                self.up_down_velocity, self.yaw_velocity)


def main():
    frontend = FrontEnd()
    # Uncomment one of the following sets to choose a different recognition algorithm
    #1
    # frontend.Current_Face_Recognition_output = "TELLO HAAR CASCADE"
    # frontend.action("HAAR")
    #2
    # frontend.Current_Face_Recognition_output = "TELLO YOLO CASCADE"
    # frontend.action("YOLO")
    #3
    frontend.Current_Face_Recognition_output = "TELLO SVM CASCADE"
    frontend.action()

if __name__ == '__main__':
     main()

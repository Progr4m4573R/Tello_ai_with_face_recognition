from djitellopy import Tello
import cv2
import pygame
import numpy as np
import time
from face_tracking import telloGetFrame, findfacehaar, initialisetello
# Speed of the drone
# 无人机的速度
S = 60
# Frames per second of the pygame window display
# A low number also results in input lag, as input information is processed once per frame.
# pygame窗口显示的帧数
# 较低的帧数会导致输入延迟，因为一帧只会处理一次输入信息
FPS = 120

Current_Face_Recognition_output = " "
global set_target_img
#prep for saving videos
#-------------------set w and h for processing
w,h = 960,720


class FrontEnd(object):
    """ Maintains the Tello display and moves it through the keyboard keys.
        Press escape key to quit.
        The controls are:
            - T: Takeoff
            - L: Land
            - Arrow keys: Forward, backward, left and right.
            - A and D: Counter clockwise and clockwise rotations (yaw)
            - W and S: Up and down.

        保持Tello画面显示并用键盘移动它
        按下ESC键退出
        操作说明：
            T：起飞
            L：降落
            方向键：前后左右
            A和D：逆时针与顺时针转向
            W和S：上升与下降

    """

    def __init__(self):
        # Init pygame
        # 初始化pygame
        pygame.init()

        # Creat pygame window
        # 创建pygame窗口
        pygame.display.set_caption("Tello video stream")
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
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_frames = cv2.VideoWriter(f'/home/thinkpad/Desktop/Tello_ai_with_face_recognition/tello_videos/{time.time()}.avi',fourcc,20.0,(w,h))
        video_frames.write(img)

    def run(self):

        # In case streaming is on. This happens when we quit this program without the escape key.
        # 防止视频流已开启。这会在不使用ESC键退出的情况下发生。
        
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
                cv2.imwrite(f'/home/thinkpad/Desktop/Tello_ai_with_face_recognition/tello_photos/{time.time()}.jpeg',frame)
                time.sleep(0.3)
            
            #Take a video
            if self.getKey('v'):
                self.getVideoFrames(frame)

            #set a new target for the drone to follow
            if self.getKey('t'):
                set_target_img = frame
                cv2.imwrite(f"/home/thinkpad/Desktop/Tello_ai_with_face_recognition/resources/target/new_target.jpeg",set_target_img)
        
            self.screen.fill([0, 0, 0])
            img = telloGetFrame(self.tello,960,720)
            frame,_,_ = findfacehaar(img)
            
            # battery n. 电池
            text = "Battery: {}%".format(self.tello.get_battery())
            cv2.putText(frame, text, (5, 720 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)

            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            pygame.display.update()

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

    frontend.run()


if __name__ == '__main__':
    main()

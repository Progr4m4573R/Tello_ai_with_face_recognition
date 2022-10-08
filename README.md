# Tello_ai_with_face_recognition
Tello drone AI with Face recognition and a host of additional control features such as the ability to take pictures, videos and also switch targets mid operation (Target switching mid misison is only possible when running facetrac_SVM/tello_svm.py))

The tello_yolo.py will not run without the associated weights which i have taken out for the sake of uploading to gihub. these weights can be downloaded from my google drives 

Python Requirements:
1.Python 3.8.10
2.Dlib's face recognition algorithm
3.numpy
4.cv2
5.time
6.sys
7.djitellopy
8.math
9.pickle
10.os
11.PIL
12.YOLO darknet


Tello_all_in_one: When running Face recognition code some functions and features can end up slowing down the frame rate of the output video. In addition to this, remote control also experiences a lag in drone response to control input These functions are vital for some autonomous features and therefore cannot be removed. However, the drone can be run with them by commenting them out.

The modules and functions to comment out for manual control only are:
 
module: Bodytracking
function: trackbodies
function: trackface
module: mapping

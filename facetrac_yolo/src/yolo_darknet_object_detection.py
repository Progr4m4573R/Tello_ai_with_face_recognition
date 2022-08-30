
import cv2
import numpy as np


#author - Jay Shankar Bhatt 
# using this code without author's permission other then leaning task is strictly prohibited

## provide the absolute path for testing config file and tained model from colab
net = cv2.dnn.readNetFromDarknet("/home/thinkpad/Desktop/Tello_ai_face_recognition/tello-ai/facetrac_yolo/src/yolov3_custom.cfg","/home/thinkpad/Desktop/Tello_ai_face_recognition/tello-ai/facetrac_yolo/src/backup/yolov3_custom_6000.weights")

# Change here for custom classes for trained model this is really important because if the names are not in the correct order it will appear like improper classification
classes = ['Dog','Barak Obama','Stephen','Jack Sparrow']

cap = cv2.VideoCapture(0)

while 1:
    _, img = cap.read()
    img = cv2.resize(img,(1280,720))#1280 720
    hight,width,_ = img.shape
    blob = cv2.dnn.blobFromImage(img, 1/255,(416,416),(0,0,0),swapRB = True,crop= False)

    net.setInput(blob)

    output_layers_name = net.getUnconnectedOutLayersNames()

    layerOutputs = net.forward(output_layers_name)

    boxes =[]
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            score = detection[5:]
            class_id = np.argmax(score)
            confidence = score[class_id]
            if confidence > 0.7:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * hight)
                w = int(detection[2] * width)
                h = int(detection[3]* hight)
                x = int(center_x - w/2)
                y = int(center_y - h/2)
                boxes.append([x,y,w,h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)
    indexes = cv2.dnn.NMSBoxes(boxes,confidences,.5,.4)
    
    #Not sure why this is repeated again tbh
    boxes =[]
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            score = detection[5:]
            class_id = np.argmax(score)
            confidence = score[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * hight)
                w = int(detection[2] * width)
                h = int(detection[3]* hight)
                x = int(center_x - w/2)
                y = int(center_y - h/2)
                boxes.append([x,y,w,h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)
    indexes = cv2.dnn.NMSBoxes(boxes,confidences,.8,.4)

    font = cv2.FONT_HERSHEY_PLAIN
    colors = np.random.uniform(0,255,size =(len(boxes),3))
    if  len(indexes)>0:
        for i in indexes.flatten():
            x,y,w,h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i],2))
            color = colors[i]
            cv2.rectangle(img,(x,y),(x+w,y+h),color,2)
            cv2.putText(img,label + " " + confidence, (x,y+400),font,2,color,2)
    print("class ids: ",class_ids)
    cv2.imshow('img',img)
    if cv2.waitKey(1) == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
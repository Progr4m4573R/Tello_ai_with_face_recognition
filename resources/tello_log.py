
from enum import Enum


from pickle import TRUE
from cancel_token import CancellationToken # not available in Python 3.10 so use Python 3.8.10
from crc import CrcCalculator, Crc8
import threading
import socket
import time
import math
import asyncio
from datetime import timedelta
#######################################################RUN ME SOON AS YOU CAN##################################################
#pip install cancel-token

"""
@brief  Tello IP address. Use local IP address since 
        host computer/device is a WiFi self to Tello.
"""
tello_ip = "192.168.10.1"

"""
Tello port to send command message.
"""
command_port = 8889

"""
@brief  Host IP address. 0.0.0.0 referring to current 
        host/computer IP address.
"""
host_ip = "0.0.0.0"

"""
@brief  UDP port to receive response msg from Tello.
        Tello command response will send to this port.
"""
response_port = 9000
##################################################################################################################################################################
class FlyData:

    flyMode = 0
    height= 0
    verticalSpeed = 0
    flySpeed = 0
    eastSpeed = 0
    northSpeed = 0
    flyTime = 0

    flying = False#
    downVisualState = False
    droneHover = False
    eMOpen = False
    onGround = True
    pressureState = False

    batteryPercentage = 0#
    batteryLow = True
    batteryLower = True
    batteryState = True
    powerState = True
    droneBatteryLeft = 0
    droneFlyTimeLeft = 0

    cameraState = 0#
    electricalMachineryState = 0
    factoryMode = False
    frontIn = False
    frontLSC = False 
    frontOut = False
    gravityState = False
    imuCalibrationState = 0
    imuState = False
    lightStrength = 0
    outageRecording = False
    smartVideoExitMode = 0
    temperatureHeight = 0
    throwFlyTimer = 0
    wifiDisturb = 0
    wifiStrength = 0# = 100#
    windState = False

    #From log
    velX = 0
    velY = 0
    velZ = 0

    posX = 0
    posY = 0
    posZ = 0
    posUncertainty = 0

    velN = 0
    velE = 0
    velD = 0

    quatX = 0
    quatY = 0
    quatZ = 0
    quatW = 0

    def set(data):
        drone_status =FlyData()
        index = 0
        if (data[index] or (data[index + 1] << 8)):
            index += 2
        drone_status.height = data[index]

        if (data[index] or (data[index + 1] << 8)):
            index += 2
        drone_status.northSpeed = data[index]

        if (data[index] or (data[index + 1] << 8)):
            index += 2
        drone_status.eastSpeed = data[index] 

        drone_status.flySpeed = math.Sqrt(math.Pow(drone_status.northSpeed, 2) + math.Pow(drone_status.eastSpeed, 2))

        if (data[index] or (data[index + 1] << 8)):
            index += 2
        drone_status.verticalSpeed = data[index]  # ah.a(paramArrayOfByte[6], paramArrayOfByte[7])

        if data[index] | (data[index + 1] << 8):
            index += 2
        drone_status.flyTime = data[index] # ah.a(paramArrayOfByte[8], paramArrayOfByte[9])

        if (data[index] >> 0 & 0x1) == 1:
            drone_status.imuState =  True
        else:
            drone_status.imuState =  False

        if (data[index] >> 1 & 0x1) == 1:
            drone_status.pressureState = True
        else:
            drone_status.pressureState = False

        if (data[index] >> 2 & 0x1) == 1:
            drone_status.downVisualState = True
        else:
            drone_status.downVisualState = False

        if (data[index] >> 3 & 0x1) == 1:
            drone_status.powerState =  True
        else:
            drone_status.powerState =  False

        if (data[index] >> 4 & 0x1) == 1:
            drone_status.batteryState = True
        else:
            drone_status.batteryState =  False

        if (data[index] >> 5 & 0x1) == 1:
            drone_status.gravityState =  True
        else:
            drone_status.gravityState = False

        if (data[index] >> 7 & 0x1) == 1:
            drone_status.windState =  True
        else:
            drone_status.windState = False
        index += 1

        #if (paramArrayOfByte.length < 19) { }
        drone_status.imuCalibrationState = data[index]
        index += 1
        drone_status.batteryPercentage = data[index]
        index += 1
        drone_status.droneFlyTimeLeft = data[index] or (data[index + 1] << 8) 
        index += 2
        drone_status.droneBatteryLeft = data[index] or (data[index + 1] << 8) 
        index += 2

        #index 17
        if (data[index] >> 0 & 0x1)==1:
            drone_status.flying = True
        else:
            drone_status.flying = False

        if (data[index] >> 1 & 0x1) == 1:
            drone_status.onGround = True
        else:
            drone_status.onGround = False

        if (data[index] >> 2 & 0x1) == 1:
            drone_status.eMOpen = True
        else:
            drone_status.eMOpen =  False

        if(data[index] >> 3 & 0x1) == 1:
            drone_status.droneHover = True
        else:
            drone_status.droneHover =  False

        if(data[index] >> 4 & 0x1) == 1:
            drone_status.outageRecording = True
        else:
            drone_status.outageRecording = False

        if(data[index] >> 5 & 0x1) == 1:
            drone_status.batteryLow = True
        else:
            drone_status.batteryLow = False

        if (data[index] >> 6 & 0x1) == 1:
           drone_status.batteryLower =  True
        else:
            drone_status.batteryLower = False

        if (data[index] >> 7 & 0x1) == 1:
            drone_status.factoryMode = True
        else:
            drone_status.factoryMode = False
        index += 1

        drone_status.flyMode = data[index]
        index += 1
        drone_status.throwFlyTimer = data[index]
        index += 1
        drone_status.cameraState = data[index]
        index += 1

        #if (paramArrayOfByte.length >= 22)
        drone_status.electricalMachineryState = data[index]
        index += 1 #(paramArrayOfByte[21] & 0xFF)

        #if (paramArrayOfByte.length >= 23)
        if (data[index] >> 0 & 0x1) == 1:
            drone_status.frontIn = True
        else:
            drone_status.frontIn = False#22

        if (data[index] >> 1 & 0x1) == 1:
            drone_status.frontOut = True
        else:
            drone_status.frontOut = False

        if(data[index] >> 2 & 0x1) == 1:
            drone_status.frontLSC = True
        else:
            drone_status.frontLSC = False

        index += 1

        drone_status.temperatureHeight = (data[index] >> 0 & 0x1)#23

        drone_status.wifiStrength = Tello.wifiStrength#Wifi str comes in a cmd.
    

    #Parse some of the interesting info from the tello log stream
    def parseLog(data):
        drone_status =FlyData()
        pos = 0 

        #A packet can contain more than one record.
        while (pos < data.Length-2):#-2 for CRC bytes at end of packet.
        
            if (data[pos] != 'U'):#Check magic byte
            
                #print("PARSE ERROR!!!")
                break
            
            len = data[pos + 1]
            if (data[pos + 2] != 0):#Should always be zero (so far)
            
                #print("SIZE OVERFLOW!!!")
                break
        
            crc = data[pos + 3]
            id = int.from_bytes(data, pos + 4)
            xorBuf = [256]
            xorValue = data[pos + 6]
            
            if id == 0x1d:#29 new_mvo
                for i in range(len):#Decrypt payload.
                    xorBuf[i] = (data[pos + i] ^ xorValue)
                index = 10#start of the velocity and pos data.
                observationCount = int.from_bytes(xorBuf,signed=True)
                index += 2
                drone_status.velX = int.from_bytes(xorBuf, signed=True)
                index += 2
                drone_status.velY = int.from_bytes(xorBuf, signed=True)
                index += 2
                drone_status.velZ = int.from_bytes(xorBuf, index)
                index += 2
                drone_status.posX = int.from_bytes(xorBuf, index) 
                index += 4
                drone_status.posY = int.from_bytes(xorBuf, index) 
                index += 4
                drone_status.posZ = int.from_bytes(xorBuf, index) 
                index += 4
                drone_status.posUncertainty = float(xorBuf, index)*10000 
                index += 4
                #print(observationCount + " " + posX + " " + posY + " " + posZ)
                break
            elif id == 0x0800:#2048 imu
                for i in range(len):#Decrypt payload.
                    xorBuf[i] = (data[pos + i] ^ xorValue)
                index2 = 10 + 48#44 is the start of the quat data.
                drone_status.quatW = float(xorBuf, index2) 
                index2 += 4
                drone_status.quatX = float(xorBuf, index2) 
                index2 += 4
                drone_status.quatY = float(xorBuf, index2) 
                index2 += 4
                drone_status.quatZ = float(xorBuf, index2) 
                index2 += 4
                #print("qx:" + qX + " qy:" + qY+ "qz:" + qZ)

                # eular = toEuler(quatX, quatY, quatZ, quatW)
                #print(" Pitch:"+eular[0] * (180 / 3.141592) + " Roll:" + eular[1] * (180 / 3.141592) + " Yaw:" + eular[2] * (180 / 3.141592))

                index2 = 10 + 76#Start of relative velocity
                drone_status.velN = float(xorBuf, index2) 
                index2 += 4
                drone_status.velE = float(xorBuf, index2) 
                index2 += 4
                drone_status.velD = float(xorBuf, index2)
                index2 += 4
                #print(vN + " " + vE + " " + vD)        
        pos += len
        
    
    def toEuler():
        drone_status = FlyData()
        qX = drone_status.quatX
        qY = drone_status.quatY
        qZ = drone_status.quatZ
        qW = drone_status.quatW

        sqW = qW * qW
        sqX = qX * qX
        sqY = qY * qY
        sqZ = qZ * qZ
        yaw = 0.0
        roll = 0.0
        pitch = 0.0
        retv = [3]
        unit = sqX + sqY + sqZ + sqW # if normalised is one, otherwise
                                                # is correction factor
        test = qW * qX + qY * qZ
        if (test > 0.499 * unit):
            # singularity at north pole
            yaw = 2 * math.Atan2(qY, qW)
            pitch = math.PI / 2
            roll = 0
        
        elif (test < -0.499 * unit):
            # singularity at south pole
            yaw = -2 * math.Atan2(qY, qW)
            pitch = -math.PI / 2
            roll = 0
        
        else:
        
            yaw = math.Atan2(2.0 * (qW * qZ - qX * qY),
                    1.0 - 2.0 * (sqZ + sqX))
            roll = math.Asin(2.0 * test / unit)
            pitch = math.Atan2(2.0 * (qW * qY - qX * qZ),
                    1.0 - 2.0 * (sqY + sqX))
        
        retv[0] = pitch
        retv[1] = roll
        retv[2] = yaw
        return retv
    

    #For saving out state info.
    def getLogHeader():
        pass
    
        # StringBuilder sb = new StringBuilder()
        # foreach (System.Reflection.FieldInfo property in this.GetType().GetFields()):
        
        #     sb.Append(property.Name)
        #     sb.Append(",")
        
        # sb.AppendLine()
        # return sb
    def getLogLine():
        pass
    
        # StringBuilder sb = new StringBuilder()
        # foreach (System.Reflection.FieldInfo property in this.GetType().GetFields()):
        
        #     if(property.FieldType==typeof(Boolean)):
            
        #         if((property.GetValue(this)==true):
        #             sb.Append("1")
        #         else:
        #             sb.Append("0")
            
        #     else:
        #         sb.Append(property.GetValue(this))
        #     sb.Append(",")
        
        # sb.AppendLine()
        # return str(sb)
    

    def ToString():
        pass
        # StringBuilder sb = new StringBuilder()
        # count = 0
        # foreach (System.Reflection.FieldInfo property in this.GetType().GetFields()):
        
        #     sb.Append(property.Name)
        #     sb.Append(": ")
        #     sb.Append(property.GetValue(this))
        #     if(count+1%2==1):
        #         sb.Append(System.Environment.NewLine)
        #     else:
        #         sb.Append("      ")
        # return str(sb)
#########################################################################################################################################################################
class CRC:
    #Utils to calculate packet CRCs
    #FCS crc
    poly = 13970
    fcstab = [ 0, 4489, 8978, 12955, 17956, 22445, 25910, 29887, 35912, 40385, 44890, 48851, 51820, 56293, 59774, 63735, 4225, 264, 13203, 8730, 22181, 18220, 30135, 25662, 40137, 36160, 49115, 44626, 56045, 52068, 63999, 59510, 8450, 12427, 528, 5017, 26406, 30383, 17460, 21949, 44362, 48323, 36440, 40913, 60270, 64231, 51324, 55797, 12675, 8202, 4753, 792, 30631, 26158, 21685, 17724, 48587, 44098, 40665, 36688, 64495, 60006, 55549, 51572, 16900, 21389, 24854, 28831, 1056, 5545, 10034, 14011, 52812, 57285, 60766, 64727, 34920, 39393, 43898, 47859, 21125, 17164, 29079, 24606, 5281, 1320, 14259, 9786, 57037, 53060, 64991, 60502, 39145, 35168, 48123, 43634, 25350, 29327, 16404, 20893, 9506, 13483, 1584, 6073, 61262, 65223, 52316, 56789, 43370, 47331, 35448, 39921, 29575, 25102, 20629, 16668, 13731, 9258, 5809, 1848, 65487, 60998, 56541, 52564, 47595, 43106, 39673, 35696, 33800, 38273, 42778, 46739, 49708, 54181, 57662, 61623, 2112, 6601, 11090, 15067, 20068, 24557, 28022, 31999, 38025, 34048, 47003, 42514, 53933, 49956, 61887, 57398, 6337, 2376, 15315, 10842, 24293, 20332, 32247, 27774, 42250, 46211, 34328, 38801, 58158, 62119, 49212, 53685, 10562, 14539, 2640, 7129, 28518, 32495, 19572, 24061, 46475, 41986, 38553, 34576, 62383, 57894, 53437, 49460, 14787, 10314, 6865, 2904, 32743, 28270, 23797, 19836, 50700, 55173, 58654, 62615, 32808, 37281, 41786, 45747, 19012, 23501, 26966, 30943, 3168, 7657, 12146, 16123, 54925, 50948, 62879, 58390, 37033, 33056, 46011, 41522, 23237, 19276, 31191, 26718, 7393, 3432, 16371, 11898, 59150, 63111, 50204, 54677, 41258, 45219, 33336, 37809, 27462, 31439, 18516, 23005, 11618, 15595, 3696, 8185, 63375, 58886, 54429, 50452, 45483, 40994, 37561, 33584, 31687, 27214, 22741, 18780, 15843, 11370, 7921, 3960]
    
    def fsc16(bytes,len,poly):

        if (bytes == None):#source https://realpython.com/null-in-python/
            return 65535
        i = 0
        j = poly
        poly = len
        len = j
        while (True):
            j = len
            if (poly == 0):
                break
            
            j = bytes[i]
            len = CRC.fcstab[((len ^ j) & 0xFF)] ^ len >> 8
            i += 1
            poly -= 1
        
        return j
    #write fsc16 crc into the last 2 bytes of the array.
    def calcCrc(bytes, len):
    
        if ((bytes == None) or (len <= 2)):
            return
        
        i = CRC.fsc16(bytes, len - 2, CRC.poly)
        bytes[(len - 2)] = (i & 0xFF)#need to convert to bytes
        bytes[(len - 1)] = (i >> 8 & 0xFF)#need to convert to bytes

    #uCRC
    uCRCTable = [ 0, 94, 188, 226, 97, 63, 221, 131, 194, 156, 126, 32, 163, 253, 31, 65, 157, 195, 33, 127, 252, 162, 64, 30, 95, 1, 227, 189, 62, 96, 130, 220, 35, 125, 159, 193, 66, 28, 254, 160, 225, 191, 93, 3, 128, 222, 60, 98, 190, 224, 2, 92, 223, 129, 99, 61, 124, 34, 192, 158, 29, 67, 161, 255, 70, 24, 250, 164, 39, 121, 155, 197, 132, 218, 56, 102, 229, 187, 89, 7, 219, 133, 103, 57, 186, 228, 6, 88, 25, 71, 165, 251, 120, 38, 196, 154, 101, 59, 217, 135, 4, 90, 184, 230, 167, 249, 27, 69, 198, 152, 122, 36, 248, 166, 68, 26, 153, 199, 37, 123, 58, 100, 134, 216, 91, 5, 231, 185, 140, 210, 48, 110, 237, 179, 81, 15, 78, 16, 242, 172, 47, 113, 147, 205, 17, 79, 173, 243, 112, 46, 204, 146, 211, 141, 111, 49, 178, 236, 14, 80, 175, 241, 19, 77, 206, 144, 114, 44, 109, 51, 209, 143, 12, 82, 176, 238, 50, 108, 142, 208, 83, 13, 239, 177, 240, 174, 76, 18, 145, 207, 45, 115, 202, 148, 118, 40, 171, 245, 23, 73, 8, 86, 180, 234, 105, 55, 213, 139, 87, 9, 235, 181, 54, 104, 138, 212, 149, 203, 41, 119, 244, 170, 72, 22, 233, 183, 85, 11, 136, 214, 52, 106, 43, 117, 151, 201, 74, 20, 246, 168, 116, 42, 200, 150, 21, 75, 169, 247, 182, 232, 10, 84, 215, 137, 107, 53]
    def uCRC(bytes,len,poly):
            j = 0
            i = poly
            poly = j
            while (len != 0):      
                j = bytes[poly] ^ i
                i = j
                if (j < 0):
                    i = j + 256
                i = CRC.uCRCTable[i]
                poly += 1
                len -= 1
            return i
    #write uCRC to bytes[len-1]
    def calcUCRC(bytes,len):
        if ((bytes.Length == 0) or (len <= 2)):
            return
        i = CRC.uCRC(bytes, len - 1, 119)
        bytes[(len - 1)] = (i & 0xFF)#convert to bytes


class Tello:
    lastMessageTime = 0#for connection timeouts.

    state = FlyData()
    wifiStrength=0
    global connected

    # updateDeligate(cmdId)
    # event updateDeligate onUpdate
    # connectionDeligate(ConnectionState(newState))
    # event connectionDeligate onConnection
    # videoUpdateDeligate(data)
    # event videoUpdateDeligate onVideoData

    picPath = ""#todo redo this. 
    picFilePath = ""#todo redo this. 
    picMode = 0#pic or vid aspect ratio.

    iFrameRate = 5#How often to ask for iFrames in 50ms. Ie 2=10x 5=4x 10=2xSecond 5 = 4xSecond

    sequence = 1
    #https:#stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    class ConnectionState(Enum):
    
        Disconnected=0
        Connecting=0
        Connected=0
        Paused=0
        UnPausing = 0 #used to keep from disconnecting when starved for input.
        #Transition. Never stays in this state. 
    
    connectionState = ConnectionState.Disconnected

    cancelTokens = CancellationToken()#used to cancel listeners

    def takeOff(self):
        
        packet = { 0xcc, 0x58, 0x00, 0x7c, 0x68, 0x54, 0x00, 0xe4, 0x01, 0xc2, 0x16 }
        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)
        self.Send(packet)
    
    def throwTakeOff(self):
    
        packet = { 0xcc, 0x58, 0x00, 0x7c, 0x48, 0x5d, 0x00, 0xe4, 0x01, 0xc2, 0x16 }
        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)
        self.Send(packet)
    
    def land(self):
    
        packet = { 0xcc, 0x60, 0x00, 0x27, 0x68, 0x55, 0x00, 0xe5, 0x01, 0x00, 0xba, 0xc7 }

        ##payload
        packet[9] = 0x00##todo. Find out what this is for.
        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)
        self.Send(packet)
    
    def requestIframe(self):
        iframePacket = { 0xcc, 0x58, 0x00, 0x7c, 0x60, 0x25, 0x00, 0x00, 0x00, 0x6c, 0x95 }
        self.Send(iframePacket)

    def setMaxHeight(self,height):
    
        ##                           crc    typ  cmdL  cmdH  seqL  seqH  heiL  heiH  crc   crc
        packet = { 0xcc, 0x68, 0x00, 0x27, 0x68, 0x58, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5b, 0xc5 }

        #payload
        packet[9] = (height & 0xff)
        packet[10] = ((height >>8) & 0xff)

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    

    def queryUnk(self,cmd):
    
        packet = { 0xcc, 0x58, 0x00, 0x7c, 0x48, 0xff, 0x00, 0x06, 0x00, 0xe9, 0xb3 }
        packet[5] = cmd
        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)
        self.Send(packet)
    

    def queryAttAngle(self):
    
        packet =  { 0xcc, 0x58, 0x00, 0x7c, 0x48, 0x59, 0x10, 0x06, 0x00, 0xe9, 0xb3 }
        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)
        self.Send(packet)
    
    def queryMaxHeight(self):
        packet = { 0xcc, 0x58, 0x00, 0x7c, 0x48, 0x56, 0x10, 0x06, 0x00, 0xe9, 0xb3 }
        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)
        self.Send(packet)
    
    def setAttAngle(self,angle):
        ##                           crc    typ  cmdL  cmdH  seqL  seqH  ang1  ang2 ang3  ang4  crc   crc
        packet = { 0xcc, 0x78, 0x00, 0x27, 0x68, 0x58, 0x10, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x5b, 0xc5 }

        #payload
        bytes = int.to_bytes(angle)
        packet[9] = bytes[0]
        packet[10] = bytes[1]
        packet[11] = bytes[2]
        packet[12] = bytes[3]

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)

        Tello.queryAttAngle()#refresh
    
    def setEis(self,value):
        ##                           crc    typ  cmdL  cmdH  seqL  seqH  valL  crc   crc
        packet = { 0xcc, 0x60, 0x00, 0x27, 0x68, 0x24, 0x00, 0x09, 0x00, 0x00, 0x5b, 0xc5 }

        #payload
        packet[9] = (value & 0xff)

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    
    def doFlip(self,dir): 
        ##                           crc    typ  cmdL  cmdH  seqL  seqH  dirL  crc   crc
        packet = { 0xcc, 0x60, 0x00, 0x27, 0x70, 0x5c, 0x00, 0x09, 0x00, 0x00, 0x5b, 0xc5 }

        ##payload
        packet[9] = (dir & 0xff)

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)

    def setJpgQuality(self,quality):
        ##                           crc    typ  cmdL  cmdH  seqL  seqH  quaL  crc   crc
        packet = { 0xcc, 0x60, 0x00, 0x27, 0x68, 0x37, 0x00, 0x09, 0x00, 0x00, 0x5b, 0xc5 }

        #payload
        packet[9] = (quality & 0xff)

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    
    def setEV(self,ev):
    
        ##                            crc    typ  cmdL  cmdH  seqL  seqH  evL  crc   crc
        packet = { 0xcc, 0x60, 0x00, 0x27, 0x68, 0x34, 0x00, 0x09, 0x00, 0x00, 0x5b, 0xc5 }

        evb = (ev-9)#Exposure goes from -9 to +9
        #payload
        packet[9] = evb

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    
    def setVideoBitRate(self,rate):
        ##                          crc    typ  cmdL  cmdH  seqL  seqH  rateL  crc   crc
        packet = { 0xcc, 0x60, 0x00, 0x27, 0x68, 0x20, 0x00, 0x09, 0x00, 0x00, 0x5b, 0xc5 }

        #payload
        packet[9] = rate

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    
    def setVideoDynRate(self,rate):
        #                           crc    typ  cmdL  cmdH  seqL  seqH  rateL  crc   crc
        packet = { 0xcc, 0x60, 0x00, 0x27, 0x68, 0x21, 0x00, 0x09, 0x00, 0x00, 0x5b, 0xc5 }

        #payload
        packet[9] = rate

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    
    def setVideoRecord(self,n):
        ##                             crc    typ  cmdL  cmdH  seqL  seqH  nL  crc   crc
        packet = { 0xcc, 0x60, 0x00, 0x27, 0x68, 0x32, 0x00, 0x09, 0x00, 0x00, 0x5b, 0xc5 }

        ##payload
        packet[9] = n

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    
    # TELLO_CMD_SWITCH_PICTURE_VIDEO
    # 49 0x31
    # 0x68
    # switching video stream mode
    # data: u8 (1=video, 0=photo)
    
    def setPicVidMode(self,mode):
    
        ##                           crc    typ  cmdL  cmdH  seqL  seqH  modL  crc   crc
        packet = { 0xcc, 0x60, 0x00, 0x27, 0x68, 0x31, 0x00, 0x00, 0x00, 0x00, 0x5b, 0xc5 }

        picMode = mode

        ##payload
        packet[9] = (mode & 0xff)

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    
    def takePicture(self):
    
        ##                            crc    typ  cmdL  cmdH  seqL  seqH  crc   crc
        packet = { 0xcc, 0x58, 0x00, 0x7c, 0x68, 0x30, 0x00, 0x06, 0x00, 0xe9, 0xb3 }
        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)
        self.Send(packet)
        print("PIC START")
    
    def sendAckFilePiece(self,endFlag,fileId,pieceId):
    
        ##                                          crc    typ  cmdL  cmdH  seqL  seqH  byte  nL    nH    n2L                     crc   crc
        packet = { 0xcc, 0x90, 0x00, 0x27, 0x50, 0x63, 0x00, 0xf0, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5b, 0xc5 }

        packet[9] = endFlag
        packet[10] = (fileId & 0xff)
        packet[11] = ((fileId >> 8) & 0xff)

        packet[12] = ((int)(0xFF & pieceId))
        packet[13] = ((int)(pieceId >> 8 & 0xFF))
        packet[14] = ((int)(pieceId >> 16 & 0xFF))
        packet[15] = ((int)(pieceId >> 24 & 0xFF))

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)
        # dataStr = BitConverter.ToString(packet).Replace("-", " ")
        #print(dataStr)

        self.Send(packet)
    
    # def a(final byte b, final int n, final int n2):
    
    #     final c c = new c(18)
    #     c.a(204)
    #     c.a(()144)
    #     c.a(com.ryzerobotics.tello.gcs.core.b.c(c.b(), 4))
    #     c.a(80)
    #     c.a(()99)
    #     c.a(this.e.a())
    #     c.a(b)
    #     c.a(()n)
    #     c.b(n2)
    #     com.ryzerobotics.tello.gcs.core.a.b(c.b(), 18)
    #     com.ryzerobotics.tello.gcs.core.c.a.a().a(c)
    
    def sendAckFileSize(self):
    
        ##                                          crc    typ  cmdL  cmdH  seqL  seqH  modL  crc   crc
        packet = { 0xcc, 0x60, 0x00, 0x27, 0x50, 0x62, 0x00, 0x00, 0x00, 0x00, 0x5b, 0xc5 }
        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    
    def sendAckFileDone(self,size):
    
        ##                                          crc    typ  cmdL  cmdH  seqL  seqH  fidL  fidH  size  size  size  size  crc   crc
        packet = { 0xcc, 0x88, 0x00, 0x24, 0x48, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5b, 0xc5 }

        #packet[9] = (fileid & 0xff)
        #packet[10] = ((fileid >> 8) & 0xff)

        packet[11] = ((int)(0xFF & size))
        packet[12] = ((int)(size >> 8 & 0xFF))
        packet[13] = ((int)(size >> 16 & 0xFF))
        packet[14] = ((int)(size >> 24 & 0xFF))
        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    

    def sendAckLog(self,cmd,id):
    
        ##                           crc    typ  cmdL  cmdH  seqL  seqH  unk   idL   idH   crc   crc
        packet = { 0xcc, 0x70, 0x00, 0x27, 0x50, 0x50, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5b, 0xc5 }

        ba = int.to_bytes(cmd)
        packet[5] = ba[0]
        packet[6] = ba[1]

        ba = int.to_bytes(id)
        packet[10] = ba[0]
        packet[11] = ba[1]

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    

    #this might not be working right 
    def sendAckLogConfig(self,cmd,  id, n2):
    
        ##                            crc    typ  cmdL  cmdH  seqL  seqH  unk   idL   idH  n2L   n2H  n2L   n2H   crc   crc
        packet =  { 0xcc, 0xd0, 0x00, 0x27, 0x88, 0x50, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00,0x00, 0x00, 0x5b, 0xc5 }

        ba = int.to_bytes(cmd)
        packet[5] = ba[0]
        packet[6] = ba[1]

        ba = int.to_bytes(id)
        packet[10] = ba[0]
        packet[11] = ba[1]

        packet[12] = ((int)(0xFF & n2))
        packet[13] = ((int)(n2 >> 8 & 0xFF))
        packet[14] = ((int)(n2 >> 16 & 0xFF))
        packet[15] = ((int)(n2 >> 24 & 0xFF))

        #ba = int.to_bytes(n2)
        #packet[12] = ba[0]
        #packet[13] = ba[1]
        #packet[14] = ba[2]
        #packet[15] = ba[3]

        self.setPacketSequence(packet)
        self.setPacketCRCs(packet)

        self.Send(packet)
    

    def setPacketSequence(self,packet):
    
        packet[7] = (self.sequence & 0xff)
        packet[8] = ((self.sequence >> 8) & 0xff)
        self.sequence+1
    
    def setPacketCRCs(packet):
    
        CRC.calcUCRC(packet, 4)
        CRC.calcCrc(packet, packet.Length)

    def setEIS(eis):
        pass


    def xsetAxis(axis):
    
        #joyAxis = axis.Take(5).ToArray() 
        #joyAxis[4] = axis[7]
        #joyAxis[3] = axis[11]
        pass
    

    def disconnect(self):
        cancelTokens = CancellationToken()
        connectionState = connectionState()
        #kill listeners
        cancelTokens.cancel()
        #self.self.Close()
        Tello.ConnectionState.Connected = False

        if (connectionState != Tello.ConnectionState.Disconnected):
        
            #if changed to disconnect send event
            onConnection(self.ConnectionState.Disconnected)
        connectionState = self.ConnectionState.Disconnected

    def connect(self):
        ConnectionState = ConnectionState()
        #print("Connecting to tello.")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host_ip, response_port))  # Bind for receiving

        connectionState = self.ConnectionState.Connecting
        #send event
        onConnection(connectionState)
        #source: https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3
        mystring = "conn_req:\x00\x00"
        connectPacket = mystring.encode('utf-8')
        connectPacket[connectPacket.Length - 2] = 0x96
        connectPacket[connectPacket.Length - 1] = 0x17
        self.Send(connectPacket)
    

    #Pause connections. Used by aTello when app paused.
    def connectionSetPause(self,bPause):
        ConnectionState = ConnectionState()
        #NOTE only pause if connected and only unpause (connect) when paused.
        if (bPause & connectionState == self.ConnectionState.Connected):
        
            connectionState = self.ConnectionState.Paused
            #send event
            onConnection(connectionState)
        
        elif (bPause ==False & connectionState == self.ConnectionState.Paused):
        
            #NOT-E:send unpause and not connection event
            onConnection(self.ConnectionState.UnPausing)

            connectionState = self.ConnectionState.Connected
        
    

    picbuffer=[3000*1024]
    picChunkState = []
    picPieceState = []
    picBytesRecived = []
    picBytesExpected = []
    picExtraPackets = []
    picDownloading = []
    maxPieceNum = 0
    def startListeners(self):
        state = FlyData()
        cancelTokens = CancellationToken()
        token = cancelTokens

        #wait for reply messages from the tello and process. 
        async def wait_for_message():
            print("Waiting for messages...")
            while (True):
                try:
                    if (token.IsCancellationRequested):#handle canceling thread.
                        break
                    received = await self.Receive()
                    lastMessageTime = time.gmtime(0)#for timeouts

                    if(connectionState==self.ConnectionState.Connecting):
                    
                        if(received.Message.StartsWith("conn_ack")):
                        
                            connected = True
                            connectionState = self.ConnectionState.Connected
                            #send event
                            onConnection(connectionState)

                            self.startHeartbeat()
                            self.requestIframe()
                            #for(int i=74i<80i+1)
                            #queryUnk(i)
                            #print("Tello connected!")
                            continue
                        
                    cmdId = (received.bytes[5] or (received.bytes[6] << 8))

                    if(cmdId>=74 & cmdId<80):
                        print("XXXXXXXXCMD:" + cmdId)
                    
                    if (cmdId == 86):#state command
                        #update
                        state.set(received.bytes.Skip(9).ToArray())

                    
                    if (cmdId == 4176):#log header
                    
                        #just ack.
                        id = int.to_bytes(received.bytes, 9)
                        self.sendAckLog(cmdId, id)
                        #print(id)
                    
                    if (cmdId == 4177):#log data
                    
                        try:
                        
                            state.parseLog(received.bytes.Skip(10).ToArray())
                        except Exception as pex:
                        
                            print("parseLog error:" + pex.Message)
                        
                    
                    if (cmdId == 4178):#log config
                    
                        #todo. this doesnt seem to be working.

                        #id = BitConverter.ToUInt16(received.bytes, 9)
                        #n2 = BitConverter.ToInt32(received.bytes, 11)
                        #sendAckLogConfig(()cmdId, id,n2)

                        # dataStr = BitConverter.ToString(received.bytes.Skip(14).Take(10).ToArray()).Replace("-", " ")/*+"  "+pos*/


                        #print(dataStr)
                        pass
                    if (cmdId == 4185):#att angle response
                    
                        array = received.bytes.Skip(10).Take(4).ToArray()
                        f = float(array, 0)
                        print(f)
                    
                    if (cmdId == 4182):#max hei response
                    
                        # array = received.bytes.Skip(9).Take(4).Reverse().ToArray()
                        # f = BitConverter.ToSingle(array, 0)
                        #print(f)
                        if (received.bytes[10] != 10):
                            pass

                    
                    if (cmdId == 26):#wifi str command
                    
                        wifiStrength = received.bytes[9]
                        if(received.bytes[10]!=0):#Disturb?
                            pass
                    
                    if (cmdId == 53):#light str command
                        pass

                    if (cmdId == 98):#start jpeg.
                    
                        picFilePath = self.picPath + time.gmtime(0) + ".jpg"

                        start = 9
                        ftype = received.bytes[start]
                        start += 1
                        picBytesExpected = int.from_bytes(received.bytes, start)
                        if(picBytesExpected>picbuffer.Length):
                        
                            print("WARNING:Picture Too Big! " + picBytesExpected)
                            picbuffer = [picBytesExpected]
                        
                        picBytesRecived = 0
                        picChunkState = [(picBytesExpected/1024)+1] #calc based on size. 
                        picPieceState = [(picChunkState.Length / 8)+1]
                        picExtraPackets = 0#for debugging.
                        picDownloading = True

                        self.sendAckFileSize()
                    
                    if(cmdId == 99):#jpeg
                    
                        # dataStr = BitConverter.ToString(received.bytes.Skip(0).Take(30).ToArray()).Replace("-", " ")

                        start = 9
                        fileNum = int.from_bytes(received.bytes,start)
                        start += 2
                        pieceNum = int.from_bytes(received.bytes, start)
                        start += 4
                        seqNum = int.from_bytes(received.bytes, start)
                        start += 4
                        size = int.from_bytes(received.bytes, start)
                        start += 2

                        maxPieceNum = max(int(pieceNum), maxPieceNum)
                        if (not picChunkState[seqNum]):
                        
                            picbuffer = received.bytes.copy()
                            picBytesRecived += size
                            picChunkState[seqNum] = True

                            for p in range(len(picChunkState)) / 8:
                                done = True
                                for s in range(8):
                                
                                    if (not picChunkState[(p * 8) + s]):
                                    
                                        done = False
                                        break
                                    
                                
                                if (done & (not picPieceState[p])):
                                
                                    picPieceState[p] = True
                                    self.sendAckFilePiece(0, fileNum,p)
                                    #print("\nACK PN:" + p + " " + seqNum)
                                
                            
                            if (picFilePath != None & picBytesRecived >= picBytesExpected):
                            
                                picDownloading = False

                                self.sendAckFilePiece(1, 0, int(maxPieceNum))#todo.  check this. finalize

                                self.sendAckFileDone(int(picBytesExpected))

                                #HACK.
                                #Send file done cmdId to the update listener so it knows the picture is done. 
                                #hack.
                                onUpdate(100)
                                #hack.
                                #This is a hack because it is faking a message. And not a very good fake.
                                #HACK.

                                print("\nDONE PN:" + pieceNum + " max: " + maxPieceNum)

                                # #Save raw data minus sequence.
                                # using ( stream = new FileStream(picFilePath, FileMode.Append)):
                                #     stream.Write(picbuffer, 0, (int)picBytesExpected)
                                
                            
                        
                        else:
                        
                            picExtraPackets+1#for debugging.

                            #if(picBytesRecived >= picBytesExpected)
                            #    print("\nEXTRA PN:"+pieceNum+" max "+ maxPieceNum)
                        


                    
                    if (cmdId == 100):
                        pass


                    #send command to listeners. 
                    try:
                    
                        #fire update event.
                        onUpdate(cmdId)
                    
                    except Exception as ex:
                    
                        #Fixed. Update errors do not cause disconnect.
                        print("onUpdate error:" + ex.Message)
                        #break
                except Exception as eex:
                    print("Receive thread error:" + eex.Message)
                    self.disconnect()
                    break
                    
            

        videoServer =  (tello_ip, command_port)#this is incorrect

        async def wait_for_video(): 
            #print("video:1")
            started = False

            while (True):
            
                try:
                
                    if (token.IsCancellationRequested):#handle canceling thread.
                        break
                    received = await videoServer.Receive()
                    if (received.bytes[2] == 0 & received.bytes[3] == 0 & received.bytes[4] == 0 & received.bytes[5] == 1):#Wait for first NAL
                    
                        nal = (received.bytes[6] & 0x1f)
                        #if (nal != 0x01 & nal!=0x07 & nal != 0x08 & nal != 0x05)
                        #    print("NAL type:" +nal)
                        started = True
                    
                    if (started):
                        onVideoData(received.bytes)
                    

                
                except Exception as ex:
                
                    print("Video receive thread error:" + ex.Message)
                    #dont disconnect()
#                        break
                

    def startHeartbeat(self):
        cancelTokens = CancellationToken()
        token = cancelTokens

        #heartbeat.
        async def heartbeat():
        
            tick = 0
            while (True):
                try:
                
                    if (token.IsCancellationRequested):
                        break

                    if (self.connectionState == self.ConnectionState.Connected):#only send if not paused
                    
                        self.sendControllerUpdate()

                        tick+1
                        if ((tick % self.iFrameRate) == 0):
                            self.requestIframe()
                    
                    time.Sleep(50)#Often enough?
                
                except Exception as ex:
                
                    print("Heatbeat error:" + ex.Message)
                    if (ex.Message.StartsWith("Access denied") #Denied means app paused
                        & self.connectionState != self.ConnectionState.Paused):
                    
                        #Can this happen?
                        print("Heatbeat: access denied and not paused:" + ex.Message)

                        self.disconnect()
                        break
                    


                    if (not ex.Message.StartsWith("Access denied")):#Denied means app paused
                        self.disconnect()
                        break

    
    def startConnecting(self):
    
        #Thread to handle connecting.
        async def connecting():
        
            timeout = timedelta(3000)#3 second connection timeout
            while (True):
            
                try:
                    
                    if self.connectionState == self.ConnectionState.Disconnected:
                        self.connect()
                        lastMessageTime = time.gmtime(0)

                        self.startListeners()
                        
                        break
                    self.connectionState == self.ConnectionState.Connecting
                    self.connectionState == self.ConnectionState.Connected
                    elapsed = time.gmtime(0) - lastMessageTime
                    if (elapsed.Seconds > 2):#1 second timeout.
                    
                        print("Connection timeout :")
                        self.disconnect()
                        
                        break
                    if self.connectionState == self.ConnectionState.Paused:
                        lastMessageTime = time.gmtime(0)#reset timeout so we have time to recover if enabled. 
                        break
                    #source: https://stackoverflow.com/questions/92928/time-sleep-sleeps-thread-or-process
                    time.Sleep(500)
                
                except Exception as ex:
                
                    print("Connection thread error:" + ex.Message)
                
            
        

    

    class ControllerState():
        rx=0
        ry=0
        lx=0
        ly = 0
        speed = 0
        deadBand = 0.15
        def setAxis(self, lx,  ly, rx,  ry):
        
            # deadBand = 0.15f
            #this.rx = math.Abs(rx) < deadBand ? 0 : rx
            #this.ry = math.Abs(ry) < deadBand ? 0 : ry
            #this.lx = math.Abs(lx) < deadBand ? 0 : lx
            #this.ly = math.Abs(ly) < deadBand ? 0 : ly

            self.rx = rx
            self.ry = ry
            self.lx = lx
            self.ly = ly

            #print(rx + " " + ry + " " + lx + " " + ly + " SP:" + speed)
        
        def setSpeedMode(mode):
            speed = mode
            #print(rx + " " + ry + " " + lx + " " + ly + " SP:" + speed)
        
    
    controllerState = ControllerState()
    autoPilotControllerState = ControllerState()

    def Clamp( value,  min,  max):
        return (value < min) if True else (value > max)

    def sendControllerUpdate(self,state):
        controllerState = state()
        autoPilotControllerState = state()
        
        if (not controllerState.connected):
            return

        boost = 0
        if (controllerState.speed > 0):
            boost = 1

        # limit = 1#Slow down while testing.
        #rx = rx * limit
        #ry = ry * limit
        rx =controllerState.rx
        ry =controllerState.ry
        lx =controllerState.lx
        ly =controllerState.ly
        if (True):#Combine autopilot sticks.
        
            rx = self.Clamp(rx + autoPilotControllerState.rx, -1, 1)
            ry = self.Clamp(ry + autoPilotControllerState.ry, -1, 1)
            lx = self.Clamp(lx + autoPilotControllerState.lx, -1, 1)
            ly = self.Clamp(ly + autoPilotControllerState.ly, -1, 1)
        
        #print(controllerState.rx + " " + controllerState.ry + " " + controllerState.lx + " " + controllerState.ly + " SP:"+boost)
        packet = self.createJoyPacket(rx, ry, lx, ly, boost)
        try:
            self.Send(packet)
        except:
            pass

    

    cmdIdLookup = {
            '26': 'Wifi',#2 bytes. Strength, Disturb.
            '53': 'Light',#1 byte?
            '86': 'FlyData',
            '4176':'Data'#wtf?
        }

    #Create joystick packet from ing point axis.
    #Center = 0.0. 
    #Up/Right =1.0. 
    #Down/Left=-1.0. 
    def createJoyPacket( fRx,  fRy,  fLx,  fLy,  speed):
    
        #template joy packet.
        packet = { 0xcc, 0xb0, 0x00, 0x7f, 0x60, 0x50, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x12, 0x16, 0x01, 0x0e, 0x00, 0x25, 0x54 }

        axis1 = (660 * fRx + 1024)#RightX center=1024 left =364 right =-364
        axis2 = (660 * fRy + 1024)#RightY down =364 up =-364
        axis3 = (660 * fLy + 1024)#LeftY down =364 up =-364
        axis4 = (660 * fLx + 1024)#LeftX left =364 right =-364
        axis5 = (660 * speed + 1024)#Speed. 

        if (speed > 0.1):
            axis5 = 0x7fff

        packedAxis = (axis1 & 0x7FF) | ((axis2 & 0x7FF) << 11) | ((0x7FF & axis3) << 22) | ((0x7FF & axis4) << 33) | (axis5 << 44)
        packet[9] = ((int)(0xFF & packedAxis))
        packet[10] = ((int)(packedAxis >> 8 & 0xFF))
        packet[11] = ((int)(packedAxis >> 16 & 0xFF))
        packet[12] = ((int)(packedAxis >> 24 & 0xFF))
        packet[13] = ((int)(packedAxis >> 32 & 0xFF))
        packet[14] = ((int)(packedAxis >> 40 & 0xFF))

        #Add time info.		
        now = time.gmtime(0)
        packet[15] = now.Hour
        packet[16] = now.Minute
        packet[17] = now.Second
        packet[18] = (now.Millisecond & 0xff)
        packet[19] = (now.Millisecond >> 8)

        CRC.calcUCRC(packet, 4)#Not really needed.

        #calc crc for packet. 
        CRC.calcCrc(packet, packet.Length)

        return packet
    
        

        
    




import numpy as np
import base64
import cv2
#Type = 0(000) 8bit ASCII码(运行标准文本文档)
#Type = 1(001) 16bit GBK编码(运行标准文本文档)
#Tyep = 2(010) 8bit BASE64图片编码(运行标准JPEG)
#Type = 3(011) 24bit RGB三通道图片编码(运行标准BMP)
typeCheck = [8, 16, 8, 24]

#函数功能：制作图片编码头信息
def Make_Head(Length, TypeList, SizeList, Sizebit):
#参数：编码类型(int数组)，编码大小(int数组), 编码元素个数(int), 编码大小的位数(int一般是固定32)
#返回：头信息的二进制流(string)
    Finally = '0101010101010101'
    lengthBet = bin(Length).replace('0b', '')
    print(lengthBet)
    Finally += (8-len(lengthBet))*'0'
    Finally += lengthBet
    for i in range(len(TypeList)):
        Type = bin(TypeList[i]).replace('0b', '')
        Size = bin(SizeList[i]).replace('0b', '')
        SizeFinally = TypeFinally = ''
        TypeFinally += (3-len(Type))*'0'
        SizeFinally += (Sizebit-len(Size))*'0'
        TypeFinally += Type
        SizeFinally += Size
        Finally += (TypeFinally + SizeFinally)
    print("Finally = %s" %Finally)
    return Finally

#函数功能：制作编码图片
def Code_Pic(img, TypeList, SizeList, binaryStream):
#参数：图片(opencv图片对象), 编码类型(int), 要编码内容的二进制流(string)
#返回：编码后的图片(opencv图片对象)
    Head = Make_Head(len(TypeList), TypeList, SizeList, 32)
    binaryStream = Head + binaryStream
    x = y = 0
    for i in range(len(binaryStream)):
        if img[x][y][i%3]%2 != ord(binaryStream[i]) - ord('0'):
            if img[x][y][i%3] != 0:
                img[x][y][i%3] -= 1
            else:
                img[x][y][i%3] += 1
        if i%3 == 2:
            y += 1
            if y > img.shape[1]-1:
                x += 1
                y = 0
    return img

#函数功能: 将一个对象转化为Type指定类型的二进制流
def Change_Binary(Thing, Type):
#参数：要转换的对象(类型随意但需要对应Type值), 编码类型(int)
#返回：对应的二进制流(string)
    binaryStream = ''
    typeBit = typeCheck[Type]
    if Type == 0 or Type == 1:
        for i in Thing:
            bet = bin(ord(i)).replace('0b','')
            bet = (typeBit-len(bet))*'0' + bet
            binaryStream += bet
    if Type == 2:
        bytesList = cv2.imencode(".jpg", Thing)[1].tobytes()
        for i in bytesList:
            bet = bin(i).replace('0b', '')
            binaryStream += (8-len(bet))*'0'
            binaryStream += bet
        print(len(binaryStream))
    return binaryStream

#函数功能：返回图片编码头信息
def Read_HeadPic(img):
#参数: 图片(opencv图片对象)
#返回：编码正确判断(bool), 编码类型数组(string[]), 编码大小数组(string[])
    x = y = 0
    typeList = []
    sizeList = []
    Check = Check2 = ''
    for i in range(24):
        Check += chr(img[x][y][i%3]%2+ord('0'))
        if i%3 == 2:
            y += 1
            if y > img.shape[1]-1:
                x += 1
                y = 0
    if Check[0:16] == '0101010101010101':
        listSize = int(Check[16:24], 2)
        print(listSize)
        for i in range(24, 24+35*listSize):
            Check2 += chr(img[x][y][i%3]%2+ord('0'))
            if i%3 == 2:
                y += 1
                if y > img.shape[1]-1:
                    x += 1
                    y = 0
        for i in range(int(len(Check2)/35)):
           typeList.append(int(Check2[35*i:35*i+3], 2))
           sizeList.append(int(Check2[35*i+3:35*i+35], 2))
        print(typeList)
        print(sizeList)
        return 1, typeList, sizeList
    else:
        return 0, [], []

#函数功能：返回图片编码解码后的数据
def Encode_Pic(img, TypeList, SizeList):
#参数: 图片(opencv图片对象), 编码类型(int), 编码大小(int)
#返回：解码后的数据(类型随Type改变而改变)
    headSize = 24 + 35*len(TypeList)
    y = int(headSize/3)
    x = int(y/img.shape[1])
    y %= img.shape[1]
    for k in range(len(SizeList)):
        Data = ''
        Str = ''
        typeBit = typeCheck[TypeList[k]]
        for i in range(headSize, SizeList[k]+headSize):
            Data += chr(img[x][y][i%3]%2+ord('0'))
            if i%3 == 2:
                y += 1
                if y > img.shape[1]-1:
                    x += 1
                    y = 0
        if TypeList[k] == 0 or TypeList[k] == 1:
            for i in range(int(SizeList[k]/typeBit)):
                Str += chr(int(Data[typeBit*i:typeBit*i+typeBit], 2))
            return Str
        headSize += SizeList[k]

#函数功能：编码函数，用来隐写数据
def Picsubmit(img, string):    
#参数: 图片对象(cv2图片对象), 隐写数据(string)
#返回: 图片对象(cv2图片对象)
    binaryStream = ''
    typeList = []
    sizeList = []
    
    typeList.append(1)
    Thing = string
    binaryBet = Change_Binary(Thing, 1)
    binaryStream += binaryBet
    sizeList.append(len(binaryBet))

    if len(binaryStream) > img.shape[0]*img.shape[1]*3:
        print("too large")
    else:
        img = Code_Pic(img, typeList, sizeList, binaryStream)
    return img
    #cv2.imwrite('./Nar/Output/S.png', img2, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])

#函数功能：解码函数，用来反隐写数据
def Picsubmit2(img):
#参数: 图片对象(cv2图片对象)
#返回: 隐写数据(string)
    Check, TypeList, SizeList = Read_HeadPic(img)
    if Check == 0:
        print("该图片无隐藏编码或隐藏编码损坏")
        return ''
    else:
        return Encode_Pic(img, TypeList, SizeList)
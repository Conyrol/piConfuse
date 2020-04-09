import numpy as np
import shutil
import base64
import math
import cv2
import os

Pi = 3.1415926

#图片混淆类
class imgConfuseObject:
    
    #构造函数
    def __init__(self, img, xyList, allList, times, name, Type, string):
        self.img = img
        self.xyList = xyList     #记录打码矩阵点
        self.wDiv = allList[0]
        self.hDiv = allList[1]
        self.wDev = allList[2]
        self.hDev = allList[3]
        self.times = times       #混淆次数
        self.name = name         #名称
        self.type = Type         #类型记录
        self.string = string     #额外码
        #混淆 ———— 无额外码：图片条 0；隐写 1 | 有额外码 2
        #反混淆 ———— 无额外码：图片条 0；隐写 1 | 有额外码 2

    #函数功能：混淆函数
    def confuse(self):
        if self.type == '0':
            self.preOperate()
        if self.type == '1':
            pass

        strBet = str(self.img.shape[0]) + ',' + str(self.img.shape[1]) + '|'
        pointIndex = 0
        jZhi = 120
        while(pointIndex < len(self.xyList)):
            point1 = self.xyList[pointIndex]
            pointIndex += 1
            point2 = self.xyList[pointIndex]
            pointIndex += 1

            strBet += str(point1[0]) + ',' + str(point1[1]) + ';' + str(point2[0]) + ',' + str(point2[1])
            if pointIndex != len(self.xyList):
                strBet += ';'
            if self.type == '0':
                self.img[0, point1[0]:point2[0]] += int(jZhi)
                self.img[point1[1]:point2[1], 0] += int(jZhi)
            
            jZhi /= 2
            for k in range(self.times):
                wDivCopy = 2 * Pi * self.wDiv[k] / self.img.shape[1]
                hDivCopy = 2 * Pi * self.hDiv[k] / self.img.shape[0]
                for i in range(point1[0], point2[0]):
                    self.img[point1[1]:point2[1], i, :3] = (256 - int((math.sin(wDivCopy * (i + self.wDev[k])) + 1)*128) + self.img[point1[1]:point2[1], i, :3]) % 256
                for j in range(point1[1], point2[1]):
                    self.img[j, point1[0]:point2[0], :3] = (256 - int((math.sin(hDivCopy * (j + self.hDev[k])) + 1)*128) + self.img[j, point1[0]:point2[0], :3]) % 256
        
        strBet += '|' + str(self.times) + '|'
        for i in range(self.times):
            strBet += str(self.wDiv[i]) + ',' + str(self.hDiv[i]) + ',' + str(self.wDev[i]) + ',' + str(self.hDev[i])
            if i != self.times - 1:
                strBet += ';'
        strBytes = strBet.encode("utf-8")
        strBase64 = base64.b64encode(strBytes)
        self.string = strBase64.decode("utf-8")
    
    #函数功能：反混淆函数
    def unconfuse(self):
        if self.type == '0':
            self.readList()
        if self.type == '1':
            self.readAllList()
        if self.type == '2':
            self.readAllList()
        pointIndex = 0
        while(pointIndex < len(self.xyList)):
            point1 = self.xyList[pointIndex]
            pointIndex += 1
            point2 = self.xyList[pointIndex]
            pointIndex += 1
            for k in range(self.times):
                wDivCopy = 2 * Pi * self.wDiv[self.times-k-1] / self.img.shape[1]
                hDivCopy = 2 * Pi * self.hDiv[self.times-k-1] / self.img.shape[0]
                for j in range(point1[1], point2[1]):
                    self.img[j, point1[0]:point2[0], :3] = (self.img[j, point1[0]:point2[0], :3] + int((math.sin(hDivCopy * (j + self.hDev[self.times-k-1])) + 1)*128)) % 256
                for i in range(point1[0], point2[0]):
                    self.img[point1[1]:point2[1], i, :3] = (self.img[point1[1]:point2[1], i, :3] + int((math.sin(wDivCopy * (i + self.wDev[self.times-k-1])) + 1)*128)) % 256
        if self.type == '0':
            self.img = self.img[2:self.img.shape[0], 2:self.img.shape[1]]

    #函数功能：对于图片条形式的编码，进行点位信息读取
    def readList(self):
        w, h = self.img.shape[:2]
        jZhi = 120
        while(jZhi >= 15):
            x1 = x2 = y1 = y2 = -1
            B1 = 1
            B2 = 0
            for i in range(h):
                if self.img[0, i, 1] > jZhi - 10 and B1:
                    x1 = i
                    B1 = 0
                    B2 = 1
                if self.img[0, i, 1] < jZhi - 10 and B2:
                    x2 = i
                    break
            B1 = 1
            B2 = 0
            for i in range(w):
                if self.img[i, 0, 1] > jZhi - 10 and B1:
                    y1 = i
                    B1 = 0
                    B2 = 1
                if self.img[i, 0, 1] < jZhi - 10 and B2:
                    y2 = i
                    break
            self.img[0, x1:x2] -= jZhi
            self.img[y1:y2, 0] -= jZhi
            jZhi = int(jZhi/2)
            if x1 != -1 and y2 != -1:
                self.xyList.append((x1, y1))
                self.xyList.append((x2, y2))
        print(self.xyList)
    
    #函数功能：预处理，对于图片条形式编码，提前在图片中加入图片条
    def preOperate(self):
        imgBet = np.zeros([self.img.shape[0]+2, self.img.shape[1]+2, self.img.shape[2]], np.uint8)
        imgBet[1,:] = 255
        imgBet[:,1] = 255
        imgBet[0,:] = 0
        imgBet[:,0] = 0
        imgBet[2:self.img.shape[0]+2, 2:self.img.shape[1]+2] = self.img
        self.img = imgBet
    
    #函数功能：对于隐写编码或额外码，根据编码字符串进行全部信息的读取
    def readAllList(self):
        self.xyList = []
        self.wDiv = []
        self.hDiv = []
        self.wDev = []
        self.hDev = []
        strList = self.string.split('|')
        height = int(strList[0].split(',')[0])
        width = int(strList[0].split(',')[1])
        print(height, width)
        if height != self.img.shape[0] or width != self.img.shape[1]:
            print("你的图片已经被改变了大小，这个过程再进行反混淆会损失数据")
        xyListBet = strList[1].split(';')
        for i in xyListBet:
            self.xyList.append((int(int(i.split(',')[0]) * self.img.shape[0]/height), int(int(i.split(',')[1]) * self.img.shape[1]/width)))
        self.times = int(strList[2])
        confuseList = strList[3].split(';')
        for i in confuseList:
            i = i.split(',')
            self.wDiv.append(int(i[0]))
            self.hDiv.append(int(i[1]))
            self.wDev.append(int(i[2]))
            self.hDev.append(int(i[3]))
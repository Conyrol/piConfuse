import numpy as np
import steganography
import confuse
import shutil
import base64
import math
import cv2
import os

#定义画板事件
def eventCall(event, x, y, flags, param):
    winHeight, winWidth = param.img.shape[:2]
    hwScale = winHeight / winWidth
    if event == cv2.EVENT_LBUTTONDOWN and flags == cv2.EVENT_FLAG_CTRLKEY + cv2.EVENT_LBUTTONDOWN:
        if len(param.xyList) == 8 and param.type == '0':
            print("已经达到可识别的最多矩阵点个数，接下来的点将不会记录")
        else:
            if param.type == '0':
                param.xyList.append((x + 2, y + 2))
            else:
                param.xyList.append((x, y))
            print("确认第%d个矩阵点(%d, %d)" %(len(param.xyList), x, y))
    elif event == cv2.EVENT_MOUSEWHEEL:
        if flags < 0:
            dWidth = 30
            dHeight = int(hwScale*30)
        if flags > 0:
            dWidth = -30
            dHeight = -int(hwScale*30)
        winWidth += dWidth
        winHeight += dHeight
        cv2.resizeWindow('show', int(winWidth), int(winHeight))

def init():
    if not os.path.exists('./confIn'):
        os.mkdir('./confIn')
    if not os.path.exists('./confOut'):
        os.mkdir('./confOut')
    if not os.path.exists('./unconfIn'):
        os.mkdir('./unconfIn')
    if not os.path.exists('./unconfOut'):
        os.mkdir('./unconfOut')
    if not os.path.exists('./confIn/over'):
        os.mkdir('./confIn/over')
    if not os.path.exists('./unconfIn/over'):
        os.mkdir('./unconfIn/over')

if __name__ == "__main__":
    init()
    imgList = []
    string = ''
    allList = [[17, 207], [47, 131], [0, 0], [0, 0]]  #宽度细分, 高度细分, 宽度偏移, 高度偏移
    #allList = [[17], [47], [0], [0]] 
    a = input("1.混淆图片 —— 2.反混淆图片 (1/2)\n")
    if a == '1':
        print("目前定义混淆次数为 %d：" %len(allList[0]))
        for k in range(len(allList[0])):
            print("第 %d 组混淆信息：" %k)
            print("宽度细分：%d | 高度细分：%d | 宽度偏移：%d | 高度偏移：%d" %(allList[0][k], allList[1][k], allList[2][k], allList[3][k]))
        a = input("\n2.使用额外码(反混淆需要指定额外码反混淆)\n1.不使用额外码(使用隐写)\n0.不使用额外码(使用图片码，最大混淆矩阵个数为4)\n")
        maxWinHeight = 800
        maxWinWidth = 1200
        fileList = os.listdir('./confIn')
        for i in fileList:
            if '.png' in i:
                name = i.replace('.png', '')
            elif '.jpg' in i:
                name = i.replace('.jpg', '')
            else:
                if i != 'over':
                    print('cannot read %s' %i)
                continue
            print('read %s' %i)
            img = cv2.imread('./confIn/' + i, cv2.IMREAD_UNCHANGED)
            imgList.append(confuse.imgConfuseObject(img, [], allList, len(allList[0]), name, a, ''))
            shutil.copy('./confIn/' + i, './confIn/over/' + i)
            os.remove('./confIn/' + i)
            
        for i in imgList:
            print("confuse %s" %i.name)
            img = i.img
            winHeight, winWidth = img.shape[:2]
            hwScale = winHeight / winWidth
            if winHeight > maxWinHeight:
                winWidth = winWidth * maxWinHeight / winHeight
                winHeight = maxWinHeight
            if winWidth > maxWinWidth:
                winHeight = winHeight * maxWinWidth / winWidth
                winWidth = maxWinWidth
            cv2.namedWindow('show', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('show', int(winWidth), int(winHeight))
            cv2.imshow('show', img)
            cv2.setMouseCallback('show', eventCall, i)
            cv2.waitKey(0)
            i.confuse()
            if a == '1':
                i.img = steganography.Picsubmit(i.img, i.string)
            cv2.imwrite('./confOut/' + i.name + '.png', i.img, [int(cv2.IMWRITE_PNG_COMPRESSION), 5])
            if a == '2':
                print(i.string)
        
    elif a == '2':
        a = input("2.使用额外码\n1.不使用额外码(隐写解码)\n0.不使用额外码(图片码解码)\n")
        if a == '2':
            string = input("输入额外码：")
            string = base64.b64decode(string).decode("utf-8")
            print(string)
        fileList = os.listdir('./unconfIn')
        for i in fileList:
            if '.png' in i:
                name = i.replace('.png', '')
            elif '.jpg' in i:
                name = i.replace('.jpg', '')
            else:
                if i != 'over':
                    print('cannot read %s' %i)
                continue
            print('read %s' %i)
            img = cv2.imread('./unconfIn/' + i, cv2.IMREAD_UNCHANGED)
            imgList.append(confuse.imgConfuseObject(img, [], allList, len(allList[0]), name, a, string))
            shutil.copy('./unconfIn/' + i, './unconfIn/over/' + i)
            os.remove('./unconfIn/' + i)
        
        print("总共 %d 张图片" %len(imgList))
        for i in imgList:
            print('unconfuse %s' %i.name)
            try:
                if a == '1':
                    i.string = base64.b64decode(steganography.Picsubmit2(i.img)).decode("utf-8")
                i.unconfuse()
            except:
                print("%s 反混淆失败，可能是图片格式损坏，请使用原图，不要用压缩过的" %i.name)
            cv2.imwrite('./unconfOut/' + i.name + '.png', i.img, [int(cv2.IMWRITE_PNG_COMPRESSION), 5])
    os.system('pause')
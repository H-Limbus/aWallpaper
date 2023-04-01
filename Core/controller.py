#  -*- coding: utf-8 -*-
# @Author  :  Limbus
#  @file   :  controller.py
#  @Date   :  23/3/2023 AM 3:40
# @Github  :  https://github.com/H-Limbus

import os
import ctypes
import asyncio
import time
from shutil import move, copy
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from configure.Config import ConfigFunc
from spider.bing import bingDownload
from spider.ThreeGbizhi import ThreeGbizhiDownload
from spider.tenwallpaper import TenwallpaperDownload
from spider.gugong import gugongDownload


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.configure = ConfigFunc()
        self.SCREEN_WIDTH = QApplication.desktop().width()
        self.SCREEN_HEIGHT = QApplication.desktop().height()
        self.APP_WIDTH = 1200
        self.APP_HEIGHT = 850
        self.imageFilePath = self.configure['global'].get('imagemainfile')
        self.imagePage = 1
        self.loveImageFile = self.configure['global'].get('imagelovefile')
        self.BUTTON = "QPushButton{background-color: rgba(255,255,255, 0.1); color: rgb(255,255," \
                      "255); border-radius: 10px; border: 2px groove gray;border-style: outset;} " \
                      "QPushButton::pressed{ border: 3px groove gray;border-style: outset;}"
        self.QSSCHECKBOXTAG = 'QCheckBox{background-color: rgba(255,255,255,0.1); border-radius: 5px; color: #FFFFFF}' \
                           'QCheckBox::checked{background-color: rgba(225,225,225,0.7);color: #000000;} QCheckBox::indicator {width: 0px; height: 40px;}'
        self.PATTERN = "background-color: rgba(255,255,255, 0.1); color: rgb(255,255," \
                       "255); border-radius: 10px;"
        self.QRADIOBUTTON = 'QCheckBox{background-color: rgba(255,255,255,0); border-radius: 1px; color: rgba(255,255,255,0)} ' \
                           'QCheckBox::checked{background-color: rgba(0,0,0,0.6);} QCheckBox::indicator {width: 0px; height: 115px;}'
        self.typeTags = eval(self.configure['tag'].get('tags'))
        self.loop = asyncio.get_event_loop()
        self.nameList = {
            '风景': 'scenery',
            '人物': 'person',
            '动漫': 'cartoon',
            '简约': 'brief',
            '机械': 'machinery',
            '影视': 'movie',
            '其他': 'other'
        }
        self.initUI()

    def initUI(self):
        self.setWindowTitle('aWallpaper')
        self.setGeometry((self.SCREEN_WIDTH - self.APP_WIDTH) // 2, (self.SCREEN_HEIGHT - self.APP_HEIGHT) // 2, self.APP_WIDTH, self.APP_HEIGHT)
        self.setFixedSize(self.APP_WIDTH, self.APP_HEIGHT)
        self.setObjectName("MainWindow")
        self.setWindowIcon(QIcon(self.configure['global'].get("ICON") + "softwareIcon.png"))
        self.setStyleSheet("#MainWindow{background-image:url(" + self.configure['global'].get("ICON") + "background.jpg)}")
        self.mainWindow = QWidget(self)
        self.mainLayout = QGridLayout()

        # 创建左侧多选布局
        leftWindow = QWidget()
        leftLayout, checkBoxList = self.LeftTagsLayout()
        leftWindow.setLayout(leftLayout)
        self.mainLayout.addWidget(leftWindow, 2, 1, 10, 1)

        # 创建右侧预览布局
        self.rightWindow = QWidget()
        self.rightWindow.setStyleSheet('background-color: rgba(255,255,255,0.1); border-radius: 15px;')
        self.rightViewLayout = QGridLayout()
        self.rightWindow.setLayout(self.rightViewLayout)
        self.showImage(self.imageFilePath)

        # 创建上部搜索框布局
        topWindow = QWidget()
        topLayout = self.TopSearchLayout(checkBoxList)

        # 创建下方布局
        underWindow = QWidget()
        underLayout = self.UnderButtonLayout(checkBoxList)

        nextPageButton, previousPageButton = self.CreateTwoButton()

        self.mainLayout.addWidget(nextPageButton, 17, 13, 1, 1)
        self.mainLayout.addWidget(previousPageButton, 17, 2, 1, 1)

        underWindow.setLayout(underLayout)
        topWindow.setLayout(topLayout)

        self.mainLayout.addWidget(topWindow, 0, 0, 1, 15)
        self.mainLayout.addWidget(self.rightWindow, 2, 2, 10, 12)
        self.mainLayout.addWidget(underWindow, 18, 2, 1, 12)

        # 将布局添加到整体布局
        self.mainWindow.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWindow)

    def TopSearchLayout(self, checkBoxList):
        topSearchLayout = QHBoxLayout()
        topSearchBar = QLineEdit()
        topSearchBar.setFixedSize(800, 35)
        topSearchBar.setFont(QFont('Times', 12, QFont.Bold))
        topSearchBar.setStyleSheet(self.PATTERN)
        topSearchBar.setPlaceholderText("请输入你想要查找的壁纸")
        topSearchBar.returnPressed.connect(lambda: self.run(checkBoxList, topSearchBar.text()))
        searchButton = QPushButton()
        searchButton.setFixedSize(80, 40)
        searchButton.setText("搜索")
        searchButton.setStyleSheet(self.BUTTON)
        searchButton.setFont(QFont('Times', 12, QFont.Bold))
        searchButton.clicked.connect(lambda: self.run(checkBoxList, topSearchBar.text()))
        topSearchLayout.addWidget(topSearchBar, 0, Qt.AlignTop)
        topSearchLayout.addWidget(searchButton, 0, Qt.AlignTop)
        return topSearchLayout

    def LeftTagsLayout(self):
        leftTagsLayout = QVBoxLayout()
        checkBoxList = []
        leftTagsLayout.setSpacing(30)
        for item in self.typeTags:
            tag = QCheckBox()
            tag.setFixedSize(120, 40)
            tag.setFont(QFont('Times', 15, QFont.Bold))
            tag.setStyleSheet(self.QSSCHECKBOXTAG)
            tag.setText("  " + item + "  ")
            checkBoxList.append(tag)
            leftTagsLayout.addWidget(tag)
        leftTagsLayout.addStretch(0)
        return leftTagsLayout, checkBoxList

    def UnderButtonLayout(self, checkBoxList):
        underLayout = QHBoxLayout()
        for item in ['自动更换', '更换壁纸', '清除缓存', '加入喜欢']:
            Button = QPushButton()
            Button.setFixedSize(90, 50)
            Button.setFont(QFont('Times', 11, QFont.Bold))
            Button.setText(item)
            Button.setStyleSheet(self.BUTTON)
            if item == '更换壁纸':
                Button.clicked.connect(lambda: self.ChangeWallpaper(self.getImageID(self.imageFilePath)))
            elif item == '自动更换':
                Button.clicked.connect(lambda: self.AutoChange())
            elif item == '清除缓存':
                Button.clicked.connect(lambda: self.ClearCache())
            elif item == '加入喜欢':
                Button.clicked.connect(lambda: self.joinMylove())
            else:
                pass
            underLayout.addWidget(Button)
        return underLayout

    def CreateTwoButton(self):
        nextPageButton = QPushButton()
        nextPageButton.setFixedSize(32, 32)
        nextPageButton.setStyleSheet(
        'background-image: url(' + self.configure['global'].get('ICON') + 'next.png); background-color: rgba(255,255,255,0)')
        nextPageButton.clicked.connect(lambda: self.TurnPage(1))

        previousPageButton = QPushButton()
        previousPageButton.setFixedSize(32, 32)
        previousPageButton.setStyleSheet(
        'background-image: url(' + self.configure['global'].get('ICON') + 'previous.png); background-color: rgba(255,255,255,0)')
        previousPageButton.clicked.connect(lambda: self.TurnPage(-1))
        return nextPageButton, previousPageButton

    def messageBoxInit(self, message):
        messageBox = QMessageBox(self.mainWindow)
        messageBox.setIconPixmap(QPixmap(self.configure['global'].get('ICON') + 'messageIcon.png'))
        messageBox.setWindowTitle('你来这儿干什么？')
        messageBox.setText(message)
        messageBox.show()

    def showImage(self, path):
        if len(self.getImageID(path)):
            self.imageSelectedList = []
            for i in range(self.rightViewLayout.count()):  # 每次加载先清空内容，避免layout里堆积label
                self.rightViewLayout.itemAt(i).widget().deleteLater()
            start, end = (self.imagePage-1)*20, self.imagePage*20

            if start <= len(self.getImageID(path)) < end:
                end = len(self.getImageID(path))
            else:
                pass
            columns, rows = 0, 0
            for index, imageName in enumerate(self.getImageID(path)[start:end]):
                self.imageLabel = QLabel()
                imageCheckBox = QCheckBox()
                imageCheckBox.setFixedSize(205, 115)
                imageCheckBox.setFont(QFont('Times', 15, QFont.Bold))
                imageCheckBox.setStyleSheet(self.QRADIOBUTTON)
                imageCheckBox.setText(str(index) + "                              ")
                self.imageLabel.setPixmap(QPixmap(path + imageName).scaled(205, 115))
                if columns <= 3:
                    self.rightViewLayout.addWidget(self.imageLabel, rows, columns, 1, 1)
                    self.rightViewLayout.addWidget(imageCheckBox, rows, columns, 1, 1)
                else:
                    columns = 0
                    rows += 1
                    self.rightViewLayout.addWidget(self.imageLabel, rows, columns, 1, 1)
                    self.rightViewLayout.addWidget(imageCheckBox, rows, columns, 1, 1)
                columns += 1
                self.imageSelectedList.append(imageCheckBox)

    def getImageID(self, path):
        return [_ for _ in os.listdir(path) if '.jpg' in _ or 'png' in _ or 'jpeg' in _]

    def TurnPage(self, pagePreOrNext):
        self.imagePage += pagePreOrNext
        if self.imagePage <= 0 or (self.imagePage-1)*20 >= len(self.getImageID(self.imageFilePath)):
            self.imagePage -= pagePreOrNext
            pass
        else:
            self.showImage(self.imageFilePath)

    def ChangeWallpaper(self, filePathID):
        selectImageIndexList = [_.text() for _ in self.imageSelectedList if _.isChecked()]
        if len(selectImageIndexList) == 0:
            self.messageBoxInit('你没有选中图片哦！')
        elif len(selectImageIndexList) > 1:
            self.messageBoxInit('你选择的图片太多了！')
        else:
            for i in selectImageIndexList:
                try:
                    fp = self.imageFilePath + filePathID[(self.imagePage-1)*20 + int(i)]
                except:
                    filePathID = self.getImageID(self.loveImageFile)
                    fp = self.loveImageFile + filePathID[(self.imagePage - 1) * 20 + int(i)]
                ctypes.windll.user32.SystemParametersInfoW(20, 0, fp.replace('\\\\', '\\'), 3)

    def run(self, checkBoxList, searchSyntax):
        tagsList = []
        if self.CheckTagsIsClicked(checkBoxList):
            for _ in [i.text().replace(" ", "").strip() for i in checkBoxList if i.isChecked()]:
                temp = eval(self.configure['wallpaper'][self.nameList[_] + 'List'])
                tagsList += temp
            if searchSyntax != '':
                for webName in set(tagsList):
                    if webName == 'bing':
                        self.bingSearchThread = mySearchThread(searchSyntax, webName)
                        # self.bingSearchThread.searchThreadSignal.connect(self.test)
                        self.bingSearchThread.start()
                    elif webName == 'ThreeGbizhi':
                        self.GbizhisearchThread = mySearchThread(searchSyntax, webName)
                        # self.GbizhisearchThread.searchThreadSignal.connect(self.test)
                        self.GbizhisearchThread.start()
                    elif webName == 'Tenwallpaper':
                        self.TenwallpaperSearchThread = mySearchThread(searchSyntax, webName)
                        # self.TenwallpaperSearchThread.searchThreadSignal.connect(self.test)
                        self.TenwallpaperSearchThread.start()
                    elif webName == 'gugong':
                        self.gugongSearchThread = mySearchThread(searchSyntax, webName)
                        # self.gugongSearchThread.searchThreadSignal.connect(self.test)
                        self.gugongSearchThread.start()
                    else:
                        pass
            else:
                for webName in set(tagsList):
                    if webName == 'bing':
                        self.bingSearchThread = mySearchThread(webName, webName)
                        # self.bingSearchThread.searchThreadSignal.connect(self.test)
                        self.bingSearchThread.start()
                    elif webName == 'ThreeGbizhi':
                        self.GbizhisearchThread = mySearchThread(webName, webName)
                        # self.GbizhisearchThread.searchThreadSignal.connect(self.test)
                        self.GbizhisearchThread.start()
                    elif webName == 'Tenwallpaper':
                        self.TenwallpaperSearchThread = mySearchThread(webName, webName)
                        # self.TenwallpaperSearchThread.searchThreadSignal.connect(self.test)
                        self.TenwallpaperSearchThread.start()
                    elif webName == 'gugong':
                        self.gugongSearchThread = mySearchThread(searchSyntax, webName)
                        # self.gugongSearchThread.searchThreadSignal.connect(self.test)
                        self.gugongSearchThread.start()
                    else:
                        pass
        else:
            self.messageBoxInit('你没有选中标签哦\t\n  我怎么搜呢？')
        self.showImage(self.imageFilePath)

    def CheckTagsIsClicked(self, checkBoxList):
        if len([_ for _ in checkBoxList if _.isChecked()]) == 0:
            return False
        else:
            return True

    def AutoChange(self):
        self.autoChangeThread = AutoChangeWallpaper(self.loveImageFile)
        self.autoChangeThread.start()


    def ClearCache(self):
        for i in os.listdir(self.imageFilePath):
            os.remove(self.imageFilePath + i)
        self.messageBoxInit('清理完成！')
        self.showImage(self.imageFilePath)

    def joinMylove(self):
        selectImageIndexList = [_.text().strip() for _ in self.imageSelectedList if _.isChecked()]
        _ = os.listdir(self.imageFilePath)
        if len(selectImageIndexList) == 0:
            self.messageBoxInit('没有选中图片哦！')
            return
        else:
            for fileName in selectImageIndexList:
                copy(self.imageFilePath + _[(self.imagePage-1)*20+int(fileName)], self.loveImageFile + _[(self.imagePage-1)*20+int(fileName)])
        self.messageBoxInit('添加成功。')

    def test(self, sec):
        print(sec)


class mySearchThread(QThread):

    searchThreadSignal = pyqtSignal(str)

    def __init__(self, searchSyntax, webName):
        super(mySearchThread, self).__init__()
        self.searchSyntax = searchSyntax
        self.webName = webName

    def run(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        if self.webName == 'bing':
            bingDownload(self.searchSyntax)
        elif self.webName == 'ThreeGbizhi':
            ThreeGbizhiDownload(self.searchSyntax)
        elif self.webName == 'Tenwallpaper':
            TenwallpaperDownload(self.searchSyntax)
        elif self.webName == 'gugong':
            gugongDownload(self.searchSyntax)
        else:
            return
        self.searchThreadSignal.emit(f'{self.webName}搜索下载完成。')


class AutoChangeWallpaper(QThread):
    autoChangeSignal = pyqtSignal()

    def __init__(self, path):
        super(AutoChangeWallpaper, self).__init__()
        self.path = path

    def run(self):
        loveImageNameList = os.listdir(self.path)
        loveImageNum = len(loveImageNameList)
        if loveImageNum == 0:
            return
        point = 0
        while 1:
            fp = self.path + loveImageNameList[point]
            ctypes.windll.user32.SystemParametersInfoW(20, 0, fp.replace('\\\\', '\\'), 3)
            if point == loveImageNum - 1:
                point = 0
            else:
                point += 1
            time.sleep(int(ConfigFunc()['global'].get('changetime')))


#  -*- coding: utf-8 -*-
# @Author  :  Limbus
#  @file   :  Config.py
#  @Date   :  23/3/2023 PM 7:48
# @Github  :  https://github.com/H-Limbus

from configparser import ConfigParser


def ConfigFunc():
    configFilePath = 'F://ProgramFiles/PyCharm Files/aWallpaper/config.ini'
    configure = ConfigParser()
    configure.read(configFilePath, encoding='utf-8')
    # print(config['wallpaperType']['scenery'])
    return configure

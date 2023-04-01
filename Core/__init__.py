#  -*- coding: utf-8 -*-
# @Author  :  Limbus
#  @file   :  __init__.py
#  @Date   :  23/3/2023 AM 3:39
# @Github  :  https://github.com/H-Limbus


import os
from configure.Config import ConfigFunc

config = ConfigFunc()['global']
for i in ['imagelovefile', 'imagemainfile']:
    path = config.get(i)
    if not os.path.exists(path):
        os.makedirs(path)
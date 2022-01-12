# -*- coding: gb18030 -*-

"""
实现不同语言版本的小地图界面

2010.05.20: writen by pengju
"""

from guis import *
from AbstractTemplates import MultiLngFuncDecorator
from guis.common.PyGUI import PyGUI

class deco_guiMinMapNavigateTexture( MultiLngFuncDecorator ) :
	@staticmethod
	def locale_big5( SELF ) :
		"""
		获取“自动寻路”按钮贴图
		"""
		return "guis/general/minimap/autorunbtn_big5.dds"

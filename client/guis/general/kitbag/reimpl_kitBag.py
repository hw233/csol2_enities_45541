# -*- coding: gb18030 -*-

"""
实现不同语言版本的背包界面

2010.05.15: writen by pengju
"""

from guis import *
from AbstractTemplates import MultiLngFuncDecorator
from guis.common.PyGUI import PyGUI

class deco_guiKitBagGetGUI( MultiLngFuncDecorator ) :
	@staticmethod
	def locale_big5( SELF ) :
		"""
		读取UI文件
		"""
		return GUI.load( "guis/general/kitbag/kitbag_big5.gui" )

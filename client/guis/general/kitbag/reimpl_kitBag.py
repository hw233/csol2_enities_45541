# -*- coding: gb18030 -*-

"""
ʵ�ֲ�ͬ���԰汾�ı�������

2010.05.15: writen by pengju
"""

from guis import *
from AbstractTemplates import MultiLngFuncDecorator
from guis.common.PyGUI import PyGUI

class deco_guiKitBagGetGUI( MultiLngFuncDecorator ) :
	@staticmethod
	def locale_big5( SELF ) :
		"""
		��ȡUI�ļ�
		"""
		return GUI.load( "guis/general/kitbag/kitbag_big5.gui" )

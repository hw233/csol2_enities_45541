# -*- coding: gb18030 -*-

"""
ʵ�ֲ�ͬ���԰汾��С��ͼ����

2010.05.20: writen by pengju
"""

from guis import *
from AbstractTemplates import MultiLngFuncDecorator
from guis.common.PyGUI import PyGUI

class deco_guiMinMapNavigateTexture( MultiLngFuncDecorator ) :
	@staticmethod
	def locale_big5( SELF ) :
		"""
		��ȡ���Զ�Ѱ·����ť��ͼ
		"""
		return "guis/general/minimap/autorunbtn_big5.dds"

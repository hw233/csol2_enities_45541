# -*- coding: gb18030 -*-

"""
ʵ�ֲ�ͬ���԰汾��״̬��ͼ

2010.05.24: writen by pengju
"""

from AbstractTemplates import MultiLngFuncDecorator

class deco_guiStatusText( MultiLngFuncDecorator ) :
	"""
	��ȡ�Զ�ս�������Զ�Ѱ·����UI
	"""
	@staticmethod
	def locale_big5( SELF, status ) :
		"""
		��ȡ�Զ�ս�������Զ�Ѱ·����UI
		"""
		if status == "autoFight":
			return "guis/general/autofightwindow/autoFightState_big5.gui"
		elif status == "autoRun":
			return "guis/tooluis/navigateWord/navigateWord_big5.gui"
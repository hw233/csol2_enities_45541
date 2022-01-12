# -*- coding: gb18030 -*-

"""
实现不同语言版本的状态贴图

2010.05.24: writen by pengju
"""

from AbstractTemplates import MultiLngFuncDecorator

class deco_guiStatusText( MultiLngFuncDecorator ) :
	"""
	获取自动战斗或者自动寻路文字UI
	"""
	@staticmethod
	def locale_big5( SELF, status ) :
		"""
		获取自动战斗或者自动寻路文字UI
		"""
		if status == "autoFight":
			return "guis/general/autofightwindow/autoFightState_big5.gui"
		elif status == "autoRun":
			return "guis/tooluis/navigateWord/navigateWord_big5.gui"
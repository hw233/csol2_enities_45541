# -*- coding: gb18030 -*-

# implement SystemButton
# by ganjinxing 2010-01-05

from guis import *
from guis.controls.Button import Button
from guis.common.PyGUI import PyGUI

class SystemButton( Button ) :

	def __init__( self, button, pyBinder = None ) :
		Button.__init__( self, button, pyBinder )

		self.__pyIcon = PyGUI( button.icon )
		self.__orgIconPos = self.__pyIcon.pos


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def setStateView_( self, state ) :
		"""
		设置指定状态下的外观表现
		"""
		if state == UIState.DISABLE :
			self.setDisableView_()
		else:
			self.materialFX = "BLEND"
			if state == UIState.HIGHLIGHT :
				self.__pyIcon.pos = self.__orgIconPos
				self.gui.hlBg.visible = True
			elif state == UIState.PRESSED :
				self.__pyIcon.left = self.__orgIconPos[0] + 1
				self.__pyIcon.top = self.__orgIconPos[1] + 1
				self.gui.hlBg.visible = False
			else :
				self.__pyIcon.pos = self.__orgIconPos
				self.gui.hlBg.visible = False

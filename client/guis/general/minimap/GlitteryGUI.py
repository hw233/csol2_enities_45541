# -*- coding: gb18030 -*-
#
# mail flag
# 小地图闪烁标记
# written by gjx 2009-05-16
#为了实现鼠标信息提示 把邮件提示图标改为继承Control modified by姜毅

from guis import *
from guis.controls.Control import Control
from guis.otheruis.AnimatedGUI import AnimatedGUI


class GlitteryGUI( Control, AnimatedGUI ):

	def __init__( self, gui ) :
		AnimatedGUI.__init__( self, gui )
		Control.__init__( self, gui )
		self.crossFocus = True


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def hide( self ) :
		"""
		隐藏掉
		"""
		self.stopPlay_()
		self.visible = False

	def startFlash( self ) :
		"""
		闪烁
		"""
		self.playAnimation()
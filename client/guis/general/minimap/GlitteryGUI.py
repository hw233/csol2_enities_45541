# -*- coding: gb18030 -*-
#
# mail flag
# С��ͼ��˸���
# written by gjx 2009-05-16
#Ϊ��ʵ�������Ϣ��ʾ ���ʼ���ʾͼ���Ϊ�̳�Control modified by����

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
		���ص�
		"""
		self.stopPlay_()
		self.visible = False

	def startFlash( self ) :
		"""
		��˸
		"""
		self.playAnimation()
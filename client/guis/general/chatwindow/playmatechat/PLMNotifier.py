# -*- coding: gb18030 -*-

# ������Ϣ��ʾ��
# written by gjx 2010-06-17

from guis import *
from guis.common.RootGUI import RootGUI

class PLMNotifier( RootGUI ) :

	def __init__( self ) :
		wnd = GUI.load( "guis/general/chatwindow/playmatechat/notifier.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.movable_ = False
		self.escHide_ = False
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "BOTTOM"

		self.__shader = GUI.AlphaShader()				# ���һ��shader
		self.gui.addShader( self.__shader )
		self.__shader.value = 1.0
		self.__shader.speed = 0.8
		self.__flashCBID = 0

		self.visible = False
		self.addToMgr()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __startFlash( self ) :
		"""
		��ʼ��˸
		"""
		self.__stopFlash()
		self.__flash()

	def __flash( self ) :
		self.__shader.value = 0 if self.__shader.value else 1
		self.__flashCBID = BigWorld.callback( 0.5, self.__flash )

	def __stopFlash( self ) :
		"""
		ֹͣ��˸
		"""
		if self.__flashCBID :
			BigWorld.cancelCallback( self.__flashCBID )
			self.__flashCBID = 0
		self.__shader.value = 1.0


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		"""
		����˳���Ϸ
		"""
		self.hide()

	def notifyNewMsg( self ) :
		"""
		֪ͨ�յ����µ���Ϣ
		"""
		self.show()
		self.__startFlash()

	def hide( self ) :
		"""
		ֹͣ��ʾ������ͼ��
		"""
		self.__stopFlash()
		RootGUI.hide( self )

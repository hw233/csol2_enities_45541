# -*- coding: gb18030 -*-
#
# $Id: ChatWindow.py,v 1.60 2008-09-04 01:00:31 huangyongwei Exp $

"""
imlement broadcaster

2009/03/18: rewriten by huangyongwei
"""

import time
import csdefine
import Define
import event.EventCenter as ECenter
from ChatFacade import chatFacade
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.tooluis.CSRichText import CSRichText

class SYSBroadcaster( RootGUI ) :
	__cc_need_time	= 7.0

	def __init__( self ) :
		wnd = GUI.load( "guis/general/chatwindow/sysbroadcaster/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.activable_ = False
		self.escHide_ = False
		self.hitable_ = False
		self.posZSegment = ZSegs.L2
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"
		self.focus = False
		self.moveFocus = False

		self.__fader = wnd.fader
		self.__fader.speed = 0.5
		self.__fader.value = 0
		self.__msgPanel = wnd.msgPanel

		self.__pyRTBMSGs = []						# 刚进入时的时间, 当前进入显示的所有广播
		self.__msgs = []							# 广播消息队列
		self.__maxWidth = self.__msgPanel.width		# 广播横条宽度
		self.__playCBID = 0

		# 绑定系统广播消息处理函数
		chatFacade.bindChannelHandler( csdefine.CHAT_CHANNEL_SYSBROADCAST, self.__onSYSBroadcast )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __createMSGRTB( self, msg ) :
		pyRich = CSRichText()
		pyRich.opGBLink = True
		pyRich.autoNewline = False
		pyRich.text = msg + " " * 10
		pyRich.foreColor = ( 255, 255, 128, 255 )
		self.__msgPanel.addChild( pyRich.getGui() )
		pyRich.left = self.__maxWidth
		pyRich.middle = self.__msgPanel.height / 2 + 1
		return pyRich

	def __cycleMove( self ) :
		"""
		跑马灯播放广播
		"""
		now = time.time()
		for start, pyRTB in self.__pyRTBMSGs[:] :
			passRate = ( now - start ) / self.__cc_need_time		# 历时比
			pyRTB.left = self.__maxWidth * ( 1 - passRate ) 		# 往左移
			if pyRTB.right <= 0 :									# 消息已经移出视区
				self.__pyRTBMSGs.remove( ( start, pyRTB ) )			# 可以被抛弃

		if ( len( self.__pyRTBMSGs ) == 0 or \
			self.__pyRTBMSGs[-1][1].right < self.__maxWidth ) and \
			len( self.__msgs ) :
				pyRich = self.__createMSGRTB( self.__msgs.pop( 0 ) )
				self.__pyRTBMSGs.append( ( now, pyRich ) )
		if len( self.__pyRTBMSGs ) or len( self.__msgs ) :
			self.__playCBID = BigWorld.callback( 0.05, self.__cycleMove )
		else :
			self.__playCBID = 0
			self.fadeout()

	# -------------------------------------------------
	def __onSYSBroadcast( self, channel, spkID, spkName, msg, statusID = None ) :
		self.__msgs.append( msg )
		if not self.__playCBID and rds.statusMgr.isInWorld() :
			self.__cycleMove()
			self.fadein()


	# ----------------------------------------------------------------
	# overwrite methods
	# ----------------------------------------------------------------
	def onEnterWorld( self ) :
		RootGUI.onEnterWorld( self )
		if len( self.__msgs ) and not self.__playCBID :
			self.__cycleMove()
			self.fadein()

	def beforeStatusChanged( self, oldStatus, newStatus ) :
		"""
		系统状态改变时被触发
		"""
		if newStatus != Define.GST_IN_WORLD:
			BigWorld.cancelCallback( self.__playCBID )
			self.__playCBID = 0
			self.__pyRTBMSGs = []
			self.hide()

	def isMouseHit( self ) :
		return False

	def fadein( self ) :
		"""
		渐显
		"""
		self.__fader.value = 1
		self.show()

	def fadeout( self ) :
		"""
		渐隐
		"""
		self.__fader.value = 0
		BigWorld.callback( self.__fader.speed, self.hide )

# -*- coding: gb18030 -*-
#
# $Id: ChatWindow.py,$

"""
imlement broadcaster

"""

import time
import event.EventCenter as ECenter
from ChatFacade import emotionParser
from guis import *
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText

class SpecialCaster( PyGUI ) :
	__cc_need_time	= 10.0

	def __init__( self, msgPanel ) :
		PyGUI.__init__( self, msgPanel )
		self.hitable_ = False
		self.focus = False
		self.moveFocus = False

#		self.__fader = msgPanel.fader
#		self.__fader.speed = 0.5
#		self.__fader.value = 0

		self.__pyRTBMSGs = []						# 刚进入时的时间, 当前进入显示的所有广播
		self.__msgs = []							# 广播消息队列
		self.__maxWidth = self.width		# 广播横条宽度
		self.__playCBID = 0

		self.__triggers = {}
		self.registerEvents()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def registerEvents( self ) :
		self.__triggers["EVT_ON_SPECIALSHOP_BROADCAST"] = self.__onSpecialShopBroadcast #商城广播
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	# -------------------------------------------------
	def __createMSGRTB( self, msg ) :
		pyRich = CSRichText()
		pyRich.opGBLink = True
		pyRich.autoNewline = False
		pyRich.text = msg + " " * 10
		self.addPyChild( pyRich )
		pyRich.left = self.__maxWidth
		pyRich.middle = self.height / 2
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
#			self.fadeout()

	# -------------------------------------------------
	def __onSpecialShopBroadcast( self, msg ) :
		msg = emotionParser.parseRcvMsg( msg )
		self.__msgs.append( msg )
		if not self.__playCBID :
			self.__cycleMove()
#			self.fadein()


	# ----------------------------------------------------------------
	# overwrite methods
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		BigWorld.cancelCallback( self.__playCBID )
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

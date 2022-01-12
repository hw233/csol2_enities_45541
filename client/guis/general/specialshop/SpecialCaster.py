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

		self.__pyRTBMSGs = []						# �ս���ʱ��ʱ��, ��ǰ������ʾ�����й㲥
		self.__msgs = []							# �㲥��Ϣ����
		self.__maxWidth = self.width		# �㲥�������
		self.__playCBID = 0

		self.__triggers = {}
		self.registerEvents()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def registerEvents( self ) :
		self.__triggers["EVT_ON_SPECIALSHOP_BROADCAST"] = self.__onSpecialShopBroadcast #�̳ǹ㲥
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
		����Ʋ��Ź㲥
		"""
		now = time.time()
		for start, pyRTB in self.__pyRTBMSGs[:] :
			passRate = ( now - start ) / self.__cc_need_time		# ��ʱ��
			pyRTB.left = self.__maxWidth * ( 1 - passRate ) 		# ������
			if pyRTB.right <= 0 :									# ��Ϣ�Ѿ��Ƴ�����
				self.__pyRTBMSGs.remove( ( start, pyRTB ) )			# ���Ա�����

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
		����
		"""
		self.__fader.value = 1
		self.show()

	def fadeout( self ) :
		"""
		����
		"""
		self.__fader.value = 0
		BigWorld.callback( self.__fader.speed, self.hide )

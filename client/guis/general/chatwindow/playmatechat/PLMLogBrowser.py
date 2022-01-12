# -*- coding: gb18030 -*-

# ���������¼�鿴����
# written by gjx 2010-06-17

from PLMLogWindow import PLMLogWindow
from AbstractTemplates import Singleton


class PLMLogBrowser( Singleton ) :

	_MAX_SAVE_COUNT = 1000								# ��󱣴�����

	def __init__( self ) :
		self.__msgs = {}								# ������Ϣ��¼


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __queryMsgs( self, objName ) :
		"""
		��ѯ���֮���������Ϣ��¼
		@param		objName	: ������������
		@type		objName	: string
		"""
		return self.__msgs.get( objName, [] )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def recordMsg( self, channel, spkID, spkName, msg, date ) :
		"""
		��¼�����յ�����Ϣ
		"""
		msgs = self.__msgs.get( spkName )
		if msgs is None :
			msgs = [ ( channel.id, spkID, spkName, msg, date ) ]
			self.__msgs[ spkName ] = msgs
		else :
			msgs.append( ( channel.id, spkID, spkName, msg, date ) )
			if len( msgs ) > self._MAX_SAVE_COUNT :		# ������󱣴�����
				msgs.pop( 0 )							# ����������Ϣȥ��ȥ��

	def removeChatLog( self, objName ) :
		"""
		�Ƴ���ĳ��ҵ������¼
		"""
		if objName in self.__msgs :
			del self.__msgs[ objName ]

	def showChatLogs( self, objName, pyOwner = None ) :
		"""
		��ʾ�����¼
		"""
		msgs = self.__queryMsgs( objName )
		PLMLogWindow.inst.showChatLogs( objName, msgs, pyOwner )

	def clearMsgs( self ) :
		"""
		�����Ϣ��¼
		"""
		self.__msgs = {}


plmLogBrowser = PLMLogBrowser()
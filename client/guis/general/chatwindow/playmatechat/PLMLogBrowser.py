# -*- coding: gb18030 -*-

# 好友聊天记录查看窗口
# written by gjx 2010-06-17

from PLMLogWindow import PLMLogWindow
from AbstractTemplates import Singleton


class PLMLogBrowser( Singleton ) :

	_MAX_SAVE_COUNT = 1000								# 最大保存数量

	def __init__( self ) :
		self.__msgs = {}								# 所有消息记录


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __queryMsgs( self, objName ) :
		"""
		查询玩家之间的所有消息记录
		@param		objName	: 聊天对象的名称
		@type		objName	: string
		"""
		return self.__msgs.get( objName, [] )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def recordMsg( self, channel, spkID, spkName, msg, date ) :
		"""
		记录所有收到的消息
		"""
		msgs = self.__msgs.get( spkName )
		if msgs is None :
			msgs = [ ( channel.id, spkID, spkName, msg, date ) ]
			self.__msgs[ spkName ] = msgs
		else :
			msgs.append( ( channel.id, spkID, spkName, msg, date ) )
			if len( msgs ) > self._MAX_SAVE_COUNT :		# 超过最大保存数量
				msgs.pop( 0 )							# 则把最早的消息去掉去掉

	def removeChatLog( self, objName ) :
		"""
		移除和某玩家的聊天记录
		"""
		if objName in self.__msgs :
			del self.__msgs[ objName ]

	def showChatLogs( self, objName, pyOwner = None ) :
		"""
		显示聊天记录
		"""
		msgs = self.__queryMsgs( objName )
		PLMLogWindow.inst.showChatLogs( objName, msgs, pyOwner )

	def clearMsgs( self ) :
		"""
		清空消息记录
		"""
		self.__msgs = {}


plmLogBrowser = PLMLogBrowser()
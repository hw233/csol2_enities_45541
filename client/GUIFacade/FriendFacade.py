# -*- coding: gb18030 -*-
#
# $Id: FriendFacade.py,v 1.40 2008-04-02 09:38:59 zhangyuxing Exp $
"""
好友的　Facade
"""
from bwdebug import *
from event.EventCenter import *
import BigWorld
import time
import csstatus
BLACKGROUPID = 		9 # 黑名单组的ID
FRIENDGROUPID = 	0 # 好友组ID

class FriendFacade:
	@staticmethod
	def reset():
		pass

class FriendItem:
	def __init__( self, name, online, groupID ):
		self.name = name
		self.online = online
		self.groupID = groupID

class FriendSystem:
	def __init__( self ):
		self.__friends = {}
		self.__friendMsgs = {}

	def onUpdateFriend( self, name, online, groupID ):
		"""
		expost
		更新好友信息
		@ivar name		:		玩家名称
		@type name		:		string
		@ivar level		:		玩家等级
		@type level		:		uint8
		@ivar metier	:		玩家BASE
		@type metier	:		mailbox
		@ivar online	:		玩家是否在线
		@type online	:		bool
		"""
		self.__friends[name] = FriendItem( name, online, groupID )
		fireEvent( "EVENT_FRIEND_ADD_LINKMAN", name, online, groupID )

	def addFriend( self, name, groupID ):
		"""
		添加好友
		"""
		if self.__friends.has_key(name):
			BigWorld.player().statusMessage( csstatus.FRIEND_FRIEND_EXIST )
			return

		BigWorld.player().addFriend( name, groupID )


	def initializeFriendsList( self ):
		for friend in self.__friends.itervalues():
			fireEvent( "EVENT_FRIEND_ADD_LINKMAN", friend.name, friend.online, friend.groupID )

	def removeFriend( self, name ):
		"""
		删除好友
		"""
		if not self.__friends.has_key(name):
			BigWorld.player().statusMessage( csstatus.FRIEND_NOT_EXIST )
			return

		self.__friends.pop( name )
		fireEvent( "EVENT_FRIEND_REMOVE", name )
		BigWorld.player().removeFriend( name )

	def changeGroup( self, name, groupID ):
		"""
		改变好友所在的组
		"""
		if not self.__friends.has_key(name):
			BigWorld.player().statusMessage( csstatus.FRIEND_NOT_EXIST )
			return

		if groupID != BLACKGROUPID and groupID != FRIENDGROUPID:
			BigWorld.player().statusMessage( csstatus.FRIEND_GROUP_NOT_EXIST )
			return

		self.__friends[name].groupID = groupID
		online = self.__friends[name].online
		fireEvent( "EVENT_FRIEND_CHANGE_GROUP", name, groupID )
#		fireEvent( "EVENT_FRIEND_ADD_LINKMAN", name, online, groupID )
		BigWorld.player().changeGroup( name, groupID )

	def onShowWhisper( self, name, msg ):
		if not self.__friends.has_key(name):
			BigWorld.player().statusMessage( csstatus.FRIEND_NOT_EXIST )
			return
		fireEvent( "EVENT_FRIEND_SHOW_WHISPER",name, msg )

	def onReceiveMsg( self, name, msg ):#
		"""
		接收到消息
		"""
		if self.__friendMsgs.has_key( name ):
			self.__friendMsgs[name].append( msg )
		else:
			self.__friendMsgs[name] = [msg]


		msgList = self.__friendMsgs[name]
		print "===== msg:",name,msg
#		fireEvent("EVENT_FRIEND_SHOW_MESSAGE_BTN",name,msgList )
		fireEvent( "EVT_ON_FRIENDS_RECEIVE_MSG", name, msgList )

	def hasFriend( self, name ):
		"""
		是否有朋友存在
		"""
		return self.__friends.has_key( name )

g_oFriendInstance = FriendSystem()

def onUpdateFriend( name, online, groupID ):
	"""
	expost
	更新好友信息
	@ivar name		:		玩家名称
	@type name		:		string
	@ivar level		:		玩家等级
	@type level		:		uint8
	@ivar metier	:		玩家BASE
	@type metier	:		mailbox
	@ivar online	:		玩家是否在线
	@type online	:		bool
	"""
	g_oFriendInstance.onUpdateFriend( name, online, groupID )

def addFriend( name, groupID ):
	"""
	添加好友
	"""
	g_oFriendInstance.addFriend( name, groupID )


def initializeFriendsList( ):
	g_oFriendInstance.initializeFriendsList( )

def removeFriend( name ):
	"""
	删除好友
	"""
	g_oFriendInstance.removeFriend( name )

def changeGroup( name, groupID ):
	"""
	改变好友所在的组
	"""
	g_oFriendInstance.changeGroup( name, groupID )

def onReceiveMsg( name, msg ):
	"""
	接收到消息
	"""
	g_oFriendInstance.onReceiveMsg( name, msg )


def onShowWhisper( name, msg ):
	g_oFriendInstance.onShowWhisper( name, msg )

##################################
#好友判断接口
##################################
def IsFriend( name ):
	return g_oFriendInstance.hasFriend( name )

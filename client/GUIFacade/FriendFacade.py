# -*- coding: gb18030 -*-
#
# $Id: FriendFacade.py,v 1.40 2008-04-02 09:38:59 zhangyuxing Exp $
"""
���ѵġ�Facade
"""
from bwdebug import *
from event.EventCenter import *
import BigWorld
import time
import csstatus
BLACKGROUPID = 		9 # ���������ID
FRIENDGROUPID = 	0 # ������ID

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
		���º�����Ϣ
		@ivar name		:		�������
		@type name		:		string
		@ivar level		:		��ҵȼ�
		@type level		:		uint8
		@ivar metier	:		���BASE
		@type metier	:		mailbox
		@ivar online	:		����Ƿ�����
		@type online	:		bool
		"""
		self.__friends[name] = FriendItem( name, online, groupID )
		fireEvent( "EVENT_FRIEND_ADD_LINKMAN", name, online, groupID )

	def addFriend( self, name, groupID ):
		"""
		��Ӻ���
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
		ɾ������
		"""
		if not self.__friends.has_key(name):
			BigWorld.player().statusMessage( csstatus.FRIEND_NOT_EXIST )
			return

		self.__friends.pop( name )
		fireEvent( "EVENT_FRIEND_REMOVE", name )
		BigWorld.player().removeFriend( name )

	def changeGroup( self, name, groupID ):
		"""
		�ı�������ڵ���
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
		���յ���Ϣ
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
		�Ƿ������Ѵ���
		"""
		return self.__friends.has_key( name )

g_oFriendInstance = FriendSystem()

def onUpdateFriend( name, online, groupID ):
	"""
	expost
	���º�����Ϣ
	@ivar name		:		�������
	@type name		:		string
	@ivar level		:		��ҵȼ�
	@type level		:		uint8
	@ivar metier	:		���BASE
	@type metier	:		mailbox
	@ivar online	:		����Ƿ�����
	@type online	:		bool
	"""
	g_oFriendInstance.onUpdateFriend( name, online, groupID )

def addFriend( name, groupID ):
	"""
	��Ӻ���
	"""
	g_oFriendInstance.addFriend( name, groupID )


def initializeFriendsList( ):
	g_oFriendInstance.initializeFriendsList( )

def removeFriend( name ):
	"""
	ɾ������
	"""
	g_oFriendInstance.removeFriend( name )

def changeGroup( name, groupID ):
	"""
	�ı�������ڵ���
	"""
	g_oFriendInstance.changeGroup( name, groupID )

def onReceiveMsg( name, msg ):
	"""
	���յ���Ϣ
	"""
	g_oFriendInstance.onReceiveMsg( name, msg )


def onShowWhisper( name, msg ):
	g_oFriendInstance.onShowWhisper( name, msg )

##################################
#�����жϽӿ�
##################################
def IsFriend( name ):
	return g_oFriendInstance.hasFriend( name )

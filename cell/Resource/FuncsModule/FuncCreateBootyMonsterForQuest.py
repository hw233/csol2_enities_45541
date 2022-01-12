# -*- coding:gb18030 -*-

import csdefine
from Function import Function
from ObjectScripts.GameObjectFactory import g_objFactory
from bwdebug import *
import utils

class FuncCreateBootyMonsterForQuest( Function ):
	"""
	为拥有某个任务的玩家创建一个monster，并且拥有这个monster的战利品所有权
	"""
	def __init__( self, section ):
		Function.__init__( self, section )
		self.questID = section.readInt( "param1" )
		self.className = section.readString( "param2" )
		
		self.position = None
		position = section.readString( "param3" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param3 " % ( self.__class__.__name__, position ) )
		else:
			self.position = pos
		
		self.direction = ( 0, 0, 0 )
		direction = section.readString( "param4" )
		if direction:
			dir = utils.vector3TypeConvert( direction )
			if dir is None:
				ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param4 " % ( self.__class__.__name__, direction ) )
			else:
				self.direction = dir
	
	def valid( self, player, talkEntity = None ):
		quest = player.getQuest( self.questID )
		if quest and quest.query( player ) == csdefine.QUEST_STATE_NOT_FINISH:	# 任务存在且没有完成
			return True
		return False
		
	def do( self, player, talkEntity = None ):
		try:
			teamID = 0
			playerTeam = player.getTeamMailbox()
			if playerTeam:
				teamID = playerTeam.id
			position = talkEntity.position
			direction = talkEntity.direction
			if self.position:
				position = self.position
			direction = self.direction
			g_objFactory.getObject( self.className ).createEntity( talkEntity.spaceID, position, direction, \
				{"firstBruise":1,"bootyOwner":( player.id, teamID ),} )
		except:
			EXCEHOOK_MSG()
			
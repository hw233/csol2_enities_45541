# -*- coding: gb18030 -*-

from Function import Function
from bwdebug import *
import BigWorld
import csconst
import csdefine
import ECBExtend
import Const
import csstatus


class FuncSpringRiddle( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.param1 = section.readInt( "param1" )	# 问题类型
		
	def do( self, playerEntity, talkEntity = None ):
		"""
		执行一个功能

		@param playerEntity: 玩家
		@type  playerEntity: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		playerEntity.endGossip( talkEntity )
		spaceLabel = BigWorld.getSpaceDataFirstForKey( playerEntity.spaceID, csconst.SPACE_SPACEDATA_KEY )
		try:
			flag = Const.SPRING_RIDDLE_AREA_FLAGS[spaceLabel]
		except KeyError:
			flag = 31
		if playerEntity.isActivityCanNotJoin( csdefine.ACTIVITY_SPRING_RIDDER ) :
			playerEntity.client.onStatusMessage( csstatus.SPRING_RIDDLE_FORBID_AMOUNT, "" )
			return
			
		playerEntity.addActivityCount( csdefine.ACTIVITY_SPRING_RIDDER )
		playerEntity.setTemp( "talkID", "START_SPRING_RIDDLE" )
		playerEntity.setTemp( "talkNPCID", talkEntity.id )
		playerEntity.setTemp("question_type", self.param1 )
		playerEntity.addTimer( 0.5, 0, ECBExtend.AUTO_TALK_CBID )
		
	def valid( self, playerEntity, talkEntity = None ):
		"""
		"""
		return True
		
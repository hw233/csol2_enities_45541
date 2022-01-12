# -*- coding: gb18030 -*-

import BigWorld
import csstatus
import csconst
import csdefine
from bwdebug import *
from Function import Function

ENTERN_DESTINY_TRANS_MENBER_DISTANCE = 30.0

class FuncEnterDestinyTrans( Function ):
	"""
	天命轮回副本
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.reqLevel = section.readInt( "param1" )
		
	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		"""
		if player.isState( csdefine.ENTITY_STATE_DEAD ):	# 如果玩家已经死亡，则不能开启
			return False
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		进入天命轮回副本
		"""
		player.endGossip( talkEntity )
		
		if self.reqLevel > player.level:
			#玩家等级不够
			player.statusMessage( csstatus.DESTINY_TRANS_LEVEL_NOT_ENOUGH,  player.getName() )
			return

		if not player.isInTeam():
			#玩家没有组队
			player.statusMessage( csstatus.DESTINY_TRANS_NEED_TEAM )
			return

class FuncEnterDestinyTransCommon( FuncEnterDestinyTrans ):
	"""
	天命轮回副本，普通模式
	"""
	def __init__( self, section ):
		FuncEnterDestinyTrans.__init__( self, section )
		self.type = csconst.DESTINY_TRANS_COPY_COMMON
	
	def do( self, player, talkEntity = None ):
		FuncEnterDestinyTrans.do( self, player, talkEntity )
		BigWorld.globalData[ "SpaceDestinyTransMgr" ].roleRequreEnter( player.base, player.databaseID, player.getTeamMailbox().id, self.reqLevel )


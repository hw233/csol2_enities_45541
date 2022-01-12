# -*- coding: gb18030 -*-

from Function import Function
import csdefine
import BigWorld
import time
import csstatus
import csconst
from ActivityRecordMgr import g_activityRecordMgr
from ObjectScripts.GameObjectFactory import g_objFactory

class FuncYeZhanFengQi( Function ):
	"""
	进入经验乱斗副本
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.spaceName = section.readString( "param1" ) # 进入地图className
		self.level = section.readInt( "param2" )		#进入等级
		self.maxLevel = 110

	def do( self, player, talkEntity = None ):
		"""
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if player.isActivityCanNotJoin( csdefine.ACTIVITY_YE_ZHAN_FENG_QI ):
			player.statusMessage( csstatus.YE_ZHAN_FENG_QI_ACT_FULL )
			return
		
		objScript = g_objFactory.getObject( self.spaceName )
		if player.level < objScript.minLevel:
			player.statusMessage( csstatus.YE_ZHAN_FENG_QI_ENTER_LEVEL, self.level )
			return
			
		if player.level > objScript.maxLevel:
			player.statusMessage( csstatus.YE_ZHAN_FENG_QI_ENTER_MAX_LEVEL, self.level )
			return
		
		pos, direction = objScript.getRandomEnterPos()
		player.gotoSpace( self.spaceName, pos, direction )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True


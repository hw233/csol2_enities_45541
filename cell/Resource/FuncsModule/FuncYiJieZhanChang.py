# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus
import csconst
from ActivityRecordMgr import g_activityRecordMgr
from ObjectScripts.GameObjectFactory import g_objFactory

class FuncYiJieZhanChang( Function ):
	"""
	进入异界战场副本
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.spaceName = section.readString( "param1" ) # 进入地图className

	def do( self, player, talkEntity = None ):
		"""
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if player.findBuffByBuffID( csconst.YI_JIE_ZHAN_CHANG_DESERTER_BUFF_ID ):
			player.statusMessage( csstatus.YI_JIE_ZHAN_CHANG_DESERTER_ABANDON )
			return
		
		objScript = g_objFactory.getObject( self.spaceName )
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


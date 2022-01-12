# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from Buff_Normal import Buff_Normal

class Buff_299036( Buff_Normal ):
	"""
	检测某任务状态，如果完成（未提交），通知副本刷出传送门
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self.questID = 0
		self.spaceName = ""

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self.questID = int(dict["Param1"])
		self.spaceName = dict["Param2"]
		
	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		spaceBase = receiver.getCurrentSpaceBase()
		spaceEntity = BigWorld.entities.get( spaceBase.id )
		if spaceEntity:
			if spaceEntity.className != "xin_fei_lai_shi_001_25_dao":
				return False
			q = receiver.getQuest( self.questID )
			if q:
				state = q.query( receiver )
				if state == csdefine.QUEST_STATE_FINISH:
					spaceEntity.getScript().spawnTransportDoor( spaceEntity )
					return False
		
		return Buff_Normal.doLoop( self, receiver, buffData )
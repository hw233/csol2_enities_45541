# -*- coding: gb18030 -*-

import BigWorld
from Buff_Normal import Buff_Normal
import csdefine

class Buff_299042( Buff_Normal ):
	"""
	友好阵营列表专用buff（只限于怪物对玩家、怪物对怪物、玩家对怪物）
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._friendlyCamps = []

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		friendlyCamps = ( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else "" ).split( ";" )
		self._friendlyCamps = [int( i ) for i in friendlyCamps]

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		if self._friendlyCamps:
			receiver.friendlyCamps = self._friendlyCamps
			for camp in self._friendlyCamps:
				receiver.addCombatRelationIns( csdefine.RELATION_DYNAMIC_COMBAT_CAMP_FRIEND, camp )

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		if self._friendlyCamps:
			receiver.friendlyCamps = self._friendlyCamps
			for camp in self._friendlyCamps:
				receiver.addCombatRelationIns( csdefine.RELATION_DYNAMIC_COMBAT_CAMP_FRIEND, camp )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.friendlyCamps = [ receiver.getCamp() ]
		for camp in self._friendlyCamps:
			receiver.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_COMBAT_CAMP_FRIEND, camp )

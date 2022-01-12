# -*- coding: gb18030 -*-
#
import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import random
import time
import csconst

class Buff_22133( Buff_Normal ):
	"""
	此buff用于检测阵营活动开启情况,buff结束时移除阵营任务. add by cwl
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		
	def receive( self, caster, receiver ):
		"""
		用于给目标施加一个buff，所有的buff的接收都必须通过此接口，
		此接口必须判断接收者是否为realEntity，
		如果否则必须要通过receiver.receiveOnReal()接口处理。

		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		if not receiver.isReal():
			receiver.receiveOnReal( casterID, self )
			return

		buffs = receiver.findBuffsByBuffID( self._buffID )

		#判断是否有相同的buff
		if len( buffs ) > 0:
			# 已存在相同类型的buff
			return
		else:
			receiver.addBuff( self.getNewBuffData( caster, receiver ) )

	def calculateTime( self, caster ):
		"""
		virtual method.
		取得持续时间
		"""
		if not BigWorld.globalData.has_key( "CampActivityEndTime" ):
			return 1
		return BigWorld.globalData["CampActivityEndTime"]

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
		receiver.set( "CampQuestEndTime", self.calculateTime( None ) )		# 记录本次阵营活动结束时间

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
		if BigWorld.globalData.has_key( "CampActivityEndTime" ) and receiver.query( "CampQuestEndTime", 0 ) == BigWorld.globalData["CampActivityEndTime"]:
			return
		# 以上条件不满足说明上次阵营活动已结束，移除此buff
		receiver.removeBuffByBuffID( self._buffID, [0] )

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
		if not BigWorld.globalData.has_key( "CampActivityEndTime" ):
			return False
		if len( receiver.findQuestByType( csdefine.QUEST_TYPE_CAMP_ACTIVITY ) ) <= 0 and len( receiver.findQuestByType( csdefine.QUEST_TYPE_CAMP_DAILY ) ) <= 0:
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		receiver.remove( "CampQuestEndTime" )
		receiver.removeFailedCampQuests()			# 移除所有失败的阵营任务
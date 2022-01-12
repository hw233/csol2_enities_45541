# -*- coding: gb18030 -*-
#
# $Id: Buff_1003.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_99029( Buff_Normal ):
	"""
	用于保镖的帮会成员获得镖车的攻击者
	该buff由镖车加到玩家身上
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
	
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
	
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
		Buff_Normal.receive( self, caster, receiver )
		receiver.setTemp( "protect_dart_id",caster.id )			# 帮会成员记录镖车的id
		receiver.setTemp( "TongDart_level",caster.queryTemp( "level",0 ) )
		receiver.setTemp( "TongDart_factionID",caster.queryTemp("factionID",0) )
	
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
		dartID = receiver.queryTemp( "protect_dart_id",0 )
		
		# 将镖车的合法攻击者（等级与镖车相差小于3）记录到玩家身上
		if dartID != 0:
			entities = receiver.entitiesInRangeExt( 35, "SlaveDart", receiver.position )
			for dartEntity in entities:
				if dartEntity.id == dartID:
					enemyList = []
					for entityID in dartEntity.enemyForTongDart:
						try:
							entity = BigWorld.entities[entityID]
						except KeyError:
							dartEntity.enemyForTongDart.remove( entityID )
							continue
						if entity.getLevel()- receiver.queryTemp( "TongDart_level",0 ) < csconst.DART_ROB_MIN_LEVEL:
							enemyList.append( entityID )
					receiver.setTemp( "attackDartRoleID", enemyList )
					return Buff_Normal.doLoop( self, receiver, buffData )
			
		if receiver.queryTemp( "attackDartRoleID" ):
			receiver.removeTemp( "attackDartRoleID" )
		if receiver.queryTemp( "protect_dart_id" ):
			receiver.removeTemp( "protect_dart_id" )
		if receiver.queryTemp( "TongDart_level" ):
			receiver.removeTemp( "TongDart_level" )
		if receiver.queryTemp( "TongDart_factionID" ):
			receiver.removeTemp( "TongDart_factionID" )
		return False
		
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
		if receiver.queryTemp( "attackDartRoleID" ):
			receiver.removeTemp( "attackDartRoleID" )
		if receiver.queryTemp( "protect_dart_id" ):
			receiver.removeTemp( "protect_dart_id" )
		if receiver.queryTemp( "TongDart_level" ):
			receiver.removeTemp( "TongDart_level" )
		if receiver.queryTemp( "TongDart_factionID" ):
			receiver.removeTemp( "TongDart_factionID" )
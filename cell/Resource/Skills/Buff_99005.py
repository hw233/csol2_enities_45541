# -*- coding: gb18030 -*-

import BigWorld
from SpellBase import *
from Buff_Normal import Buff_Normal
from bwdebug import *
import csdefine
import csconst


class Buff_99005( Buff_Normal ):
	"""
	未决状态buff

	在此状态中时，无法移动、无法使用任何道具/技能、不能攻击，同时也不受到任何攻击、伤害。
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )


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
		receiver.changeState( csdefine.ENTITY_STATE_PENDING )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			actPet = receiver.pcg_getActPet()
			if actPet : 											# 如果玩家有出战宠物
				actPet.entity.changeState( csdefine.ENTITY_STATE_PENDING )

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		receiver.changeState( csdefine.ENTITY_STATE_PENDING )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			actPet = receiver.pcg_getActPet()
			if actPet : 											# 如果玩家有出战宠物
				actPet.entity.changeState( csdefine.ENTITY_STATE_PENDING )

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
		if receiver.state != csdefine.ENTITY_STATE_PENDING:
			return
		if receiver.state != csdefine.ENTITY_STATE_FREE:
			receiver.changeState( csdefine.ENTITY_STATE_FREE )

		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			actPet = receiver.pcg_getActPet()
			if actPet : 										# 如果玩家有出战宠物
				actPet.entity.changeState( csdefine.ENTITY_STATE_FREE )

		es = receiver.entitiesInRangeExt( 15.0, None, receiver.position )
		for e in es:
			if not hasattr( e, "triggerTrap" ):
				continue

			if e.initiativeRange > 0:
				range = receiver.position.flatDistTo( e.position )
				if e.initiativeRange >= range:
					e.triggerTrap( receiver.id, range )
# -*- coding: gb18030 -*-

import random
import BigWorld

import csstatus
import csdefine
from bwdebug import *

import Const
from SpellBase import *
from Buff_Normal import Buff_Normal
STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP
BE_HOMING_MAX_SPEED = 50.0

class Buff_108007( Buff_Normal ):
	"""
	example:混乱
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
		
		#如果是最先连击你的那个人，那么可以移动否则不移动
		receiver.setTemp( "HOMING_TARGET", buffData["caster"] )

		if receiver.attrIntonateTimer > 0 and receiver.attrIntonateSkill.getType() in Const.INTERRUPTED_BASE_TYPE or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )
		# 执行附加效果
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.effectStateInc( csdefine.EFFECT_STATE_BE_HOMING )
		else:
			receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		receiver.actCounterInc( STATES )
		if receiver.isMoving():
			# 加入移动限制，以确保buff对移动限制效果生效 by姜毅
			receiver.stopMoving()
		
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.setTopSpeed( BE_HOMING_MAX_SPEED )	


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
		#如果是最先连击你的那个人，那么可以移动否则不移动
		receiver.setTemp( "HOMING_TARGET", buffData["caster"] )
		# 执行附加效果
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.effectStateInc( csdefine.EFFECT_STATE_BE_HOMING )
		else:
			receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		receiver.actCounterInc( STATES )
		if receiver.isMoving():
			# 加入移动限制，以确保buff对移动限制效果生效 by姜毅
			receiver.stopMoving()
		
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.setTopSpeed( BE_HOMING_MAX_SPEED )
			
		
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
		#如果是最先连击你的那个人，那么可以移动否则不移动
		receiver.removeTemp( "HOMING_TARGET" )
		if receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.effectStateDec( csdefine.EFFECT_STATE_BE_HOMING )
		else:
			receiver.effectStateDec( csdefine.EFFECT_STATE_VERTIGO )
		receiver.actCounterDec( STATES )
		if not receiver.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			receiver.think( 0.1 )
		

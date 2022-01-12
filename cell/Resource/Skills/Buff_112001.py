# -*- coding: gb18030 -*-
#
# $Id: Buff_22005.py,v 1.2 2008-08-05 08:44:27 kebiao Exp $

"""
持续性效果
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import random
import csconst

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP
			 
class Buff_112001( Buff_Normal ):
	"""
	example:封印于寒冰之中。不能移动和攻击，也不会受到任何伤害。
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
		
	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: 施法者
		@type    caster: Entity
		@param receiver: 受击者
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		isRayRingEffect = buff.isRayRingEffect()

		if not isRayRingEffect and buff.isMalignant(): #是恶性但不是光环效果 那么免疫
			return csstatus.SKILL_BUFF_IS_RESIST
		elif isRayRingEffect:   # 是光环效果
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# 策划规定， 如果是自己释放的恶性光环效果， 则无敌可以免疫
				if buffData[ "caster" ] != caster.id:
					buffData[ "state" ] |= csdefine.BUFF_STATE_DISABLED
				else:
					return csstatus.SKILL_BUFF_IS_RESIST
		
		return csstatus.SKILL_GO_ON
		
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
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #首先添加抵抗
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		
		if receiver.isMoving():		# 加入移动限制，以确保buff对移动限制效果生效 by姜毅
			receiver.stopMoving()

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
		return Buff_Normal.doLoop( self, receiver, buffData )
		
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
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		
		if receiver.isMoving():		# 加入移动限制，以确保buff对移动限制效果生效 by姜毅
			receiver.stopMoving()
		
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
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.actCounterDec( STATES )
		
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/08/05 06:36:02  kebiao
# no message
#
#
#
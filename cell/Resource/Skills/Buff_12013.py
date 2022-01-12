# -*- coding: gb18030 -*-
#
# $Id: Buff_108001.py,v 1.12 2008-07-04 03:50:57 kebiao Exp $

"""
持续性效果
"""

import BigWorld

import csstatus
import csdefine
from bwdebug import *

import Const
from SpellBase import *
from Buff_Normal import Buff_Normal

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_USE_ITEM

class Buff_12013( Buff_Normal ):
	"""
	example:"冻结自身，10秒内不受任何伤害，但也不能移动不能使用技能，可主动取消。
	冻结状态下，每2秒恢复一次生命和法力，总计恢复生命和法力上限的30%(31级)/45%(60级)生命及法力。取消冻结状态停止恢复。"

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
		self._p1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) / 100.0
		
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
		if receiver.attrIntonateTimer > 0 or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )

		dels = []
		
		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			buff = receiver.getBuff( idx )
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# 策划规定， 如果是自己释放的恶性光环效果， 则无敌可以免疫
				if buffData[ "caster" ] == caster.id:
					dels.append( idx )
				else:				
					receiver.addBuffState( idx, csdefine.BUFF_STATE_DISABLED )
					
		for i in dels:
			receiver.removeBuff( i, [ 0 ] )
			
		# 执行附加效果
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )
		
		if receiver.isMoving():
			receiver.stopMoving()

		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		
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
		receiver.setHP( receiver.HP + int( receiver.HP_Max * self._p1 ) )
		receiver.setMP( receiver.MP + int( receiver.MP_Max * self._p1 ) )
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
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #首先添加抵抗
		# 执行附加效果
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )
		
		if receiver.isMoving():
			receiver.stopMoving()
		
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		
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
		receiver.effectStateDec( csdefine.EFFECT_STATE_FIX )
		receiver.actCounterDec( STATES )
		
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		
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
		
#
# 
#
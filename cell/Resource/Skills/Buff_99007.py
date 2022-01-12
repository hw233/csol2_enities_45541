# -*- coding: gb18030 -*-

"""
持续性效果
"""

from Buff_Normal import Buff_Normal
import csstatus
import csdefine

class Buff_99007( Buff_Normal ):
	"""
	共骑专用buff
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
		m = buff.isMalignant()
		if not buff.isRayRingEffect() and m: #是恶性但不是光环效果 那么免疫
			return csstatus.SKILL_BUFF_IS_RESIST
		elif buff.isRayRingEffect() and m:   #是恶性且是光环效果 那么 使其失效
			buffData[ "state" ] |= csdefine.BUFF_STATE_DISABLED

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
		#receiver.clearBuff( csdefine.BUFF_INTERRUPT_INVINCIBLE_EFFECT ) #删除自身现在所有可以删除的BUFF
		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			receiver.addBuffState( idx, csdefine.BUFF_STATE_DISABLED )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
	
	def doReload( self, receiver, buffData ):
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #首先添加抵抗
		#receiver.clearBuff( csdefine.BUFF_INTERRUPT_INVINCIBLE_EFFECT ) #删除自身现在所有可以删除的BUFF
		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			receiver.addBuffState( idx, csdefine.BUFF_STATE_DISABLED )
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
		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			receiver.removeBuffState( idx, csdefine.BUFF_STATE_DISABLED )
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.retractVehicle( receiver.id )

# $Log: not supported by cvs2svn $
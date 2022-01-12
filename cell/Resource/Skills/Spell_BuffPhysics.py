# -*- coding: gb18030 -*-
#
# $Id: Spell_BuffPhysics.py,v 1.3 2008-07-04 03:50:57 kebiao Exp $

"""
"""

import csdefine
from SpellBase import *
import csstatus
from Spell_Item import Spell_Item
from Spell_PhysSkill import Spell_PhysSkill2
from Spell_PhysSkill import Spell_PhyVolley2
import random

class Spell_BuffPhysics( Spell_PhysSkill2 ):
	"""
	释放物理伤害型BUFF， 这个技能本身并不产生伤害， 但是他走物理技能 击中 命中路线
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill2.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill2.init( self, dict )

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		校验技能是否可以使用。
		return: SkillDefine::SKILL_*;默认返回SKILL_UNKNOW
		注：此接口是旧版中的validUse()

		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return:           INT，see also csdefine.SKILL_*
		@rtype:            INT
		"""
		#处理沉默等一类技能的施法判断
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
			return csstatus.SKILL_CANT_CAST
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		return Spell_PhysSkill2.useableCheck( self, caster, target )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		if receiver is None:
			return
			
		damageType = self._damageType
		# 计算命中率
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			# 被躲开了并不代表我没打你，因此仇恨是有可能存在的，需要通知受到0点伤害
			receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
			receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
			caster.doAttackerOnDodge( receiver, damageType )
			receiver.doVictimOnDodge( caster, damageType )
			return

		self.receiveLinkBuff( caster, receiver )
		# 执行命中后的行为
		caster.doAttackerOnHit( receiver, damageType )	#攻击者触发
		receiver.doVictimOnHit( caster, damageType )   #受击者触发
		

class Spell_BuffPhyVolley2( Spell_PhyVolley2 ):
	"""
	释放物理伤害型BUFF， 这个技能本身并不产生伤害， 但是他走物理技能 击中 命中路线
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhyVolley2.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhyVolley2.init( self, dict )
		
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		damageType = self._damageType
		# 计算命中率
		hit = self.calcHitProbability( caster, receiver )
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0 or not random.random() < hit:
			# 被躲开了并不代表我没打你，因此仇恨是有可能存在的，需要通知受到0点伤害
			receiver.receiveSpell( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0, 0 )
			receiver.receiveDamage( caster.id, self.getID(), damageType | csdefine.DAMAGE_TYPE_DODGE, 0 )
			caster.doAttackerOnDodge( receiver, damageType )
			receiver.doVictimOnDodge( caster, damageType )
			return

		self.receiveLinkBuff( caster, receiver )
		# 执行命中后的行为
		caster.doAttackerOnHit( receiver, damageType )	#攻击者触发
		receiver.doVictimOnHit( caster, damageType )    #受击者触发
		
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/07/03 02:49:39  kebiao
# 改变 睡眠 定身等效果的实现
#
# Revision 1.1  2008/05/27 02:10:37  kebiao
# no message
#
#
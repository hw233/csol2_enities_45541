# -*- coding: gb18030 -*-
#
# $Id: Spell_DamageInfection.py,v 1.3 2007-12-20 01:18:32 kebiao Exp $

"""
伤害感染型技能基础
"""

from SpellBase import *
import random
import csdefine
from Spell_PhysSkill import *
from Spell_Magic import *
import SkillTargetObjImpl

def getNearEntity( caster, receivers ):
	"""
	获取与caster最近的一个受术者
	"""
	x = 0.0
	e = 0
	for i, receiver in enumerate( receivers ):
		xx = caster.position.flatDistTo( receiver.position )
		if xx < x:
			x = xx
			e = i
	return e
	
class Spell_DamageInfectionPhy( Spell_PhysSkill ):
	"""
	伤害感染型技能基础 物理 单体
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )
		self._rmax = int( dict["param1"] if len( dict["param1"] ) > 0 else 0 )  	#感染个数
		
	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		entity = target.getObject()
		if entity is None:
			return []
		return [ entity ]
		
	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		对受术者呈现最终伤害
		通常用于这些情况需要重载 需要根据对某entity所产生的伤害 进行其他方面的影响
		"""
		rmax = self._rmax
		rlist = [ receiver ] #这个受术者(通常一定是第一个施展目标)是已经确定的将受到伤害给出的
		# 根据receiver 获得他周围的范围内所有ENTITY 然后找出最近的
		receivers = self._receiverObject.getReceivers( caster, SkillTargetObjImpl.createTargetObjEntity( receiver ) )
		
		while( 1 ):
			if len( receivers ) <= 0 or rmax <= 0: break
			entity = receivers.pop( getNearEntity( caster, receivers ) )
			if entity.id != receiver.id:
				rlist.append( entity )
				rmax -= 1

		for receiver in rlist:
			if not receiver.isDestroyed and not receiver.state == csdefine.ENTITY_STATE_DEAD:
				Spell_PhysSkill.persentDamage( self, caster, receiver, damageType, damage )

class Spell_DamageInfectionMagic( Spell_Magic ):
	"""
	伤害感染型技能基础 物理 单体
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Magic.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		self._rmax = int( dict["param1"] if len( dict["param1"] ) > 0 else 0 )  	#感染个数
		
	def getReceivers( self, caster, target ):
		"""
		virtual method
		取得所有的符合条件的受术者Entity列表；
		所有的onArrive()方法都应该调用此方法来获取有效的entity。
		@return: array of Entity

		@param   caster: 施法者
		@type    caster: Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@rtype: list of Entity
		"""
		return [target.getObject()]
		
	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		对受术者呈现最终伤害
		通常用于这些情况需要重载 需要根据对某entity所产生的伤害 进行其他方面的影响
		"""
		rmax = self._rmax
		rlist = [ receiver ] #这个受术者(通常一定是第一个施展目标)是已经确定的将受到伤害给出的
		# 根据receiver 获得他周围的范围内所有ENTITY 然后找出最近的
		receivers = self._receiverObject.getReceivers( caster, SkillTargetObjImpl.createTargetObjEntity( receiver ) )
		
		while( 1 ):
			if len( receivers ) <= 0 or rmax <= 0: break
			entity = receivers.pop( getNearEntity( caster, receivers ) )
			if entity.id != receiver.id:
				rlist.append( entity )
				rmax -= 1

		for receiver in rlist:
			if not receiver.isDestroyed and not receiver.state == csdefine.ENTITY_STATE_DEAD:			
				Spell_Magic.persentDamage( self, caster, receiver, damageType, damage )
			
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/12/17 01:36:36  kebiao
# 调整PARAM0为param1
#
# Revision 1.1  2007/11/26 08:22:42  kebiao
# no message
#
# -*- coding:gb18030 -*-

"""
Spell技能类
"""
from Spell_Item import Spell_Item
import BigWorld
import csdefine

class Spell_111006( Spell_Item ):
	"""
    对目标单位造成相当于其生命值上限xx%的伤害
	"""
	def __init__( self ):
		"""
		构造函数
		"""
		Spell_Item.__init__( self )
		self.damage = 0

	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.param1 = int( dict["param1"] if len( dict["param1"] ) > 0 else 0 )  / 100.0

	def cast( self, caster, targetObject ):
		"""
		virtual method.
		播放技能吟唱动作和效果。
		@param caster:			施放者Entity
		@type caster:			Entity
		@param targetObject: 施展对象
		@type  targetObject: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		"""
		Spell_Item.cast( self, caster, targetObject )
		target = targetObject.getObject()
		self.damage = int( target.HP_Max * self.param1 )
		target.onReceiveDamage( caster.id, self, csdefine.DAMAGE_TYPE_PHYSICS_NORMAL, self.damage )

# -*- coding: gb18030 -*-
#
# $Id: Spell_MultAttack.py,v 1.5 2007-12-26 08:19:50 kebiao Exp $

"""
多次攻击伤害型技能基础
"""

from SpellBase import *
import random
import csdefine
from Spell_PhysSkill import *
from Spell_Magic import *
		
class Spell_MultAttackPhy( Spell_PhysSkill ):
	"""
	多次攻击伤害型技能 物理1 单体
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
		self._attackCount = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		if self._attackCount <= 0: self._attackCount = 1

	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		对受术者呈现最终伤害
		通常用于这些情况需要重载 需要根据对某entity所产生的伤害 进行其他方面的影响
		"""
		for count in xrange( self._attackCount ): #策划要求对每个ENTITY走一次伤害流程 造成多次掉血 而多次攻击动作由客户端完成
			Spell_PhysSkill.persentDamage( self, caster, receiver, damageType, damage / self._attackCount )
			
class Spell_MultAttackVolleyPhy( Spell_PhyVolley ):
	"""
	多次攻击伤害型技能 物理1 群体
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhyVolley.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhyVolley.init( self, dict )
		self._attackCount = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		if self._attackCount <= 0: self._attackCount = 1
		
	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		对受术者呈现最终伤害
		通常用于这些情况需要重载 需要根据对某entity所产生的伤害 进行其他方面的影响
		"""
		for count in xrange( self._attackCount ): #策划要求对每个ENTITY走一次伤害流程 造成多次掉血 而多次攻击动作由客户端完成
			Spell_PhyVolley.persentDamage( self, caster, receiver, damageType, damage / self._attackCount )
			
class Spell_MultAttackMagic( Spell_Magic ):
	"""
	多次攻击伤害型技能 法术 单体
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
		self._attackCount = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		if self._attackCount <= 0: self._attackCount = 1

	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		对受术者呈现最终伤害
		通常用于这些情况需要重载 需要根据对某entity所产生的伤害 进行其他方面的影响
		"""
		for count in xrange( self._attackCount ): #策划要求对每个ENTITY走一次伤害流程 造成多次掉血 而多次攻击动作由客户端完成
			Spell_Magic.persentDamage( self, caster, receiver, damageType, damage / self._attackCount )
			
class Spell_MultAttackVolleyMagic( Spell_MagicVolley ):
	"""
	多次攻击伤害型技能 法术 群体
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_MagicVolley.__init__( self )
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_MagicVolley.init( self, dict )
		self._attackCount = int( dict[ "param1" ] if len( dict[ "param1" ] ) > 0 else 0 ) 	
		if self._attackCount <= 0: self._attackCount = 1

	def persentDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		对受术者呈现最终伤害
		通常用于这些情况需要重载 需要根据对某entity所产生的伤害 进行其他方面的影响
		"""
		for count in xrange( self._attackCount ): #策划要求对每个ENTITY走一次伤害流程 造成多次掉血 而多次攻击动作由客户端完成
			Spell_MagicVolley.persentDamage( self, caster, receiver, damageType, damage / self._attackCount )

# $Log: not supported by cvs2svn $
# Revision 1.4  2007/12/17 01:36:36  kebiao
# 调整PARAM0为param1
#
# Revision 1.3  2007/12/03 08:26:22  kebiao
# 去掉了基础类
#
# Revision 1.2  2007/11/26 08:44:18  kebiao
# 修改BUG
#
# Revision 1.1  2007/11/26 08:25:31  kebiao
# 一次攻击流程产生多次伤害
#
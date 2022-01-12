# -*- coding: gb18030 -*-
#
# $Id: Spell_PhysSkill.py,v 1.18 2008-09-04 07:46:27 kebiao Exp $

"""
持续性效果
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
import SkillTargetObjImpl
from Spell_PhysSkill import Spell_PhysSkill2
from Spell_Magic import Spell_Magic

class Spell_DirectPhyDamage( Spell_PhysSkill2 ):
	"""
	元素伤害技能
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

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		计算被攻击方物理防御减伤
		角色基础物理防御值（总公式中的基础值）=0
		物理防御减伤（总公式中的基础值）= 防御值/(0.1*防御值+150*攻击方等级+1000) 
		在攻防的计算中，防御值会先换算成防御减伤，然后再和攻击力进行换算。
		@param source:	攻击方
		@type  source:	entity
		@param target:	被攻击方
		@type  target:	entity
		@return: FLOAT
		"""
		return 0


class Spell_DirectMagicDamage( Spell_Magic ):
	"""
	元素伤害技能
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

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		计算被攻击方物理防御减伤
		角色基础物理防御值（总公式中的基础值）=0
		物理防御减伤（总公式中的基础值）= 防御值/(0.1*防御值+150*攻击方等级+1000) 
		在攻防的计算中，防御值会先换算成防御减伤，然后再和攻击力进行换算。
		@param source:	攻击方
		@type  source:	entity
		@param target:	被攻击方
		@type  target:	entity
		@return: FLOAT
		"""
		return 0
		
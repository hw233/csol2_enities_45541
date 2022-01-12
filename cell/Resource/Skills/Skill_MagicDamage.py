# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *

from SpellBase import *
from Skill_Damage import Skill_Damage

import csconst
import csdefine
import csstatus
import random


class Skill_MagicDamage( Skill_Damage ):
	"""
	被动技能伤害类:物理伤害

	目前还不完善,仅加入了目前为止确定的一些行为以适应装备附加属性技能的需求,
	以后需要对被动技能结构进行总体规划.11:14 2008-10-24,wsf
	"""
	def __init__( self ):
		"""
		"""
		Skill_Damage.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_Damage.init( self, dict )


	def calcDoubleMultiple( self, caster ):
		"""
		virtual method.
		计算暴击伤害加倍
		@param caster: 被攻击方
		@type  caster: entity
		@return type:计算后得到的暴击倍数
		"""
		return caster.magic_double_hit_multiple


	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		判断攻击者是否爆击
		return type:bool
		"""
		return random.random() < ( caster.magic_double_hit_probability + ( receiver.be_magic_double_hit_probability - receiver.be_magic_double_hit_probability_reduce ) / csconst.FLOAT_ZIP_PERCENT )






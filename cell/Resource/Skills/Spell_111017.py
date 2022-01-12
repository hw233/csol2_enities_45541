# -*- coding: gb18030 -*-
#
# $Id: Spell_311413.py,v 1.7 2008-07-15 04:06:26 kebiao Exp $

"""
技能对物品施展法术基础。
"""

from SpellBase import *
from Spell_PhysSkill import Spell_PhysSkill
import utils
import csstatus
import csdefine
import random
import csconst

class Spell_111017( Spell_PhysSkill ):
	"""
	增加NPC技能111017 狂暴冲击
	根据技能等级（共10级）使用1～10倍自身攻击力，对敌单目标造成物理伤害。 
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_PhysSkill.__init__( self )

	def init( self, dict ):
		"""
		读取配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )

	def calcSkillHitStrength( self, source, receiver,dynPercent, dynValue ):
		"""
		virtual method.
		计算技能攻击力
		方式1：技能攻击力（总公式中的基础值）=技能本身的攻击力+角色的物理攻击力
		带入总公式中就是：（技能本身的攻击力+角色物理攻击力）*（1+物理攻击力加成）+物理攻击力加值
		@param source:	攻击方
		@type  source:	entity
		@param dynPercent:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加成
		@param  dynValue:	在本次攻击流程中可能会有外部其他技能导致额外的 技能攻击力加值
		"""
		#角色物理攻击力
		extra = int((source.damage_min + source.damage_max) / 2) * self.getLevel()
		base = random.randint( self._effect_min, self._effect_max )
		return self.calcProperty( base, extra, dynPercent + source.skill_extra_percent / csconst.FLOAT_ZIP_PERCENT, dynValue + source.skill_extra_value )


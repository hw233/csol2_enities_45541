# -*- coding: gb18030 -*-
#
# $Id: Spell_111005.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $


from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from Spell_PhysSkill import Spell_PhyVolley


class Spell_111005( Spell_PhyVolley ):
	"""
	绞杀技能，对目标单位造成相当于其生命值上限50%的物理伤害
	"""
	def __init__( self ):
		"""
		"""
		Spell_PhyVolley.__init__( self )
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_PhyVolley.init( self, dict )
		self._param = int( dict["param1"] if len( dict["param1"] ) > 0 else 0 )  / 100.0	
		
	def calcDamage( self, caster, receiver, skillDamage ):
		"""
		virtual method.
		计算直接伤害
		普通物理伤害（总公式中的基础值）=物理攻击力*（1-被攻击方物理防御减伤）
		技能物理伤害（总公式中的基础值）=技能攻击力*（1-被攻击方物理防御减伤）
		
		@param source: 攻击方
		@type  source: entity
		@param target: 被攻击方
		@type  target: entity
		@param skillDamage: 技能攻击力
		@return: INT32
		"""
		return receiver.HP_Max * self._param
		
#$Log: not supported by cvs2svn $
#
#
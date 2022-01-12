# -*- coding: gb18030 -*-
#
# $Id: Spell_112001.py,v 1.1 2008-08-30 10:01:12 wangshufeng Exp $


from bwdebug import *

import BigWorld

import csdefine
import csconst
import csstatus

from Spell_Magic import Spell_Magic


class Spell_112001( Spell_Magic ):
	"""
	毁灭
	
	失去当前生命值的50%，直接作用效果目标失去生命值，不经过任何防御和豁免，视为直接的变化系属性伤害
	"""
	def __init__( self ):
		"""
		"""
		Spell_Magic.__init__( self )
		
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
		
		
	def receive( self, caster, receiver ):
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
		receiver.HP = int( receiver.HP * 0.5 )	# HP当前定义为int
		
#$Log: not supported by cvs2svn $
#
#
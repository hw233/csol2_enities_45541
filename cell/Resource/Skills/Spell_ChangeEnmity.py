# -*- coding: gb18030 -*-
#
# $Id: Spell_ChangeEnmity.py,v 1.1 2007-11-24 08:22:58 kebiao Exp $

"""
将施法者从目标的治疗列表、伤害列表、战斗列表这三个列表中删除
"""

from SpellBase import *
import random
import csdefine
import csstatus
from Spell_Magic import Spell_Magic
from Domain_Fight import g_fightMgr

class Spell_ChangeEnmity( Spell_Magic ):
	"""
	将施法者从目标的治疗列表、伤害列表、战斗列表这三个列表中删除
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

	def useableCheck( self, caster, target ):
		
		if target.getObject().level > self.getCastTargetLevelMax():
			return csstatus.SKILL_CAST_ENTITY_LEVE_MAX
		return Spell_Magic.useableCheck( self, caster, target )
	
	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		g_fightMgr.breakEnemyRelation( receiver, caster )
		
# $Log: not supported by cvs2svn $

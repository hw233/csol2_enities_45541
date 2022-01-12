# -*- coding: gb18030 -*-
#
# $Id: Spell_311101.py,v 1.3 2008-03-10 01:01:25 kebiao Exp $

"""
Spell技能类。
"""
import BigWorld
from bwdebug import *
from SpellBase import *
import csstatus
import csdefine

class Spell_322415( Spell ):
	def __init__( self ):
		"""
		从python dict构造SkillBase
		"""
		Spell.__init__( self )
		self._isCanFight = 0  #是否可战斗状态下使用

	def init( self, dict ):
		"""
		读取技能配置
		@param dict:			技能配置
		@type dict:				python dict
		"""
		Spell.init( self, dict )
		if dict["param1"] != "":
			self._isCanFight = int( dict["param1"] )

	def useableCheck( self, caster, receiver ):
		"""
		virtual method.
		校验技能是否可以使用
		"""
		if self._isCanFight:
			if caster.state != csdefine.ENTITY_STATE_FREE:
				return csstatus.SKILL_NEED_STATE_FREE
		return Spell.useableCheck( self, caster, receiver )

	def spell( self, caster, target ):
		"""
		向服务器发送Spell请求。

		@param caster:		施放者Entity
		@type  caster:		Entity
		@param target: 施展对象
		@type  target: 一个包装过的对象entity 被包装对象可能是 (位置，entity, item)详细请看SkillTargetObjImpl.py
		@return: INT, see also csdefine.SKILL_*
		"""
		buffs = caster.attrBuffs
		for buff in buffs:
			skill = buff["skill"]
			if skill.getBuffID() == "020002":
				index = buff["index"]
				caster.requestRemoveBuff( index )
				return

		Spell.spell( self, caster, target )
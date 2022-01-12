# -*- coding: gb18030 -*-

import random
from SpellBase import *
from Skill_DoubleHitSpell import Skill_DoubleHitSpell
from Function import newUID

class Skill_DoubleHitSpellMana( Skill_DoubleHitSpell ):
	"""
	玩家暴击命中后有几率对自身/目标释放一个不需要消耗魔法的标志
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Skill_DoubleHitSpell.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Skill_DoubleHitSpell.init( self, dict )

	def springOnDoubleHit( self, caster, receiver, damageType ):
		"""
		产生暴击后效果
		"""
		if self.isOwnerSpell:
			if caster.queryTemp( "FORBID_NOT_NEED_MANA", False ):
				return
		else:
			if receiver.queryTemp( "FORBID_NOT_NEED_MANA", False ):
				return

		Skill_DoubleHitSpell.springOnDoubleHit( self, caster, receiver, damageType )

	def addToDict( self ):
		"""
		生成用于传输的数据
		"""
		return { "param":{"triggerSkillID":self.triggerSkillID, "effectPercent":self.effectPercent, "isOwnerSpell":self.isOwnerSpell} }

	def createFromDict( self, data ):
		"""
		创建技能实例
		"""
		obj = Skill_DoubleHitSpellMana()
		obj.__dict__.update( self.__dict__ )
		paramData = data["param"]
		obj.triggerSkillID = paramData["triggerSkillID"]
		obj.effectPercent = paramData["effectPercent"]
		obj.isOwnerSpell = paramData["isOwnerSpell"]
		try:
			uid = data["uid"]
		except KeyError:
			uid = 0
		if uid == 0:
			uid = newUID()
		obj.setUID( uid )
		return obj

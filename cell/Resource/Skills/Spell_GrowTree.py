# -*- coding: gb18030 -*-

import csstatus
import csconst
import csdefine
import random
from Spell_Item import Spell_Item
from bwdebug import *
import BigWorld

class Spell_GrowTree( Spell_Item ):
	"""
	魅力化肥
	"""
	def __init__( self ):
		"""
		"""
		Spell_Item.__init__( self )
		self.p1 = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.p1 = int( dict[ "param1" ] )		# 生效的目标entity类型

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""
		receiver.onRipe()

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		targetEntity = target.getObject()
		if targetEntity is None: return csstatus.SKILL_CANT_CAST_ENTITY
		if targetEntity.isDestroyed: return csstatus.SKILL_CANT_CAST_ENTITY
		# 施肥目标不正确
		if not targetEntity.isEntityType( self.p1 ): return csstatus.SKILL_USE_ITEM_WRONG_TARGET
		# 目标果树已成熟
		if targetEntity.isRipe: return csstatus.FRUIT_ISRIPE
		# 目标果树不是自己栽种
		if targetEntity.planterDBID != caster.databaseID: return csstatus.FRUIT_NOT_YOU

		return Spell_Item.useableCheck( self, caster, target)


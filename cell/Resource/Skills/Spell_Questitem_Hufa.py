# -*- coding: gb18030 -*-


import BigWorld
import csdefine
import csstatus
from Spell_Item import Spell_Item

class Spell_Questitem_Hufa( Spell_Item ):
	"""
	护法任务物品使用技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )
		self.buffID = int( dict[ "param1" ] )


	def useableCheck( self, caster, target ):
		"""
		virtual method. 
		"""
		if len(target.getObject().findBuffsByBuffID( self.buffID )) == 0:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET

		return Spell_Item.useableCheck( self, caster, target)


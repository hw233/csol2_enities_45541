# -*- coding: gb18030 -*-

from Spell_BuffNormal import Spell_ItemBuffNormal
import csstatus

class Spell_Item_To_SpecifiedTarget( Spell_ItemBuffNormal ):
	"""
	对特定目标使用物品技能
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_ItemBuffNormal.__init__( self )
		self.classNames = []

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_ItemBuffNormal.init( self, dict )
		self.classNames = dict[ "param1" ].split( "|" ) if len( dict[ "param1" ] ) > 0 else [] 		# 技能作用的目标ID

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		"""
		entity = target.getObject()
		if entity.className not in self.classNames:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET
		
		return Spell_ItemBuffNormal.useableCheck( self, caster, target )
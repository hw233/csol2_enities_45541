# -*- coding: gb18030 -*-
#

"""
摧毁场景物件
"""

from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import items


class Spell_QuestItem_NPCObject( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )
		self.__className = int( dict["Param1"] )


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""

		receiver.onIncreaseQuestTaskState( caster.id )
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method. 
		"""
		if self._className != target.getObject().className:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET

		if caster.checkItemsPlaceIntoNK_( [items.instance().createDynamicItem( self.__itemID, self.__amount )] ):
			return csstatus.SKILL_USE_ITEM_NEED_ONE_BLANK

		return Spell_Item.useableCheck( self, caster, target)


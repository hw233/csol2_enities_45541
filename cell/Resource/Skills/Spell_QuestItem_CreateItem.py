# -*- coding: gb18030 -*-
#

"""
对着一个目标使用一个物品，得到另一个物品
"""

from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import items
import csdefine


class Spell_QuestItem_CreateItem( Spell_Item ):
	"""
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
		self.__itemID 	= int( dict["param1"] )
		self.__amount	= int( dict["param2"] )
		self.__className = str( dict["param3"] )
		self.__isDestroy = int( dict["param4"] )
		Spell_Item.init( self, dict )

	def receive( self, caster, receiver ):
		"""
		virtual method.
		法术到达所要做的事情
		"""

		item = items.instance().createDynamicItem( self.__itemID, self.__amount )
		caster.addItemAndNotify_( item, csdefine.ADD_ITEM_USE )
		if self.__isDestroy:
			receiver.onReceiveSpell( caster, None )
		Spell_Item.receive( self, caster, receiver )

	def useableCheck( self, caster, target ):
		"""
		virtual method. 
		"""
		if self.__className != target.getObject().className:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET
		
		bagState = caster.checkItemsPlaceIntoNK_( [items.instance().createDynamicItem( self.__itemID, self.__amount )] )
		if bagState: #modify by wuxo 2012-2-9
			if bagState == csdefine.KITBAG_NO_MORE_SPACE:
				caster.client.onStatusMessage( csstatus.KITBAG_IS_FULL, "" )
			elif bagState == csdefine.KITBAG_ITEM_COUNT_LIMIT:
				return csstatus.KITBAG_ITEM_COUNT_LIMIT
			return csstatus.SKILL_USE_ITEM_NEED_ONE_BLANK

		return Spell_Item.useableCheck( self, caster, target)


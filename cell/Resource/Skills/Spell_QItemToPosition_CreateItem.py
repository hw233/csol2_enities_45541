# -*- coding: gb18030 -*-
#

"""
"""

from bwdebug import *
from Spell_Item import Spell_Item
import csstatus
import items
import BigWorld
import csconst
import csdefine
import utils


class Spell_QItemToPosition_CreateItem( Spell_Item ):
	"""
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Spell_Item.__init__( self )
		self.__targetPosition = None


	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		self.__itemID 	= int( dict["param1"] )
		self.__amount	= int( dict["param2"] )
		self.__spaceLabel	= dict["param3"]

		position = dict.readString( "param4" )
		if position:
			pos = utils.vector3TypeConvert( position )
			if pos is None:
				ERROR_MSG( "Vector3 Type Error：( SkillID %i ) Bad format '%s' in section param4 " % ( self.getID(), position ) )
			else:
				self.__targetPosition = pos

		self.__range	= int( dict["param5"] )
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
		spaceLabel = BigWorld.getSpaceDataFirstForKey( caster.spaceID, csconst.SPACE_SPACEDATA_KEY )
		if spaceLabel != self.__spaceLabel:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET
		
		if self.__targetPosition.distTo( caster.position ) < self.__range:
			return csstatus.SKILL_USE_ITEM_WRONG_TARGET

		if caster.checkItemsPlaceIntoNK_( [items.instance().createDynamicItem( self.__itemID, self.__amount )] ):
			caster.client.onStatusMessage( csstatus.KITBAG_IS_FULL, "" )
			return csstatus.SKILL_USE_ITEM_NEED_ONE_BLANK

		return Spell_Item.useableCheck( self, caster, target)


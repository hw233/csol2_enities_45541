# -*- coding: gb18030 -*-
#
# $Id: SkillItem.py,v 1.7 2008-08-20 09:54:57 fangpengjun Exp $

"""
implement skilllist item class
"""

from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.SkillItem import SkillItem as SItem
#from guis.controls.StaticText import StaticText
from guis.controls.CircleCDCover import CircleCDCover as Cover
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.otheruis.AnimatedGUI import AnimatedGUI

class SkillItem( Control ) :
	def __init__( self, item ) :
		Control.__init__( self, item )
		self.__pyItemBg = PyGUI( item.skBg )
		self.__pyItem = SItem( item.item )
		self.__pyItem.onRClick.bind( self.__onItemRClick )
		self.__pyItem.dragMark = DragMark.PETSKILL_BAR
		self.__pyItem.crossFocus = False

		self.__pyCover = Cover( item.item.circleCover )
		self.__pyCover.crossFocus = False

		self.__pyOverCover = AnimatedGUI( item.item.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )				# 动画播放一次，共8帧
		self.__pyOverCover.cycle = 0.4									# 循环播放一次的持续时间，单位：秒
		self.__pyCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )

		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_PET_BEGIN_COOLDOWN"] = self.__beginCooldown
#		self.__triggers["EVT_ON_KITBAG_ITEM_INFO_CHANGED"] = self.__itemInfoChanged
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )
		self.__triggers = {}

	# -------------------------------------------------
	def __beginCooldown( self, cooldownType, lastTime ) :
		"""
		when cooldown triggered, it will be called
		"""
		if self.itemInfo is None : return
		if self.itemInfo.isCooldownType( cooldownType ) :
			cdInfo = self.itemInfo.getCooldownInfo()
			self.__pyCover.unfreeze( *cdInfo )


#	def __itemInfoChanged( self, kitbagOrder, itemOrder, itemInfo ) :
#		"""
#		"""
#		if not self.itemInfo : return
#		if self.__pyItem.icon[0] != skill.getSkill( self.itemInfo.id ).getIcon():
#			self.__pyItem.icon = skill.getSkill( self.itemInfo.id ).getIcon()

	# -------------------------------------------------
	def __onItemRClick( self, pyItem ) :
		if self.itemInfo is not None :
			if self.itemInfo.isPassive:
				return
			self.itemInfo.spell()
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		self.__pyItem.update( itemInfo )
		infoText = ""
		skillPro = ""
		self.__pyItem.crossFocus = itemInfo is not None
		if itemInfo is not None :
			cdInfo = itemInfo.getCooldownInfo()
			util.setGuiState( self.__pyItemBg.getGui(), ( 1, 2 ), ( 1, 1 ) )
			self.__pyCover.unfreeze( *cdInfo )
		else :
			self.__pyCover.reset( 0 )
			util.setGuiState( self.__pyItemBg.getGui(), ( 1, 2 ), ( 1, 2 ) )

	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItemInfo( self ) :
		return self.__pyItem.itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__pyItem.itemInfo = itemInfo

	def _getPyItem( self ) :
		return self.__pyItem

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	itemInfo = property( _getItemInfo, _setItemInfo )
	pySItem = property( _getPyItem )


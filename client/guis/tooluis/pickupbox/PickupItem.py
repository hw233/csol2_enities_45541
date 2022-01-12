# -*- coding: gb18030 -*-
#
# $Id: PickupItem.py Exp $
"""
implement pickup item
"""
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.tooluis.CSRichText import CSRichText
from ItemsFactory import ObjectItem as ItemInfo
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import GUIFacade
import csdefine

g_image =  PL_Image.getSource("%s")	#获取格式化的图片

class PickupItem( Control ):
	def __init__( self ):
		pickItem = GUI.load( "guis/tooluis/pickupbox/item.gui" )
		uiFixer.firstLoadFix( pickItem )
		Control.__init__( self, pickItem )
		self.crossFocus = False
		self.dragFocus = False
		self.focus = False
		self.__pyItemPanel = PyGUI( pickItem.itemPanel )
		self.__pyItemFrame = PyGUI( pickItem.itemBg ) #物品格
		self.__limited = False
		self.__panelState = ( 1, 1 )
		self.__selected = False
		self.setItem( pickItem )
		self.pyRichInfo = CSRichText()
		self.__pyItemPanel.addPyChild( self.pyRichInfo )
		self.pyRichInfo.top = 7.0
		self.pyRichInfo.left = 7.0
		self.pyRichInfo.maxWidth = self.__pyItemPanel.width
		self.pyRichInfo.lineFlat = "T"
		self.pyRichInfo.align = "L"
		self.pyRichInfo.maxWidth = self.__pyItemPanel.width - 3.0

		self.__pyCover = PyGUI( pickItem.cover )
		self.selected = False
		self.itemInfo = None

	def setItem( self, pickItem ):
		self.pyPickItems = Item( pickItem.item, self )

	def __select( self ):
		self.panelState = ( 3, 1 )
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		self.panelState = ( 1, 1 )
		if self.__pyCover:
			self.__pyCover.visible = False
	# -------------------------------------------------------------
	# public
	# -------------------------------------------------------------
	def update( self, pickData ):
		itemInfo = None
		index = -1
		if pickData is not None:
			index = pickData["order"]
			itemInfo = ItemInfo( pickData["item"] )
			player = BigWorld.player()
			baseItem = itemInfo.baseItem
			self.pyPickItems.color = 255, 255, 255, 255
			if baseItem.isEquip() : #不合适主角使用的物品变成红色
				if not baseItem.canWield( player ):
					self.pyPickItems.color = 255,100,100,200
			elif player.level < baseItem.getReqLevel():
				self.pyPickItems.color = 255,100,100,200
			name = itemInfo.name()
			amount = baseItem.getAmount()
			amountStr = ""
			if amount > 1:
				if baseItem.id == 60101001: #金钱
					gold = amount/10000
					sliver = amount % 10000 / 100
					copper = amount % 10000 % 100
					goldicon =  g_image % ("guis/controls/goldicon.gui")
					silvericon =  g_image % ("guis/controls/silvericon.gui")
					coppericon = g_image % ("guis/controls/coinicon.gui")
					amountStr = "(%d%s%d%s%d%s)"%( gold, goldicon, sliver, silvericon, copper, coppericon )
				else:
					amountStr = "(%s)" % amount
			self.pyRichInfo.text = PL_Font.getSource( name + amountStr, fc = baseItem.getQualityColor() )
			self.pyPickItems.crossFocus = True
			util.setGuiState( self.__pyItemFrame.getGui(), ( 1, 2 ), ( 1, 1 ) ) #设置物品格明暗
		else:
			self.pyRichInfo.text = ""
			self.pyPickItems.crossFocus = False
			util.setGuiState( self.__pyItemFrame.getGui(), ( 1, 2 ), ( 1, 2 ) ) #设置物品格明暗
			self.__pyCover.visible = False
		self.panelState = ( 1, 1 )
		self.pyPickItems.update( index, itemInfo )
		self.index = index
		self.itemInfo = itemInfo

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected

	def _getPanelState( self ):
		return self.__panelState

	def _setPanelState( self, state ):
		self.__panelState = state
		elements = self.__pyItemPanel.getGui().elements
		for ename, element in elements.items():
			element.mapping = util.getStateMapping( element.size, UIState.MODE_R3C1, state )
			if ename in ["frm_rt", "frm_r", "frm_rb"]:
				element.mapping = util.hflipMapping( element.mapping )

	def _getLimited( self ):
		return self.__limited

	def _setLimited( self, limited ):
		self.__limited = limited

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	selected = property( _getSelected, _setSelected )
	panelState = property( _getPanelState, _setPanelState )
	limited = property( _getLimited, _setLimited )

class PickupQuestItem( PickupItem ):
	"""
	"""
	def setItem( self, pickItem ):
		self.pyPickItems = QuestItem( pickItem.item, self )

# --------------------------------------------------------------------
class Item( BOItem ):
	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.dragFocus = True
		self.selectable = True
		self.description = ""
		self.index = -1
		self.__initialize( item )

	def __initialize( self, item ) :
		if item is None : return

	def dispose( self ) :
		BOItem.dispose( self )

	def onMouseEnter_( self ):
		self.onDescriptionShow_()
		toolbox.itemCover.highlightItem( self )
		self.pyBinder.panelState = ( 2, 1 )

	def onMouseLeave_( self ):
		BOItem.onMouseLeave_( self )
		self.pyBinder.panelState = ( 1, 1 )
		return True

	def onDescriptionShow_( self ):
		dsp = self.description
		if dsp is None : return
		if dsp == [] : return
		if dsp == "" : return
		selfDsp = dsp
		equipCount = 0
		equipDsps = GUIFacade.getSameTypeEquipDecriptionsII( self.itemInfo )
		toolbox.infoTip.showItemTips( self, selfDsp, *equipDsps )

	def onRClick_( self,mods ): #右键点击获取
		BOItem.onRClick_( self, mods )
		player = BigWorld.player()
		if self.itemInfo is None:return
		if mods == 0:
			if self.pyBinder.limited:
				return
			if BigWorld.entities.has_key( player.currentItemBoxID ):
				#if player.isCaptain() and player.pickUpState == csdefine.TEAM_PICKUP_STATE_SPECIFY:
				#	# 如果玩家是队长而且队伍为队长分配模式，就要弹出分配窗口
				#	self._allcateMenu = self._createMenu()
				#	self._allcateMenu.show()
				#else:
				#	# 否则直接拾取
				BigWorld.entities[player.currentItemBoxID].pickUpItemByIndex( self.index )
		return True

	def onLClick_( self, mods ): #左键点击获取
		BOItem.onLClick_( self, mods )
		player = BigWorld.player()
		if self.itemInfo is None:return
		if mods == 0:
			if self.pyBinder.limited:
				return
			if BigWorld.entities.has_key( player.currentItemBoxID ):
				#if player.isCaptain() and player.pickUpState == csdefine.TEAM_PICKUP_STATE_SPECIFY:
				#	# 如果玩家是队长而且队伍为队长分配模式，就要弹出分配窗口
				#	self._allcateMenu = self._createMenu()
				#	self._allcateMenu.show()
				#else:
				#	# 否则直接拾取
				BigWorld.entities[player.currentItemBoxID].pickUpItemByIndex( self.index )
		return True

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		BOItem.onDragStart_( self, pyDragged )
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		return True

	# -----------------------------------------------
	# public
	# -----------------------------------------------
	def update( self, index, itemInfo ) :
		"""
		update item
		"""
		BOItem.update( self, itemInfo )
		self.index = index


class QuestItem( Item ):
	"""
	"""
	def onLClick_( self, mods ): #左键点击获取
		BOItem.onLClick_( self, mods )
		player = BigWorld.player()
		if self.itemInfo is None:return
		if mods == 0:
			if self.pyBinder.limited:
				return
			if BigWorld.entities.has_key( player.currentQuestItemBoxID ):
				BigWorld.entities[player.currentQuestItemBoxID].pickUpItemByIndex( self.index )
		return True

	def onRClick_( self,mods ): #右键点击获取
		BOItem.onRClick_( self, mods )
		player = BigWorld.player()
		if self.itemInfo is None:return
		if mods == 0:
			if self.pyBinder.limited:
				return
			if BigWorld.entities.has_key( player.currentQuestItemBoxID ):
				BigWorld.entities[player.currentQuestItemBoxID].pickUpItemByIndex( self.index )
		return True
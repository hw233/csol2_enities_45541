# -*- coding: gb18030 -*-
#
# $Id: PetEnhance.py, Exp $

"""
implement petEnhance
"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.controls.ButtonEx import HButtonEx
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import event.EventCenter as ECenter
from PetFormulas import formulas
import csdefine
import csconst
import random
import csstatus

class PetEnhance( Window ):

	__enhancePoints = {} # 强化已用、剩余点
	__enhancePoints["corporeity"]		= ( "ec_corporeity", "ecrm_corporeity" )#体质
	__enhancePoints["strength"]		= ( "ec_strength",  "ecrm_strength" )# 力量
	__enhancePoints["intellect"]		= ( "ec_intellect" , "ecrm_intellect" )# 智力
	__enhancePoints["dexterity"]		= ( "ec_dexterity", "ecrm_dexterity" ) # 敏捷
	__enhancePoints["freepoint"]		= ( "ec_free", "ecrm_free" ) # 自由加点

	def __init__( self ):
		wnd = GUI.load( "guis/general/petswindow/petpanel/enhancebox/box.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.canBeUpgrade_ 	 = True
		self.escHide_ 		 = True

		self.__triggers = {}
		self.registerTriggers_()
		self.isCurse = False
		self.__dbid = -1
		self.__initialize( wnd )
		self.symbolUid = 0

	def __initialize( self, wnd ):
		self.__pySoulItme = EnhanceItem( wnd.soulItem, "soulStone" )			#魂魄石
		self.__pySoulItme.updateInfo( None )
		self.__pySymbolItem = EnhanceItem( wnd.symbolItem, "pointSymbol" )		#点化符
		self.__pySymbolItem.updateInfo( None )

		self.__pyRtInfo = CSRichText( wnd.rtInfo )
		self.__pyRtInfo.foreColor = ( 230, 227, 185, 255 )
		self.__pyRtInfo.text = ""

		self.__pyCheckSmelt = CheckBoxEx( wnd.checkBox )
		self.__pyCheckSmelt.checked = False
		self.__pyCheckSmelt.onCheckChanged.bind( self.__onSmeltCheck )
		labelGather.setPyBgLabel( self.__pyCheckSmelt, "PetsWindow:PetEnhance", "checkBox" )

		self.__pyBtnShut = HButtonEx( wnd.btnShut )
		self.__pyBtnShut.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnShut.onLClick.bind( self.__onShut )
		labelGather.setPyBgLabel( self.__pyBtnShut, "PetsWindow:PetEnhance", "btnShut" )

		self.__pyEnhancePoints = {}
		self.__pyEnhanceBtns = {}
		for name, item in wnd.children: #各强化类型
			if name.endswith( "_btn" ):
				enhanceType = name.split( "_" )[0]
				pyEnhanceBtn = AttrButton( item, self )
				pyEnhanceBtn.setExStatesMapping( UIState.MODE_R4C1 )
				pyEnhanceBtn.enable = False
				pyEnhanceBtn.onLClick.bind( self.__onPetEnhance )
				pyEnhanceBtn.enhanceType = enhanceType
				labelGather.setPyBgLabel( pyEnhanceBtn, "PetsWindow:PetEnhance", name )
				self.__pyEnhanceBtns[enhanceType] = pyEnhanceBtn

			if name.endswith( "_point" ):
				enhanceType = name.split( "_" )[0]
				pyEnhancePoint = EnhancePoint( item )
				pyEnhancePoint.updatePoint( ( -1, -1 ) )
				pyEnhancePoint.text = labelGather.getText( "PetsWindow:PetEnhance", "remainTimes" )
				self.__pyEnhancePoints[enhanceType] = pyEnhancePoint
				
		self.__pyStSoul = StaticText( wnd.soulItem.sText )
		self.__pyStSoul.fontSize = 12
		self.__pyStSoul.charSpace = -2
		self.__pyStSoul.text = labelGather.getText( "PetsWindow:PetEnhance", "stSoul" )
		
		self.__pyStSymbol = StaticText( wnd.symbolItem.sText )
		self.__pyStSymbol.fontSize = 12
		self.__pyStSymbol.charSpace = -2
		self.__pyStSymbol.text = labelGather.getText( "PetsWindow:PetEnhance", "stSymbol" )

		labelGather.setLabel( wnd.lbTitle, "PetsWindow:PetEnhance", "lbTitle" )
		labelGather.setLabel( wnd.freedomText, "PetsWindow:PetEnhance", "freedomText" )
#		labelGather.setLabel( wnd.soulItem.sText, "PetsWindow:PetEnhance", "stSoul" )
#		labelGather.setLabel( wnd.symbolItem.sText, "PetsWindow:PetEnhance", "stSymbol" )
		labelGather.setLabel( wnd.infoBg.bgTitle.stTitle, "PetsWindow:PetEnhance", "enhanceExp" )

	# -----------------------------------------------------------
	# pravite
	# -----------------------------------------------------------
	def registerTriggers_( self ):
		self.__triggers["EVT_ON_PET_ATTR_CHANGED"]		= self.__onAttrUpdate
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] 	= self.__onRemoveItem
		self.__triggers["EVT_ON_ENHANCE_UPDATE_SOUL"]	= self.__onUpdateSoul
		self.__triggers["EVT_ON_ENHANCE_UPDATE_SYMBOL"] = self.__onUpdateSymbol
		self.__triggers["EVT_ON_ENHANCE_REMOVE_ITEM"] = self.__onRemoveItem
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onUpdateItems

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def deregisterTriggers_( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )
	# ---------------------------------------------------------------------
	def __onAttrUpdate( self, dbid, attrName ):
		"""
		更新已用、剩余强化点数
		"""
		if self.__dbid != dbid:return
		petEmtion = BigWorld.player().pcg_getPetEpitomes()[dbid]
		for typeTag, attrTuple in self.__enhancePoints.iteritems():
			value0 = getattr( petEmtion, attrTuple[0] )
			value1 = getattr( petEmtion, attrTuple[1] )
			self.__pyEnhancePoints[typeTag].updatePoint( ( value0, value1) )

	def __onRemoveItem( self, itemInfo ):
		"""
		从包裹移除物品回调
		"""
		id = itemInfo.id
		uid = itemInfo.uid
		for pyEnhanceBtn in self.__pyEnhanceBtns.itervalues():
			if id in self.__getStoneLists(): #移除魂魄石，则强化按钮全部不可用
				pyEnhanceBtn.enable = False
				self.__pyCheckSmelt.checked = False
			if id in csconst.PET_DIRECT_ITEMS: #移除点化符
				if self.__pySoulItme.itemInfo: #如果有魂魄石对应强化按钮可用
					soulID = self.__pySoulItme.itemInfo.id
					enhanceType = pyEnhanceBtn.enhanceType
					idsTuple = csconst.pet_enhance_stones.get( enhanceType, () )
					pyEnhanceBtn.enable = soulID in idsTuple
				self.symbolUid = 0
		for pyEnhanceItem in [self.__pySoulItme, self.__pySymbolItem]:
			if pyEnhanceItem.itemInfo is None:continue
			if pyEnhanceItem.itemInfo.uid == uid:
				pyEnhanceItem.updateInfo( None )
	
	def __onUpdateItems( self, itemInfo ):
		"""
		更新点化符数量
		"""
		if itemInfo is None: return
		if not self.symbolUid: return
		if itemInfo.uid != self.symbolUid: return
		id = itemInfo.id
		if id in csconst.PET_DIRECT_ITEMS:
			self.__onUpdateSymbol( itemInfo )

	def __onUpdateSoul( self, itemInfo ):
		"""
		更新魂魄石
		"""
		self.__pySoulItme.updateInfo( itemInfo )
		id = itemInfo.id
		for enType, idsTuple in csconst.pet_enhance_stones.iteritems():
			self.__pyEnhanceBtns[enType].enable = id in idsTuple

	def __onUpdateSymbol( self, itemInfo ):
		"""
		更新点化符
		"""
		self.symbolUid = itemInfo.uid
		self.__pySymbolItem.updateInfo( itemInfo )

	def __onPetEnhance( self, pyEnhanceBtn ):
		"""
		点击强化
		"""
		enhanceType = pyEnhanceBtn.enhanceType
		epitome = BigWorld.player().pcg_getPetEpitomes()[self.__dbid]
		soulItem = self.__pySoulItme.itemInfo
		soulItemUid = soulItem.uid
		if self.__pySymbolItem.itemInfo:#自由强化
			epitome.enhance( csdefine.PET_ENHANCE_FREE, enhanceType, self.isCurse, soulItemUid, self.symbolUid )
		else: #普通强化
			epitome.enhance( csdefine.PET_ENHANCE_COMMON, enhanceType, self.isCurse, soulItemUid, self.symbolUid )

	def __onSmeltCheck( self, checked ):
		"""
		判断玩家背包中是否有强化精炼符
		"""
		if self.__dbid <= 0 : return
		player = BigWorld.player()
		epitome = player.pcg_getPetEpitomes()[self.__dbid]
		itemInfo = epitome.getSymbolInfo()
		if checked:
			symbolInfo = itemInfo
			# 在放入充满的魂魄石前“优先选择精炼符”框不能被勾选
			if self.__pySoulItme.itemInfo is None:
				player.statusMessage( csstatus.SYMBOL_USE_EXPLAIN )
				self.__pyCheckSmelt.checked = False
				return
		else:
			symbolInfo = None
		self.isCurse = itemInfo is not None and checked

	def __onShut( self ):
		self.hide()

	def __getStoneLists( self ):
		stonesList = []
		for itemlist in csconst.pet_enhance_stones.itervalues():
			stonesList += itemlist
		return stonesList
	# ------------------------------------------------------------
	# public
	# ------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )
	
	def getSymbolInfo( self ):
		return self.__pySymbolItem

	def show( self, dbid, pyBinder = None ) :
		self.__dbid = dbid
		self.isCurse_ = False
		self.__pyRtInfo.text = labelGather.getText( "PetsWindow:PetEnhance", "explain" )
		petEmtion = BigWorld.player().pcg_getPetEpitomes()[dbid]
		for typeTag, attrTuple in self.__enhancePoints.iteritems():
			value0 = getattr( petEmtion, attrTuple[0] )
			value1 = getattr( petEmtion, attrTuple[1] )
			self.__pyEnhancePoints[typeTag].updatePoint( ( value0, value1) )
		Window.show( self, pyBinder )

	def __onUpdateInfo( self, itemInfo ) :
		self.__onSmeltCheck( self.__pyCheckSmelt.checked )

	def hide( self ):
		Window.hide( self )

# -------------------------------------------------------------------
# 魂魄石、点化符物品类
class EnhanceItem( PyGUI ):

	def __init__( self, item, itemType = "" ):
		PyGUI.__init__( self, item )
		self.__pyItemBg = PyGUI( item.itemBg )
		self.__pyEnhanceItem = Item( item.item, itemType, self )
		self.__kitbagID = -1
		self.__orderID = -1
		self.__itemInfo = None

	def updateInfo( self, itemInfo ):
		self.__itemInfo = itemInfo
		self.__pyEnhanceItem.update( itemInfo )
		if itemInfo:
			util.setGuiState( self.__pyItemBg.getGui(), ( 1, 2 ), ( 1, 2 ) )
		else:
			util.setGuiState( self.__pyItemBg.getGui(), ( 1, 2 ), ( 1, 1 ) )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItemInfo( self ):
		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	itemInfo = property( _getItemInfo, _setItemInfo )

# ----------------------------------------------------------
class Item( BOItem ):
	def __init__( self, item, itemType = "", pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.focus = True
		self.itemType = itemType
		self.__itemInfo = None
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __clearItem( self ):
		ECenter.fireEvent( "EVT_ON_ENHANCE_REMOVE_ITEM", self.itemInfo )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ) :
		BOItem.onRClick_( self, mods )
		if self.itemInfo is None:return
		self.__clearItem( ) # 移除任务提交物品
		return True

	def onDragStop_( self, pyDrogged ) :
		BOItem.onDragStop_( self, pyDrogged )
		if self.itemInfo is None:return
		if ruisMgr.isMouseHitScreen() :
			self.__clearItem( )
		return True

	def onDrop_( self,  pyTarget, pyDropped ) :
		if pyDropped.dragMark != DragMark.KITBAG_WND : return
		itemInfo = pyDropped.itemInfo
		id = itemInfo.id
		if self.itemType == "soulStone": #魂魄石
			if not id in self.getStoneLists():
				BigWorld.player().statusMessage( csstatus.STONE_MUST_BE_PUT_FIRST )
				return
			baseItem = itemInfo.baseItem
			if not baseItem.isFull():
				BigWorld.player().statusMessage( csstatus.STONE_MUST_FULL )
				return
			ECenter.fireEvent( "EVT_ON_ENHANCE_UPDATE_SOUL", itemInfo )
		else:
			if id not in csconst.PET_DIRECT_ITEMS: #不是点化符
				BigWorld.player().statusMessage( csstatus.SYMBOL_MUST_BE_PUT )
				return
			ECenter.fireEvent( "EVT_ON_ENHANCE_UPDATE_SYMBOL", itemInfo )
		BOItem.onDrop_( self, pyTarget, pyDropped )
		return True

	def getStoneLists( self ):
		stonesList = []
		for itemlist in csconst.pet_enhance_stones.itervalues():
			stonesList += itemlist
		return stonesList

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BOItem.update( self, itemInfo )
		self.itemInfo = itemInfo

	def _getItemInfo( self ):

		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	itemInfo = property( _getItemInfo, _setItemInfo )			# get or set the checking state of the checkbox

# --------------------------------------------------------------------
#强化已用和剩余点数控件类
class EnhancePoint( PyGUI ):

	def __init__( self, ptItem ):
		PyGUI.__init__( self, ptItem )
		self.__pyStUsed = StaticText( ptItem.stUsed )
		self.__pyStUsed.text = ""

		self.__pyStText = StaticText( ptItem.ptText )
		self.__pyStRemain = StaticText( ptItem.stRemain )
		self.__pyStRemain.text = ""

	def updatePoint( self, valueTuple ):
		if valueTuple == (-1, -1 ):
			self.__pyStUsed.text = ""
			self.__pyStRemain.text = ""
		else:
			self.__pyStUsed.text = "X%d"%valueTuple[0]
			self.__pyStRemain.text = str( valueTuple[1] )

	def clearPoint( self ):
		self.__pyStUsed.text = ""
		self.__pyStRemain.text = ""

	def _getText( self ):
		return self.__pyStText.text

	def _setText( self, text ):
		self.__pyStText.text = text

	text = property( _getText, _setText )
	
class AttrButton( HButtonEx ):
	def onMouseEnter_( self ) :
		HButtonEx.onMouseEnter_( self )
		if self.enable:
			actPet = BigWorld.player().pcg_getActPet()
			species = actPet.species
			enhanceType = self.enhanceType
			if self.pyBinder.getSymbolInfo().itemInfo:#自由强化
				count = actPet.ec_free
				minValue,maxValue = formulas.getEnhanceValue( species, csdefine.PET_ENHANCE_FREE, enhanceType, count + 1  )
			else:
				count = getattr( actPet, "ec_" + enhanceType )
				minValue,maxValue = formulas.getEnhanceValue( species, csdefine.PET_ENHANCE_COMMON, enhanceType, count + 1  )
			attrName = labelGather.getText( "PetsWindow:PetEnhance", enhanceType )
			tips = labelGather.getText( "PetsWindow:PetEnhance","btnTips", attrName, minValue, maxValue )
			
			toolbox.infoTip.showToolTips( self, tips )
			
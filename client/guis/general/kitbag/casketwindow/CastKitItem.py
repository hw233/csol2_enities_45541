# -*- coding: gb18030 -*-
#
# $Id: ObjectItem.py
from guis import *
import Language
import BigWorld
import csdefine
import csstatus
import csconst
from LabelGather import labelGather
from guis.controls.BaseObjectItem import BaseObjectItem
from guis.controls.Control import Control
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
import ItemTypeEnum
import GUIFacade
from guis.MLUIDefine import ItemQAColorMode
from guis.common.PyGUI import PyGUI
import Define
from config.client.msgboxtexts import Datas as mbmsgs
from OblivYesNoBox import OblivYesNoBox

class ExtractItem( Control ) :
	#石头格
	def __init__( self, item, pyBinder, tag = "" ) :
		Control.__init__( self, item, pyBinder )
		self.focus = True
		self.dropFocus = True
		self.tag = tag

		self.__pyIcon = BaseObjectItem( item.item )
		self.__pyIcon.dropFocus = False
		self.__pyIcon.dragFocus = tag == "draw"
		self.__pyIcon.focus = False
		self.__pyIcon.onMouseEnter.bind( self.__onItemMouseEnter )
		self.__pyIcon.onMouseLeave.bind( self.__onItemMouseLeave )
		self.__pyIcon.onDragStop.bind( self. __onDragStop )
		self.__pyIcon.pyLbAmount_.font = "MSYHBD.TTF"
		self.__pyIcon.fontSize = 12.0
		self.__pyIcon.pyLbAmount_.charSpace = -2.0
		
		if hasattr( item, "lockIcon" ):
			item.lockIcon.visible = False
		
		if hasattr( item, "cover" ):
			item.cover.visible = False
		self.pyItemBg_ = None
		if hasattr( item, "itemBg" ):
			self.pyItemBg_ = PyGUI( item.itemBg )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		拖放物品
		"""
		Control.onDrop_( self, pyTarget, pyDropped )
		if DragMark.KITBAG_WND == pyDropped.dragMark : 			# 从背包拖来的
			self.pyBinder.onStoneDrop__( pyTarget, pyDropped )
			GUIFacade.dehighLightEquipItem( pyDropped.kitbagID, pyDropped.gbIndex )
		return True

	def onRClick_( self, mods ) :
		"""
		右键点击，移除物品
		"""
		self.pyBinder.onItemRemove__( self )
		return Control.onRClick_( self, mods )
	
	def __onDragStop( self, pyDragged ):
		"""
		拖放
		"""
		if pyDragged is None:return
		itemInfo = pyDragged.itemInfo
		if itemInfo is None:return
		if self.tag != "draw":return
		if not ruisMgr.isMouseHitScreen() : return
		if self.drawInfo is None:return
		player = BigWorld.player()
		index = self.index
		def query( rs_id ):
			if rs_id == RS_YES:
				player.delScrollSkill( index )
		OblivYesNoBox().show(  query, self.drawInfo, pyOwner = rds.ruisMgr.casketWindow.pyPanels[0] )
	
	def __onItemMouseEnter( self, pyItem ):
		"""
		鼠标进入
		"""
		if pyItem is None:return
		if self.itemInfo is None:
			self.pyBinder.onItemMouseEnter__( self )
	
	def __onItemMouseLeave( self ):
		"""
		鼠标进入
		"""
		if self.itemInfo is None:
			self.pyBinder.onItemMouseLeave__()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		self.__pyIcon.update( itemInfo )
		quality = itemInfo is None and 1 or itemInfo.quality
		util.setGuiState( self.gui, ( 4, 2 ), ItemQAColorMode[ quality ] )
		self.gui.lockIcon.visible = itemInfo is not None and itemInfo.baseItem.isBinded()
	
	def updateUseStatus( self, itemStatus ):
		"""
		更新图标状态
		"""
		self.__pyIcon.updateUseStatus( itemStatus )
	
	def setAmountText( self, amountText ):
		"""
		设置数量
		"""
		self.__pyIcon.amountText = amountText
	
	def setAmountColor( self, color ):
		"""
		设置数量颜色
		"""
		self.__pyIcon.amountColor = color

	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def itemInfo( self ) :
		return self.__pyIcon.itemInfo
	
	def _getDescription( self ) :
		return self.__pyIcon.description

	def _setDescription( self, dsp ) :
		self.__pyIcon.description = dsp

	description = property( _getDescription, _setDescription )			# 获取/设置 Item 的描述信息

class ExtractEquipItem( ExtractItem ) :
	#装备格
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		拖放物品
		"""
		Control.onDrop_( self, pyTarget, pyDropped )
		if DragMark.KITBAG_WND == pyDropped.dragMark : 			# 从背包拖来的
			self.pyBinder.onEquipDrop__( pyTarget, pyDropped )
			GUIFacade.dehighLightEquipItem( pyDropped.kitbagID, pyDropped.gbIndex )
		return True

class ExtractHierogramItem( ExtractItem ) :
	#神征令
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		拖放物品
		"""
		Control.onDrop_( self, pyTarget, pyDropped )
		if DragMark.KITBAG_WND == pyDropped.dragMark : 			# 从背包拖来的
			self.pyBinder.onHierogramDrop__( pyTarget, pyDropped )
			GUIFacade.dehighLightEquipItem( pyDropped.kitbagID, pyDropped.gbIndex )
		return True

# -----------------------------------------------------------------------------------------------------------
class CastKitItem( Control ):
	def __init__( self, item, pyBinder = None ):
		Control.__init__( self, item )
		self.crossFocus = False
		self.dragFocus = False
		self.pyCover_ = None
		self.pyLbAmount_ = None
		self.pyRtName_ = CSRichText( item.rtName )
		self.pyRtName_.align = "C"
		self.pyRtName_.lineFlat = "M"
		self.pyRtName_.top = 13.0
		self.itemPanel = item.itemPanel
		self.pyItemBg = PyGUI( item.itemBg )
		self._pyLbAmount = None
		self.pyCover_ = None
		if hasattr( item, "cover" ) :
			self.pyCover_ = PyGUI( item.cover )
			self.pyCover_.visible = False
		if hasattr( item.item, "lbAmount" ) :
			self._pyLbAmount = StaticText( item.item.lbAmount )
			self._pyLbAmount.text = ""
			self._pyLbAmount.font = "MSYHBD.TTF"
			self._pyLbAmount.fontSize = 12.0
		self.panelState = ( 1, 1 )

	def __setItemQuality( self, itemBg, quality ):
		util.setGuiState( itemBg, ( 4, 2 ), ItemQAColorMode[quality] )

	def __locate( self ):
		if self.pyRtName_.height > 35.0:
			self.pyRtName_.top = 8.0
			self.pyRtName_.fontSize = 12
		else:
			self.pyRtName_.top = 13.0
			self.pyRtName_.fontSize = 16

	# -------------------------------------------------------------
	# public
	# -------------------------------------------------------------
	def update( self, itemInfo ):
		if itemInfo is None:
			self.pyRtName_.text = ""
			self.__setItemQuality( self.pyItemBg.getGui(), 1 )
		else:
			quality = itemInfo.quality
			self.__setItemQuality( self.pyItemBg.getGui(), quality )
			self.pyRtName_.text = itemInfo.name()
		self.__locate()

	def _getPanelState( self ):
		return self.__panelState

	def _setPanelState( self, state ):
		self.__panelState = state
		elements = self.itemPanel.elements
		for ename, element in elements.items():
			element.mapping = util.getStateMapping( element.size, UIState.MODE_R3C1, state )
			if ename in ["frm_rt", "frm_r", "frm_rb"]:
				element.mapping = util.hflipMapping( element.mapping )

	def _getSelected( self ):
		return self._selected
		
	def _setSelected( self, selected ):
		if selected:
			self._select()
		else:
			self._deselect()
		self._selected = selected

	panelState = property( _getPanelState, _setPanelState )
	selected = property( _getSelected, _setSelected )

class CastKitEquip( CastKitItem ):
	"""
	带名称面板的装备格
	"""
	def __init__( self, item, pyBinder = None, tag = "" ):
		CastKitItem.__init__( self, item, pyBinder )
		self.__pyEquip = ExtractEquipItem( item.item, pyBinder, tag )

	# -------------------------------------------------------------
	# public
	# -------------------------------------------------------------
	def update( self, itemInfo ):
		CastKitItem.update( self, itemInfo )
		self.__pyEquip.update( itemInfo )

	@property
	def itemInfo( self ) :
		return self.__pyEquip.itemInfo
	

class CastKitStuff( CastKitItem ):
	"""
	带名称面板的材料
	"""
	def __init__( self, item, pyBinder = None, tag = "" ):
		CastKitItem.__init__( self, item, pyBinder )
		self.pyStuff_ = ExtractItem( item.item, pyBinder, tag )
		self.pyStuff_.tag = tag

	# -------------------------------------------------------------
	# public
	# -------------------------------------------------------------
	def update( self, itemInfo ):
		CastKitItem.update( self, itemInfo )
		self.pyStuff_.update( itemInfo )
	
	def setItemStatus( self, scount, count ):
		"""
		设置数量，型如:scount/count
		"""
		color = 255, 255, 255, 255
		itemStatus = Define.ITEM_STATUS_NATURAL
		if scount >= count:
			color = 0, 255, 0, 255
		else:
			color = 255, 0, 0, 255
			itemStatus = Define.ITEM_STATUS_USELESSNESS
		self.pyStuff_.updateUseStatus( itemStatus )
		amountText = ""
		if count > 0:
			amountText = "%d/%d"%( scount, count )
		self.pyStuff_.setAmountText( amountText )
		self.pyStuff_.setAmountColor( color )

	@property
	def itemInfo( self ) :
		return self.pyStuff_.itemInfo


class CastKitHierogram( CastKitItem ):
	"""
	带名称面板的材料
	"""
	def __init__( self, item, pyBinder = None, tag = "" ):
		CastKitItem.__init__( self, item, pyBinder )
		self.__pyHierogram = ExtractHierogramItem( item.item, pyBinder, tag )

	# -------------------------------------------------------------
	# public
	# -------------------------------------------------------------
	def update( self, itemInfo ):
		CastKitItem.update( self, itemInfo )
		self.__pyHierogram.update( itemInfo )
		if itemInfo is None:
			self.pyRtName_.text = labelGather.getText( "CasketWindow:AttrExtractPanel", "token" )

	@property
	def itemInfo( self ) :
		return self.__pyHierogram.itemInfo
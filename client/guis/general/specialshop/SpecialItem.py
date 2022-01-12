# -*- coding: gb18030 -*-
#
# $Id: SpecialItem.py,fangpengjun Exp $

"""
implement SpecialItem
"""
from guis import *
from LabelGather import labelGather
from guis.controls.Control import Control
from guis.common.PyGUI import PyGUI
from guis.controls.ButtonEx import HButtonEx
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.inputbox.InputBox import AmountInputBox
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from config.client.msgboxtexts import Datas as mbmsgs
from ItemsFactory import ObjectItem
from guis.MLUIDefine import ItemQAColorMode
import GUIFacade
import csdefine

class SpecialItem( Control ) :
	__yuanbaoUI = None

	def __init__( self, dragMark = 0, pyBinder = None ):
		item = GUI.load( "guis/general/specialshop/specitem.gui" )
		uiFixer.firstLoadFix( item )
		Control.__init__( self, item, pyBinder )
		self.focus = False
		self.crossFocus = False
		self.dragFocus = False
		self.dragMark = dragMark
		self.__pyCover = None
		self.__pyItem = Item( item.item, self.dragMark, self )
		self.__pyItemBg = PyGUI( item.itemBg )
		self.__pyRtName = CSRichText( item.rtName )
		self.__pyRtName.align = "L"
		self.__pyRtDsp = CSRichText( item.rtDsp )
		self.__pyRtDsp.align = "L"
		self.__pyRtDsp.maxWidth =190.0
		self.__pyRtMoney = CSRichText( item.rtCost )
		self.__pyRtMoney.align = "L"

		self.__pyBtnBuy = HButtonEx( item.btnBuy )
		self.__pyBtnBuy.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnBuy.onLClick.bind( self.__onBuy )
		labelGather.setPyBgLabel( self.__pyBtnBuy, "SpecialShop:main", "btnBuy" )

		if hasattr( item, "cover" ) :
			self.__pyCover = PyGUI( item.cover )
		self.__panelState = ( 1, 1 )
		self.selected = False

	# -------------------------------------------------------------
	# public
	# -------------------------------------------------------------
	def update( self, itemInfo ):
		name = ""
		self.__pyItem.crossFocus = itemInfo is not None
		self.__pyItem.dragFocus = itemInfo is not None
		self.__pyBtnBuy.visible = itemInfo is not None
		self.__pyItem.update( itemInfo )
		if itemInfo is not None:
			baseInfo = itemInfo.baseInfo
			baseItem = self.__pyItem.itemInfo.baseItem
			name = baseInfo.name()
			self.price = itemInfo.price
			priceText = self.__getGold( itemInfo.price, itemInfo.moneyType )
			self.__pyRtName.text = PL_Font.getSource( name, fc = ( 228, 225, 192, 255 ) )
			self.__pyRtMoney.text = PL_Font.getSource( priceText, fc = ( 16, 197, 165, 255 ) )
			self.__pyRtDsp.text = PL_Font.getSource( itemInfo.dsp, fc = ( 228, 225, 192, 255 ) )
			quality = baseInfo.quality
			self.__setItemQuality( self.__pyItemBg.getGui(), quality )
			self.__pyItem.amountText = ""
		else:
			self.selected = False
			self.__pyRtName.text = ""
			self.__pyRtMoney.text = ""
			self.__pyRtDsp.text = ""
			self.__setItemQuality( self.__pyItemBg.getGui(), 0 )

	def __setItemQuality( self, itemBg, quality ):
		util.setGuiState( itemBg, ( 4, 2 ), ItemQAColorMode[quality] )

	def getObjectItem( self ):
		return self.__pyItem

	def onClickToBuy( self, isSingle ) :
		pyItem = self.getObjectItem()
		if pyItem.itemInfo is None : return
		player = BigWorld.player()
		#baseItem = self.itemInfo.baseItem
		#ECenter.fireEvent( "EVT_ON_SPECIAL_ITEM_SLECTED", baseItem.id )
		# 用临时变量保存点击时对应的物品ID、价格、名称，以防玩家切换到其他商品窗口时物品ID随之发生变化，从而错买到其他商品 2008-12-9 modified by gjx
		itemID = pyItem.itemInfo.id
		itemPrice = pyItem.price
		itemName = pyItem.itemInfo.name()
		isAffirm = self.pyBinder.affirmBuy 	# 是否确认了
		moneyType = player.getSpeMoneyType()
		if hasattr( self.pyBinder, "moneyType" ):
			moneyType = self.pyBinder.moneyType
		if isSingle : 								# 购买一个
			if isAffirm:
				def query( rs_id ):
					if rs_id == RS_OK:
						player.spe_shopping( itemID, 1, moneyType )
				# "确定花费%d元宝购买1个%s?"
				showMessage( mbmsgs[0x07c1] % ( itemPrice, 1, itemName ), "", MB_OK_CANCEL, query, pyOwner = pyItem.pyTopParent )
				return True
			else:
				player.spe_shopping( itemID, 1, moneyType )
		else :										# 购买多个
			def split( result, amount ) :
				if result == DialogResult.OK :
					if isAffirm:
						def query( rs_id ):
							if rs_id == RS_OK:
								player.spe_shopping( itemID, amount, moneyType )
						# "确定花费%d元宝购买%d个%s?"
						showMessage( mbmsgs[0x07c1] % ( itemPrice*amount, amount, itemName ), "", MB_OK_CANCEL, query, pyOwner = rds.ruisMgr.specialShop )
						return True
					else:
						player.spe_shopping( itemID, amount, moneyType )
			rang = ( 1, 100 )
			AmountInputBox().show( split, pyItem, rang )
		return True

	def __onBuy( self ):
		pyItem = self.getObjectItem()
		if pyItem.itemInfo is None : return
		player = BigWorld.player()
		itemID = pyItem.itemInfo.id
		itemPrice = pyItem.price
		itemName = pyItem.itemInfo.name()
		isAffirm = self.pyBinder.affirmBuy
		moneyType = player.getSpeMoneyType()
		if hasattr( self.pyBinder, "moneyType" ):
			moneyType = self.pyBinder.moneyType
		if isAffirm:
			def query( rs_id ):
				if rs_id == RS_OK:
					player.spe_shopping( itemID, 1, moneyType )
			showMessage( mbmsgs[0x07c1] % ( itemPrice, 1, itemName ), "", MB_OK_CANCEL, query, pyOwner = pyItem.pyTopParent )
			return True
		else:
			player.spe_shopping( itemID, 1, moneyType )
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __select( self ):
		self.panelState = ( 3, 1 )
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		self.panelState = ( 1, 1 )
		if self.__pyCover:
			self.__pyCover.visible = False

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def onMouseEnter_( self ):
		Control.onMouseEnter_( self )
		if self.selected:return
		self.panelState = ( 2, 1 )

	def onMouseLeave_( self ):
		Control.onMouseLeave_( self )
		if self.selected:return
		self.panelState = ( 1, 1 )
		
	def __getGold( self, gold, moneyType = csdefine.SPECIALSHOP_MONEY_TYPE_GOLD ) :
		text = ""
		if gold:
			ybImage = None
			if moneyType == csdefine.SPECIALSHOP_MONEY_TYPE_GOLD:
				ybImage = PL_Image.getSource("guis/general/specialshop/yuanbao.gui")
			else:
				ybImage = PL_Image.getSource("guis/general/specialshop/silver.gui")
			if SpecialItem.__yuanbaoUI != ybImage:
				SpecialItem.__yuanbaoUI = ybImage
			text = str( gold ) + SpecialItem.__yuanbaoUI
		return text

	def _getPanelState( self ):
		return self.__panelState

	def _setPanelState( self, state ):
		self.__panelState = state
		elements = self.getGui().elements
		for ename, element in elements.items():
			if ename == "frm_bg":continue
			element.mapping = util.getStateMapping( element.size, UIState.MODE_R3C1, state )
			if ename in ["frm_rt", "frm_r", "frm_rb"]:
				element.mapping = util.hflipMapping( element.mapping )

	def _getItemInfo( self ):
		return self.__pyItem.itemInfo

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected

	def _getIcon( self ):
		return self.__pyItem.icon

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	panelState = property( _getPanelState, _setPanelState )
	itemInfo = property( _getItemInfo )
	selected = property( _getSelected, _setSelected )
	icon = property( _getIcon )

# -------------------------------------------------------------------------
from guis import *
import BigWorld
import event.EventCenter as ECenter
class Item( BOItem ):
	def __init__( self, item = None, dragMark = 0, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.focus = False
		self.crossFocus = False
		self.dragFocus = True
		self.selectable = True
		self.description = ""
		self.maxNum = csdefine.TRADE_MAX_GOODS_NUM
		self.dragMark = dragMark
		self.__initialize( item )

	def __initialize( self, item ) :
		if item is None : return

	def dispose( self ) :
		BOItem.dispose( self )

	def onMouseEnter_( self ):
#		BOItem.onMouseEnter_( self )
		toolbox.itemCover.highlightItem( self ) #这个放到self.onDescriptionShow_()后面会导致第一次高亮图标失败，原因未明！
		BigWorld.callback(0.5,self.wantToReadItemDescription)
		if self.dragMark != DragMark.SPECIAL_SHOP_WND or \
			self.itemInfo is None: return
		if self.pyBinder.selected:return
		self.pyBinder.panelState = ( 2, 1 )

	def wantToReadItemDescription(self):
		"""
		延迟0.5秒后，再显示物品描述信息
		"""
		if self.isMouseHit():
			self.onDescriptionShow_()

	def onMouseLeave_( self ):
		BOItem.onMouseLeave_( self )
		if self.dragMark != DragMark.SPECIAL_SHOP_WND or \
			self.itemInfo is None:return
		if self.pyBinder.selected:return
		self.pyBinder.panelState = ( 1, 1 )
		return True

	def onDescriptionShow_( self ):
#		BOItem.onDescriptionShow_( self )
		dsp = self.description
		if dsp is None : return
		if dsp == [] : return
		if dsp == "" : return
		selfDsp = dsp
		equipCount = 0
		equipDsps = GUIFacade.getSameTypeEquipDecriptionsII( self.itemInfo )
		toolbox.infoTip.showItemTips( self, selfDsp, *equipDsps )

	def onDescriptionHide_( self ):
		toolbox.infoTip.hide()

	"""
	def onRClick_( self, mods ):
		BOItem.onRClick_( self, mods )
		if self.itemInfo is None : return
		player = BigWorld.player()
		#baseItem = self.itemInfo.baseItem
		#ECenter.fireEvent( "EVT_ON_SPECIAL_ITEM_SLECTED", baseItem.id )
		# 用临时变量保存点击时对应的物品ID、价格、名称，以防玩家切换到其他商品窗口时物品ID随之发生变化，从而错买到其他商品 2008-12-9 changed by gjx
		itemID = self.itemInfo.id
		itemPrice = self.price
		itemName = self.itemInfo.name()
		isAffirm = self.pyTopParent.affirmBuy #是否确认了
		if mods == 0 : #购买一个
			if isAffirm:
				def query( rs_id ):
					if rs_id == RS_OK:
						player.spe_shopping( itemID, 1, player.getSpeMoneyType() )
				showMessage( labelGather.getText( "SpecialShop:main", "buyOneConfirm" )% ( itemPrice, itemName ), "", MB_OK_CANCEL, query, pyOwner = self.pyTopParent )
				return True
			else:
				player.spe_shopping( itemID, 1, player.getSpeMoneyType() )
		elif mods == MODIFIER_SHIFT: #购买多个
			def split( result, amount ) :
				if result == DialogResult.OK :
					if isAffirm:
						def query( rs_id ):
							if rs_id == RS_OK:
								player.spe_shopping( itemID, amount, player.getSpeMoneyType() )
						showMessage( labelGather.getText( "SpecialShop:main", "buyOneConfirm" )% ( itemPrice*amount, amount, itemName ), "", MB_OK_CANCEL, query, pyOwner = rds.ruisMgr.specialShop )
						return True
					else:
						player.spe_shopping( itemID, amount, player.getSpeMoneyType() )
			rang = ( 1, self.storeAmount )
			toolbox.amountInputBox.show( split, self, rang )
		return True

	def onLClick_( self, mods ):
		if not self.itemInfo: return
		BOItem.onLClick_( self, mods )
		player = BigWorld.player()
		#baseItem = self.itemInfo.baseItem
		#ECenter.fireEvent( "EVT_ON_SPECIAL_ITEM_SLECTED", baseItem.id )
		return True
	"""

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		BOItem.onDragStart_( self, pyDragged )
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		return True
	# -----------------------------------------------
	# public
	# -----------------------------------------------
	def update( self, itemInfo ) :
		"""
		update item
		"""
		if itemInfo is None:
			BOItem.update( self, itemInfo )
		else:
			BOItem.update( self, itemInfo.baseInfo )
			baseInfo = itemInfo.baseInfo
			self.price = itemInfo.price
			self.amountText = ""




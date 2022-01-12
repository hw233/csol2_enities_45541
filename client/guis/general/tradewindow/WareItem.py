# -*- coding: gb18030 -*-
#
# $Id: WareItem.py,v 1.37 2008-09-05 03:28:05 pengju Exp $

"""
implement ware item
"""
from guis import *
from guis.controls.Control import Control
from guis.common.PyGUI import PyGUI
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.tooluis.inputbox.InputBox import AmountInputBox
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from AbstractTemplates import MultiLngFuncDecorator
from LabelGather import labelGather
from guis.MLUIDefine import ItemQAColorMode, QAColor
from ItemsFactory import ObjectItem
import ItemTypeEnum
import GUIFacade
import csdefine
import ResMgr
import utils
import csstring

class WareItem( Control ) :
	"""
	NPC���׵���Ʒ��
	"""
	def __init__( self, item = None, dragMark = 0, pyBinder = None ):
		Control.__init__( self, item, pyBinder )
		self.crossFocus = False
		self.dragFocus = False
		self.__uid = -1
		self.dragMark = dragMark
		self.__pyCover = None
		self._pyLbAmount = None # ��Ʒ����

		self.itemPanel = item.itemPanel
		self.__pyItem = Item( item.item, self.dragMark, self )
		self.__pyItemBg = PyGUI( item.itemBg )
		
		self.__pyRtName = CSRichText( item.itemName )
#		self.__pyRtName.maxWidth = 93.0
		self.__pyRtName.crossFocus = True
		self.__pyRtName.onMouseEnter.bind( self.__onNameEnter )
		self.__pyRtName.onMouseLeave.bind( self.__onNameLeave )

		self.__pyRtMoney = CSRichText( item.itemCost )
		self.__pyRtMoney.crossFocus = True
		self.__pyRtMoney.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyRtMoney.onMouseLeave.bind( self.__onMouseLeave )
		self.__pyRtMoney.align = "R"
#		self.__pyRtMoney.fontSize = 12

		self._index  = -1
		if hasattr( item, "cover" ) :
			self.__pyCover = PyGUI( item.cover )

		if hasattr( item.item, "lbAmount" ) : # �������Ҫ����Ʒ������ʾ
			self._pyLbAmount = StaticText( item.item.lbAmount )
			self._pyLbAmount.text = ""
		self.__panelState = ( 1, 1 )
		self.selected = False

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ) :
		pass

	def onMouseEnter_( self ):
		Control.onMouseEnter_( self )
		if self.selected:return
		self.panelState = ( 2, 1 )

	def onMouseLeave_( self ):
		Control.onMouseLeave_( self )
		if self.selected:return
		self.panelState = ( 1, 1 )
		
	def haveEnoughCredit( self , item ):
		"""
		����Ƿ����㹻������
		@param  item : ��Ʒʵ��
		@type   item : ITEME
		@RETURN bool : �Ƿ���������������
		"""
		creditDic = item.credit()
		for key in creditDic:
			value = BigWorld.player().getPrestige( key )
			if value < creditDic[key]:
				return False
		return True
	
	def __onMouseEnter( self, pyRichText ):
		"""
		������һ�������Ʒ
		"""
		priceItem = GUIFacade.getPriceItem( self.index, 0 )
		if priceItem is None:return
		if priceItem.priceType == csdefine.INVOICE_NEED_ITEM:
			itemID = priceItem.itemID
			item = BigWorld.player().createDynamicItem( itemID )
			itemInfo = ObjectItem( item )
			toolbox.infoTip.showItemTips( self, itemInfo.description )
	
	def __onMouseLeave( self ):
		"""
		����뿪
		"""
		toolbox.infoTip.hide()
	
	def __onNameEnter( self, pyRichText ):
		"""
		��ʾ���Ƹ�����
		"""
		if self.itemInfo is None:return
		nameText = csstring.toString( self.__pyRtName.text )
		name = self.itemInfo.name()
		uname = csstring.toWideString( name )
		if len( uname ) > 4:
			toolbox.infoTip.showToolTips( self, name )
	
	def __onNameLeave( self ):
		"""
		�������Ƹ�����
		"""
		toolbox.infoTip.hide( self )

	# -------------------------------------------------------------
	# public
	# -------------------------------------------------------------
	def update( self, itemInfo ):
		if itemInfo is None:
			self.__pyRtName.text = ""
			self.__pyRtMoney.text = ""
			self.uid = -1
			self.__pyItem.update( -1, itemInfo )
			self.__pyItem.crossFocus = False
			util.setGuiState( self.__pyItemBg.getGui(), ( 4, 2 ), ItemQAColorMode[0] )
		else:
			index = itemInfo.index
			npcName = itemInfo.npcName
			baseInfo = itemInfo.baseInfo
			self.__pyItem.update( index, baseInfo )
			self.__pyItem.crossFocus = baseInfo is not None
			if baseInfo:
				player = BigWorld.player()
				baseItem = baseInfo.baseItem
				name = baseInfo.name()
				reqText = ""
				self.dragFocus  = True
				self.uid = baseInfo.uid
				if npcName == "TongChapman": #������ˣ����ﹱ����Ʒ����
					amount = GUIFacade.getInvoiceAmountByUid( self.uid ) # ����uid��ȡ��Ʒ����
					if amount > 1:
						self._pyLbAmount.text = amount
					else:
						if self._pyLbAmount:
							self._pyLbAmount.text = ""

					for text in GUIFacade.getInvoicePriceDescription( index ):
						reqText  += text
				elif npcName == "TongSpecialChapman":
					for text in GUIFacade.getTongSpecialItemPrice( index ):
						reqText  += text
				else: #�������ˣ��������
					if not self.haveEnoughCredit(baseItem):
						self.__pyItem.color = 255,100,100,200
					if self.dragMark == DragMark.NPC_TRADE_BUY:
						warIntegral = baseItem.query("warIntegral")
						if warIntegral > 0: #ս����Ʒ
							reqText = labelGather.getText( "TradeWindow:wareItem", "warPoint", warIntegral )
						else: #��ͨ��Ʒ
							for text in GUIFacade.getInvoicePriceDescription( index ):
								reqText  += text
				if self.dragMark == DragMark.NPC_TRADE_REDEEM: #
					uid = baseItem.getUid()
					price = GUIFacade.getSellItemPrice( uid )
					reqText = utils.currencyToViewText( price )
				self.__pyRtMoney.text = PL_Font.getSource( reqText, fc = ( 16, 197, 165, 255 ) )
				self.__pyItem.crossFocus = True
				foreColor = QAColor.get( baseItem.getQuality(), ( 255, 255, 255, 255 ))
				uname = csstring.toWideString( name )
				if len( uname ) > 4:
					uname = "%s..."%uname[:4]
				self.__pyRtName.text = PL_Font.getSource( uname, fc = foreColor )
				util.setGuiState( self.__pyItemBg.gui, ( 4, 2 ), ItemQAColorMode[ baseItem.getQuality() ] )
			else:
				if self._pyLbAmount: # �����Ʒ�����ڣ����������Ʒ������
					self._pyLbAmount.text = ""
				self.__pyRtName.text = ""
				self.__pyRtMoney.text = ""
				self.uid = -1
				self.__pyItem.crossFocus = False
				util.setGuiState( self.__pyItemBg.getGui(), ( 4, 2 ), ItemQAColorMode[0] )
			self.index = index

	def _select( self ):
		self.panelState = ( 3, 1 )
		if self.__pyCover:
			self.__pyCover.visible = True

	def _deselect( self ):
		self.panelState = ( 1, 1 )
		if self.__pyCover:
			self.__pyCover.visible = False

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def getObjectItem( self ):
		return self.__pyItem

	# -------------------------------------------------

	# -------------------------------------------------
	def _getIndex( self ):
		return self._index

	def _setIndex( self, index ):
		self._index = index

	def _getUid( self ):
		return self.__uid

	def _setUid( self, uid ):
		"""
		NPC������Ʒ��uid����set
		"""
		self.__uid = uid

	def _getPanelState( self ):
		return self.__panelState

	def _setPanelState( self, state ):
		self.__panelState = state
		elements = self.itemPanel.elements
		for ename, element in elements.items():
			element.mapping = util.getStateMapping( element.size, UIState.MODE_R3C1, state )
			if ename in ["frm_rt", "frm_r", "frm_rb"]:
				element.mapping = util.hflipMapping( element.mapping )

	def _getItemInfo( self ):
		return self.__pyItem.itemInfo

	def _getSelected( self ):
		return self._selected

	def _setSelected( self, selected ):
		if selected:
			self._select()
		else:
			self._deselect()
		self._selected = selected

	def _getIcon( self ):
		return self.__pyItem.icon
	
	def _getPyItem( self ):
		return self.__pyItem

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	index = property( _getIndex, _setIndex )
	uid = property( _getUid, _setUid )
	panelState = property( _getPanelState, _setPanelState )
	itemInfo = property( _getItemInfo )
	selected = property( _getSelected, _setSelected )
	icon = property( _getIcon )
	pyItem = property( _getPyItem )

# -------------------------------------------------------------------------
from guis import *
import BigWorld
class Item( BOItem ):
	def __init__( self, item = None, dragMark = 0, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.focus = True
		self.crossFocus = False
		self.dragFocus = True
		self.selectable = True
		self.description = ""
		self.maxNum = csdefine.TRADE_MAX_GOODS_NUM
		self.dragMark = dragMark
		self.index = -1
		self._initialize( item )
		self.callbackID=0

	def _initialize( self, item ) :
		if item is None : return

	def dispose( self ) :
		BOItem.dispose( self )

	def onMouseEnter_( self ):
		"""
		�����봥��
		"""
		self.callbackID = BigWorld.callback( 0.8, self.isWantToReadToolDescription )
		toolbox.itemCover.highlightItem( self )
		if self.dragMark not in [DragMark.NPC_TRADE_BUY, DragMark.NPC_TRADE_REDEEM] or \
		self.itemInfo is None:return
		self.pyBinder.panelState = ( 2, 1 )

	def isWantToReadToolDescription(self):
		"""
		���ͣ��1�������ʾ��ʾ��Ϣ
		"""
		if self.isMouseHit():
			self.onDescriptionShow_()

	def onMouseLeave_( self ):
		BOItem.onMouseLeave_( self )
		if self.dragMark not in [DragMark.NPC_TRADE_BUY, DragMark.NPC_TRADE_REDEEM] or \
		self.itemInfo is None:return
		if self.pyBinder.selected:return
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

	def onDescriptionHide_( self ):
		toolbox.infoTip.hide()

	def onRClick_( self,mods ):
		BOItem.onRClick_( self, mods )
		if mods == MODIFIER_SHIFT :
			self._splitItem()
		elif mods == 0:
			if self.dragMark == DragMark.NPC_TRADE_BUY and self.index != -1 :
				amount = 1
				GUIFacade.buyFromNPC( [self.index], [amount] )
			if self.dragMark == DragMark.NPC_TRADE_REDEEM:
				if self.itemInfo == None:
					return
				GUIFacade.redeemItem( self.uid )
		return True

	def onLClick_( self, mods ):
		BigWorld.cancelCallback(self.callbackID)
		if not self.itemInfo: return
		BOItem.onLClick_( self, mods )
		if self.dragMark == DragMark.NPC_TRADE_REDEEM:
			self.selected = not self.selected
			self.pyBinder.selected = not self.selected
		return True

	def _splitItem( self ):
		if self.dragMark == DragMark.NPC_TRADE_BUY:
			def split( result, amount ) :
				if result == DialogResult.OK and self.index != -1 :
					GUIFacade.buyFromNPC( [self.index], [amount] )
			rang = ( 1, self.maxNum )
			AmountInputBox().show( split, self, rang )

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
		if itemInfo is not None :
			if self.pyBinder.dragMark == DragMark.NPC_TRADE_BUY:
				self.description = GUIFacade.getInvoiceItemDescription( index )
			elif self.pyBinder.dragMark == DragMark.NPC_TRADE_REDEEM:
				self.description = GUIFacade.getPlayerInvoiceItemDescription( itemInfo.uid )
			elif self.pyBinder.dragMark == DragMark.LoLCOPY_TRADE_WND:
				self.description = GUIFacade.getInvoiceItemDescription( index )
			elif self.pyBinder.dragMark == DragMark.TONG_SPECIAL_ITEM:
				self.description = GUIFacade.getTongSpecialDescription( index )
			self.uid = itemInfo.uid
			self.index = index
		else:
			self.uid = -1
			self.index = -1

	def updateYinpiaoItem( self, index, itemInfo ) :
		"""
		update item
		"""
		BOItem.update( self, itemInfo )
		if itemInfo is not None :
			if self.pyBinder.dragMark == DragMark.NPC_TRADE_BUY:
				self.description = GUIFacade.getMerchantItemDescription( index )
			#self.maxNum = csdefine.TRADE_MAX_GOODS_NUM
			self.uid = itemInfo.uid
			self.index = index
		else:
			self.uid = -1
			self.index = -1

	def updateItemDarkMerchantItem( self, index, itemInfo ):
		"""
		"""
		BOItem.update( self, itemInfo )
		if itemInfo is not None :
			if self.pyBinder.dragMark == DragMark.NPC_TRADE_BUY:
				self.description = GUIFacade.getDarkMerchantInvoiceDescription( index )
			self.uid = itemInfo.uid
			self.index = index
		else:
			self.uid = -1
			self.index = -1

	def updateItemChapmanItem( self, index, itemInfo ) :
		"""
		"""
		BOItem.update( self, itemInfo )
		if itemInfo is not None :
			if self.pyBinder.dragMark == DragMark.NPC_TRADE_BUY:
				self.description = GUIFacade.getInvoiceItemDescription( index )
			self.uid = itemInfo.uid
			self.index = index
		else:
			self.uid = -1
			self.index = -1

	def updatePointChapmanItem( self, index, itemInfo ) :
		"""
		"""
		BOItem.update( self, itemInfo )
		if itemInfo is not None :
			if self.pyBinder.dragMark == DragMark.NPC_TRADE_BUY:
				self.description = GUIFacade.getInvoiceItemDescription( index )
			self.uid = itemInfo.uid
			self.index = index
		else:
			self.uid = -1
			self.index = -1

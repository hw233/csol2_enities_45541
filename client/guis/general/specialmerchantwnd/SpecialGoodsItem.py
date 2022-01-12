# -*- coding: gb18030 -*-
#
# gjx 2008-1-5

from guis import *
from guis.controls.Control import Control
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.general.tradewindow.WareItem import Item
from guis.MLUIDefine import ItemQAColorMode, QAColor
import GUIFacade
import csdefine


# -------------------------------------------------------------------
# implement GoodsItem
# -------------------------------------------------------------------
class GoodsItem( Control ):
	def __init__( self, item = None, dragMark = 0, pyBinder = None ):
		Control.__init__( self, item, pyBinder )
		self.crossFocus = False
		self.dragFocus = False
		self.__uid = -1
		self.dragMark = dragMark
		self.__pyCover = None

		self.itemPanel = item.itemPanel
		self.__pyItem = Item( item.item, self.dragMark, self )
		self.__pyItemBg = PyGUI( item.itemBg )

		self.__rtName = CSRichText( item.itemName )
		self.__rtName.maxWidth = 93.0

		self.__rtMoney = CSRichText( item.itemCost )
		self.__rtMoney.align = "R"
		
		self.__panelState = ( 1, 1 )

		self.__index  = 0
		if hasattr( item, "cover" ) :
			self.__pyCover = PyGUI( item.cover )
		self.__selected = False


	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def update( self, invoice ):
		name = ""
		self.__pyItemBg.crossFocus = invoice is not None
		self.__pyItem.crossFocus = invoice is not None
		if invoice is not None:
			player = BigWorld.player()
			itemColor = 255,255,255,255
			index = invoice.index
			itemInfo = invoice.itemInfo
			baseItem = itemInfo.baseItem
			quality = itemInfo.quality
			amount = itemInfo.amount
			self.__pyItem.update( index, itemInfo )
			if self.dragMark != DragMark.LoLCOPY_TRADE_WND:			#Ӣ��������Ʒֻ������ֵӰ��
				if ( baseItem.isEquip() and baseItem.canWield( player ) ) or \
					player.level < baseItem.getReqLevel() or \
					not self.haveEnoughCredit(baseItem): # ����������ʹ�õ���Ʒ��ɺ�ɫ
					itemColor = 255,100,100,200
				if amount < 1:
					itemColor = 255,100,100,200	# �ۿյ���Ʒ���ɫ
			else:
				if not self.haveEnoughAccum( index ):
					itemColor = 255,100,100,200
			self.__pyItem.color = itemColor
			self.uid = index + 1
			self.dragFocus  = True
			name = itemInfo.name()
			priceText = self.getCost_( index )
			self.__rtName.text = PL_Font.getSource( name, fc = ( 228, 225, 192, 255 ) )
			self.__rtMoney.text = PL_Font.getSource( priceText, fc = ( 228, 225, 192, 255 ) )
			util.setGuiState( self.__pyItemBg.getGui(), ( 4, 2 ), ItemQAColorMode[baseItem.getQuality()] )
			self.index = index
		else:
			self.__rtName.text = ""
			self.__rtMoney.text = ""
			self.__pyItem.amountText = ""
			self.__pyItem.update( 0, None )
			util.setGuiState( self.__pyItemBg.getGui(), ( 4, 2 ), ItemQAColorMode[0] )

	def getCost_( self, index ) :
		pass

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
			if not value or value < creditDic[key]:
				return False
		return True
	
	def haveEnoughAccum( self, index ):
		"""
		����Ƿ����㹻������ֵ
		"""
		accumPoint = GUIFacade.getInvoiceItemAccum( index )
		return BigWorld.player().accumPoint >= accumPoint

	def __select( self ):
		self.panelState = ( 2, 1 )
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		self.panelState = ( 1, 1 )
		if self.__pyCover:
			self.__pyCover.visible = False

	def getObjectItem( self ):
		return self.__pyItem

	# -------------------------------------------------
	def _getIndex( self ):
		return self.__index

	def _setIndex( self, index ):
		self.__index = index

	def _getUid( self ):
		return self.__uid

	def _setUid( self, uid ):

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
	index = property( _getIndex, _setIndex )
	uid = property( _getUid, _setUid )
	panelState = property( _getPanelState, _setPanelState )
	itemInfo = property( _getItemInfo )
	selected = property( _getSelected, _setSelected )
	icon = property( _getIcon )


# -------------------------------------------------------------------
# implement SpecialGoodsItem
# -------------------------------------------------------------------
class SpecialGoodsItem( GoodsItem ):
	"""
	�ز�����Ʒ��
	"""
	def __init__( self, item = None, dragMark = 0, pyBinder = None ):
		GoodsItem.__init__( self, item, dragMark, pyBinder )


	# ---------------------------------------------------------------
	# protected
	# ---------------------------------------------------------------
	def getCost_( self, index ):
		"""
		���صķ���
		"""
		reqYinpiao = 0
		if self.dragMark == DragMark.NPC_TRADE_BUY:
			reqYinpiao = GUIFacade.getInvoiceItemYinpiao( index )
		text = str( reqYinpiao ) + PL_Image.getSource( "guis/general/specialMerchantWnd/silver.gui" )
		return text


	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def update( self, invoice ):
		"""
		���صķ���
		"""
		GoodsItem.update( self, invoice )
		if invoice:
			self.getObjectItem().updateYinpiaoItem( invoice.index, invoice.itemInfo )

# -------------------------------------------------------------------
# implement DarkMerchantItem
# -------------------------------------------------------------------
class DarkMerchantItem( GoodsItem ):
	"""
	����������Ʒ��
	"""
	def __init__( self, item = None, dragMark = 0, pyBinder = None ):
		GoodsItem.__init__( self, item, dragMark, pyBinder )

	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def getCost_( self, index ):
		"""
		���صķ���
		"""
		money = GUIFacade.getDarkMerchantInvoicePrice( index )
		return utils.currencyToViewText( money )

	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def update( self, invoice ):
		"""
		���صķ���
		"""
		GoodsItem.update( self, invoice )
		if invoice:
			self.getObjectItem().updateItemDarkMerchantItem( invoice.index, invoice.itemInfo )

class DarkGoodsItem( GoodsItem ):
	def __init__( self, item = None, dragMark = 0, pyBinder = None ):
		GoodsItem.__init__( self, item, dragMark, pyBinder )
		self.__pyRtGoldCost = CSRichText( item.goldCost )
		self.__pyRtGoldCost.align = "R"
		self.__pyRtGoldCost.maxWidth = 25.0
		
	# ---------------------------------------------------------------
	# protected
	# ---------------------------------------------------------------
	def getCost_( self, index ):
		money = GUIFacade.getInvoiceItemPrice( index )
		gold = money / 10000
		silver = money % 10000 / 100
		coin = money % 100
		costStr = ""
		if gold:
			costStr = "%d%s"%( gold, PL_Image.getSource( "guis_v2/controls/goldicon.gui" ) )
			#self.__pyRtGoldCost.text = PL_Font.getSource( goldText, fc = ( 228, 225, 192, 255 ) )
		if silver:
			costStr += "%d%s"%( silver, PL_Image.getSource( "guis_v2/controls/silvericon.gui" ) )
		if coin:
			costStr += "%d%s"%( coin, PL_Image.getSource( "guis_v2/controls/coinicon.gui" ) )		
		return costStr
		
	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def update( self, invoice ):
		"""
		���صķ���
		"""
		GoodsItem.update( self, invoice )

class LolCopyItem( GoodsItem ):
	"""
	Ӣ�۸���������Ʒ
	"""
	def __init__( self, item = None, dragMark = 0, pyBinder = None ):
		GoodsItem.__init__( self, item, dragMark, pyBinder )
		self.dragFocus = False
		self.__pyRtGoldCost = CSRichText( item.itemCost )
		self.__pyRtGoldCost.align = "R"
		self.__pyRtGoldCost.maxWidth = 25.0

	# ---------------------------------------------------------------
	# protected
	# ---------------------------------------------------------------
	def getCost_( self, index ):
		"""
		���صķ���
		"""
		reqSoulCoin = 0
		costStr = ""
		if self.dragMark == DragMark.LoLCOPY_TRADE_WND:
			prices = GUIFacade.getInvoicePriceDescription( index )
			for  price in prices:
				costStr += price
		return costStr
		
	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def update( self, invoice ):
		"""
		���صķ���
		"""
		GoodsItem.update( self, invoice )
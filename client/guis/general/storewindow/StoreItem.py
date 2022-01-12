# -*- coding: gb18030 -*-
#
# $Id: StoreItem.py,v 1.14 2008-08-08 03:17:08 fangpengjun Exp $
#
# rewrited by ganjinxing at 2009-12-17


from guis import *
from guis.common.PyGUI import PyGUI
from guis.tooluis.inputbox.InputBox import AmountInputBox
from guis.tooluis.richtext_plugins.PL_Align import PL_Align
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from CompareDspItem import CompareDspItem
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
from guis.MLUIDefine import ItemQAColorMode
import ItemTypeEnum
import csdefine
import csconst

class StoreItem( PyGUI ) :

	def __init__( self, item, index, pyBinder = None ) :
		PyGUI.__init__( self, item )

		self.__pyItem = Item( index, item.item, pyBinder )
		self.__pyLockIcon = item.lockIcon
		self.__pyLockIcon.visible = False

	def update( self, itemInfo ) :
		self.__pyItem.update( itemInfo )
		quality = 1
		isBinded = False
		if itemInfo is not None :
			quality = itemInfo.quality
			isBinded = itemInfo.baseItem.isBinded()
		self.__pyLockIcon.visible = isBinded
		util.setGuiState( self.gui, ( 4, 2 ), ItemQAColorMode[quality] )


	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	def _getItemInfo( self ) :
		return self.__pyItem.itemInfo

	itemInfo = property( _getItemInfo )


class Item( CompareDspItem ) :

	def __init__( self, index, item = None, pyBinder = None ) :
		CompareDspItem.__init__( self, item, pyBinder )
		self.crossFocus = True
		self.dropFocus = True

		self.__index = index
		self.dragMark = DragMark.BANK_WND_ITEM
		self.__initialize( item )

	def __initialize( self, item ) :
		if item is None : return
		self.__dropEvents = {}
		self.__dropEvents[DragMark.KITBAG_WND] = DropHandlers.fromKitbagWindow
		self.__dropEvents[DragMark.BANK_WND_ITEM] = DropHandlers.fromBankWindow


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __splitItem( self ) :
		"""
		if an item is more the one, split it into two
		"""
		if self.itemInfo is None : return
		if self.itemInfo.amount <= 1 : return
		def split( result, amount ) :
			if result == DialogResult.OK :
				BigWorld.player().bank_splitItem( self.itemOrder, amount )
		rang = ( 1, self.amount - 1 )
		AmountInputBox().show( split, self, rang )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onRClick_( self, mods ) :
		"""
		右键取回物品
		"""
		BigWorld.player().bank_fetchItem2Kitbags( self.bagIndex, self.itemOrder )

	def onDragStart_( self, pyDragged ) :
		"""
		拖起一个物品
		"""
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		CompareDspItem.onDragStart_( self, pyDragged )
		return True

	def onDragStop_( self, pyDragged ) :
		"""
		放开一个拖放物品
		"""
		CompareDspItem.onDragStop_( self, pyDragged )
		if pyDragged is None: return
		if not ruisMgr.isMouseHitScreen() : return False
		if pyDragged.itemInfo is None: return
		name = pyDragged.itemInfo.name()
		def query( rs_id):
			if rs_id == RS_OK:
				BigWorld.player().bank_destroyItem( self.bagIndex, self.itemOrder )
		# "确定丢弃%s？"
		showMessage( mbmsgs[0x0821] % name,"", MB_OK_CANCEL, query )
		return True

	def onDrop_( self, pyTarget, pyDropped ) :
		"""
		一个拖放物品被放下
		"""
		CompareDspItem.onDrop_( self, pyTarget, pyDropped )
		dragMark = rds.ruisMgr.dragObj.dragMark
		if not self.__dropEvents.has_key( dragMark ) : return
		self.__dropEvents[dragMark]( pyTarget, pyDropped )
		return True


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItemOrder( self ) :
		return self.bagIndex * csdefine.KB_MAX_SPACE + self.__index

	def _getBagIndex( self ) :
		return self.pyBinder.currBagIndex

	def _getDescription( self ) :
		itemInfo = self.itemInfo
		if itemInfo is None : return []
		dsp = CompareDspItem._getDescription( self )[:]
		if  itemInfo.baseItem.canSell() and \
		itemInfo.baseItem.getType() != ItemTypeEnum.ITEM_EQUIPMAKE_SCROLL :
			money = max( 1, int( itemInfo.price * csconst.INVBUYPERCENT ) )
			perCostStr = labelGather.getText( "StoreWndRole:Item", "price" ) + utils.currencyToViewText( money )
			perCostStr = PL_Align.getSource( lineFlat = "M" ) + \
			PL_NewLine.getSource( 1 ) + perCostStr + PL_Align.getSource( "L" )
			dsp.append( [perCostStr] )
			if itemInfo.amount > 1 :
				totalCostStr = labelGather.getText( "StoreWndRole:Item", "totalCost" ) + utils.currencyToViewText( money * itemInfo.amount )
				totalCostStr = PL_Align.getSource( lineFlat = "M" ) +  totalCostStr + PL_Align.getSource( "L" )
				dsp.append( [totalCostStr] )
		return dsp

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	itemOrder = property( _getItemOrder )											# 获取物品位置索引
	bagIndex = property( _getBagIndex ) 											# 获取物品所在包位
	description = property( _getDescription, CompareDspItem._setDescription )


#---------------------------------------------------------------------
# drop handlers
#---------------------------------------------------------------------
class DropHandlers :
	@staticmethod
	def fromKitbagWindow( pyTarget, pyDropped ) :
		kitBag = pyDropped.kitbagID
		srcIndex = pyDropped.gbIndex
		dstBank = pyTarget.bagIndex
		dstIndex = pyTarget.itemOrder
		BigWorld.player().bank_storeItem2Order( kitBag, srcIndex, dstBank, dstIndex )

	@staticmethod
	def fromBankWindow( pyTarget, pyDropped ):
		srcBank = pyDropped.bagIndex
		dstBank = pyTarget.bagIndex
		srcIndex = pyDropped.itemOrder
		dstIndex = pyTarget.itemOrder
		if srcIndex == dstIndex:
			return
		BigWorld.player().bank_moveItem( srcBank, srcIndex, dstBank, dstIndex )

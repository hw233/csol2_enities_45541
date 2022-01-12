# -*- coding: gb18030 -*-

from guis import *
from guis.general.vendwindow.buywindow.ItemsPanel import BaseItemsPanel
from config.client.msgboxtexts import Datas as mbmsgs
from ItemsFactory import ObjectItem
import csdefine
import csstatus


class ItemsPanel( BaseItemsPanel ) :

	def __init__( self, panel, pyBinder = None ) :
		BaseItemsPanel.__init__( self, panel, pyBinder )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initItem_( self, pyViewItem ) :
		"""
		��ʼ����ӵļ����б���
		"""
		BaseItemsPanel.initItem_( self, pyViewItem )
		pyBuyItem = pyViewItem.pyBuyItem
		pyBuyItem.pyItem.dragMark = DragMark.TISHOU_BUY_PANEL

	def registerTriggers_( self ):
		self.triggers_["EVT_ON_TISHOU_ITEM_SELLED"] = self.onRemoveItem_
		self.triggers_["EVT_ON_TISHOU_RECEIVE_ITEMS"] = self.__onReceiveItem
		self.triggers_["EVT_ON_UPDATE_TISHOU_SELLED_ITEM"] = self.__onUpdateItemPrice
		BaseItemsPanel.registerTriggers_( self )

	def onItemRClick_( self, pyViewItem ) :
		"""
		�һ���ʾ���������Ʒ
		"""
		itemInfo = pyViewItem.pageItem
		if itemInfo is None : return
		self.pyPagesPanel_.selIndex = pyViewItem.itemIndex
		def query( rs_id ) :
			if rs_id == RS_OK :
				player = BigWorld.player()
				checkSpaceRes = player.checkItemsPlaceIntoNK_( [ itemInfo.baseItem ] )
				if checkSpaceRes == csdefine.KITBAG_NO_MORE_SPACE :
					player.statusMessage( csstatus.CIB_MSG_BAG_HAS_FULL )
					return
				tishouNPC = self.pyBinder.trapEntity
				if tishouNPC is not None :
					if not tishouNPC.tsState :
						# "��һ�û��ʼ��̯"
						self.showMsg( 0x0ae1 )
					else :
						tishouNPC.cell.buyTSItem( itemInfo.uid, itemInfo.id, itemInfo.amount, itemInfo.rolePrice )
		moneyStr = utils.currencyToViewText( itemInfo.rolePrice, False )
		# "��Ҫ����%s����%s��%sô?"
		msg = mbmsgs[0x0ae2] % ( moneyStr, itemInfo.amount, itemInfo.name() )
		self.showMsg( msg, MB_OK_CANCEL, query )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onReceiveItem( self, baseItem, price, ownerDBID ) :
		"""
		���յ�����Ʒ
		"""
		tishouNPC = self.pyBinder.trapEntity
		if tishouNPC is None or tishouNPC.ownerDBID != ownerDBID : return	# NPC�����ڻ��߲��Ǹ�NPC�ļ�����Ʒ
		for item in self.pyPagesPanel_.items :							# �����ظ���Ʒ
			if item.uid == baseItem.uid :
				return
		itemInfo = ObjectItem( baseItem )
		itemInfo.rolePrice = price
		self.pyPagesPanel_.addItem( itemInfo )
		self.pyItemsAmount_.text = str( self.pyPagesPanel_.itemCount )

	def __onUpdateItemPrice( self, uid, price ) :
		for index, itemInfo in enumerate( self.pyPagesPanel_.items ) :
			if itemInfo.baseItem.uid == uid:
				itemInfo.rolePrice = price
				self.pyPagesPanel_.updateItem( index, itemInfo )
				break

	def __queryTSGoodsInfo( self ) :
		"""
		������������ѯ������Ʒ������
		"""
		self.reset()
		def queryInfo() :
			tishouNPC = self.pyBinder.trapEntity
			if tishouNPC is not None :
				tishouNPC.cell.queryTSItems()
		if self.visible :
			queryInfo()
		else :
			BigWorld.callback( 0.3, queryInfo )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onParentShow( self ) :
		self.__queryTSGoodsInfo()

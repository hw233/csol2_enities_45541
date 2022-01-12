# -*- coding: gb18030 -*-
#
# $Id: GooodsPanel.py, fangpengjun Exp $

"""
implement goods panel class

"""
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.TabCtrl import TabPanel
from guis.controls.ODComboBox import ODComboBox
from guis.controls.TextBox import TextBox
from guis.controls.StaticText import StaticText
from guis.controls.StaticLabel import StaticLabel
from StorageItem import StorageItem
from ItemsFactory import ObjectItem
from LabelGather import labelGather
from config.client.msgboxtexts import Datas as mbmsgs
import GUIFacade
import csdefine
import csstatus

STORAGEBAG_MAX_ORDER = 80

class GoodsPanel( TabPanel ): #��Ʒ������

	_sort_types = { csdefine.BANK_SORT_BY_ID: labelGather.getText( "StorageWindow:goodsPanel", "miType" ),
			csdefine.BANK_SORT_BY_QUALITY: labelGather.getText( "StorageWindow:goodsPanel", "miQuality" ),
			csdefine.BANK_SORT_BY_PRICE: labelGather.getText( "StorageWindow:goodsPanel", "miPrice" ),
			csdefine.BANK_SORT_BY_LEVEL: labelGather.getText( "StorageWindow:goodsPanel", "miLevel" )
			}

	def __init__( self, goodsPanel, pyBinder = None ):
		TabPanel.__init__( self, goodsPanel, pyBinder )
		self.__pySortCB = ODComboBox( goodsPanel.sortComBox )
		self.__pySortCB.autoSelect = False
		self.__pySortCB.ownerDraw = True
		self.__pySortCB.pyBox_.foreColor = 236, 218, 157
		self.__pySortCB.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pySortCB.onDrawItem.bind( self.onDrawItem_ )
		for key, keyStr in self._sort_types.iteritems():
			self.__pySortCB.addItem( keyStr )
		self.__pySortCB.onItemLClick.bind( self.__onSortByType )

		self.__pyCustomBox = TextBox( goodsPanel.customBox.box, self )
		self.__pyCustomBox.inputMode = InputMode.COMMON
		self.__pyCustomBox.maxLength = 8
		self.__pyCustomBox.onKeyDown.bind( self.__onChangeName )
		self.__pyCustomBox.text = ""

		self.__triggers = {}
		self.__registerTriggers()
		self.__goods ={} #�ֿ�Ĵ洢�ռ�,keyΪorder��valueΪitemInfo����ѡ���Ӧ�İ���ʱ���Ӵ�ȡ���ݸ���ѡ��İ���
		self.__currentBagID = 0 #��ǰ�ֿ������
		self.sortItemList = []		# ��ʱ�洢����ʱ����Ʒ

		self.__pyStNum = StaticText( goodsPanel.stNum )
		self.__pyStNum.text = ""

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setLabel( goodsPanel.stCustom, "StorageWindow:goodsPanel", "rbCustom" )		# �Զ���
		labelGather.setLabel( goodsPanel.stDownLt, "StorageWindow:goodsPanel", "rbDownLt" )		# ����ʽ

		self.__pyBankItems = {}
		for name, item in goodsPanel.children:
			if name.startswith( "item_" ):
				index = int( name.split( "_" )[1] )
				pyBankItem = StorageItem( item, index )
				self.__pyBankItems[index] = pyBankItem

	def onInitialized_( self, pyViewItem ):
		pyLabel = StaticLabel()
		pyLabel.crossFocus = True
		pyLabel.foreColor = 236, 218, 157
		pyLabel.h_anchor = "CENTER"
		pyViewItem.addPyChild( pyLabel )
		pyViewItem.pyLabel = pyLabel
	
	def onDrawItem_( self, pyViewItem ):
		pyPanel = pyViewItem.pyPanel
		if pyViewItem.selected :
			pyViewItem.pyLabel.foreColor = pyPanel.itemSelectedForeColor			# ѡ��״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemSelectedBackColor				# ѡ��״̬�µı���ɫ
		elif pyViewItem.highlight :
			pyViewItem.pyLabel.foreColor = pyPanel.itemHighlightForeColor		# ����״̬�µ�ǰ��ɫ
			pyViewItem.color = pyPanel.itemHighlightBackColor				# ����״̬�µı���ɫ
		else :
			pyViewItem.pyLabel.foreColor = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor
		pyLabel = pyViewItem.pyLabel
		pyLabel.width = pyViewItem.width
		pyLabel.foreColor = 236, 218, 157
		pyLabel.left = 1.0
		pyLabel.top = 1.0
		pyLabel.text = pyViewItem.listItem

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		register all events
		"""
		self.__triggers["EVT_ON_TOGGLE_TONG_STORAGE_ITEM"] = self.__onAddItem #������Ʒ��Ϣ
		self.__triggers["EVT_ON_TOGGLE_TONG_STORAGE_ITEM_UPDATE"] = self.__onStorageItemUpdate #���²ֿ���Ʒ��Ϣ
		self.__triggers["EVT_ON_TOGGLE_TONG_STORAGE_MOVE_ITEM"] = self.__onStorageItemMove #�ֿ���Ʒ֮�佻��
		self.__triggers["EVT_ON_TOGGLE_TONG_STORAGE_DEL_ITEM"] = self.__onStorageItemDel #�Ƴ�ĳ����Ʒ
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )
	# -----------------------------------------------------------------
	def __onAddItem( self, bankIndex, gbOrder, itemInfo ):
		if itemInfo is not None:
			self.__onStorageItemUpdate( bankIndex, gbOrder, itemInfo )

	def __onStorageItemUpdate( self, bankIndex, gbOrder, itemInfo ):
		self.__goods[gbOrder] = itemInfo
		if bankIndex == self.__currentBagID: #���µ�ǰѡ��ֿ�
			index = gbOrder
			if bankIndex != 0:
				index = gbOrder % ( bankIndex * csdefine.KB_MAX_SPACE )
			self.__updateItem( index, itemInfo )
			self.__setItemsNum( len( self.__getItems( bankIndex ) ) )

	def __onStorageItemMove( self, srcOrder, dstOrder ):
		srcItem = self.__pyBankItems[srcOrder % csdefine.KB_MAX_SPACE]
		dstItem = self.__pyBankItems[dstOrder % csdefine.KB_MAX_SPACE]
		srcInfo = srcItem.itemInfo
		dstInfo = dstItem.itemInfo
		srcInfo.baseItem.setOrder( dstOrder )
		if dstInfo:
			dstInfo.baseItem.setOrder( srcOrder )
		srcItem.update( dstInfo )
		dstItem.update( srcInfo )
		srcItem.bagIndex = self.__currentBagID	# ����λ����Ϣ
		dstItem.bagIndex = self.__currentBagID
		srcItem.gbIndex = srcOrder
		dstItem.gbIndex = dstOrder
		if self.__goods.has_key( srcOrder ):
			if self.__goods.has_key( dstOrder ):
				temp = self.__goods[ srcOrder ]
				self.__goods[ srcOrder ] = self.__goods[ dstOrder ]
				self.__goods[ dstOrder ] = temp
			else:
				self.__goods[ dstOrder ] = self.__goods[ srcOrder ]
				del self.__goods[ srcOrder ]
		else:
			if self.__goods.has_key( dstOrder ):
				self.__goods[ srcOrder ] = self.__goods[ dstOrder ]
				del self.__goods[ dstOrder ]
		if self.sortItemList:		# ��������Զ�������Ʒ�У����Ҵ˹��̻�û����������������Ʒ
			self._moveItemForSort( self.__currentBagID )

	def _moveItemForSort( self, bagOrder ):
		"""
		��Ʒ�����У�������Ʒ
		"""
		player = BigWorld.player()
		if not self.sortItemList:
			return
		item = self.sortItemList.pop( 0 )
		if item.kitbag != self.__currentBagID:
			self.sortItemList = []
			return
		srcOrder = item.baseItem.getOrder()
		dstOrder = bagOrder * csdefine.KB_MAX_SPACE + len( self.sortItemList )
		while srcOrder == dstOrder and self.sortItemList:
			item = self.sortItemList.pop( 0 )
			srcOrder = item.baseItem.getOrder()
			dstOrder = bagOrder * csdefine.KB_MAX_SPACE + len( self.sortItemList )
		player.tong_moveStorageItem( srcOrder, dstOrder )

	def __onStorageItemDel( self, order ):#�Ƴ���Ʒ
		bankOrder = order/csdefine.KB_MAX_SPACE
		itemOrder = order%csdefine.KB_MAX_SPACE
		item = self.__goods.pop( order ) #����Ʒ�б���ɾ��
		if self.__currentBagID == bankOrder: #����Ƴ�����Ʒ��ѡ��Ĳֿ���
			self.__updateItem( itemOrder, None )
			self.__setItemsNum( len( self.__getItems( bankOrder ) ) )

	def __updateItem( self, itemOrder, itemInfo ):
		pyItem = self.__pyBankItems.get( itemOrder, None )
		if pyItem is None:return
		pyItem.update( itemInfo )

	def __onChangeName( self, key, mods ): #���س��ͱ����Զ�������
		if key == KEY_RETURN and mods == 0:
			text = self.__pyCustomBox.text
			if text == "":
				# "�������������Ч�����������롣"
				self.__showMsg( mbmsgs[0x0801] )
			elif self.__pyCustomBox.length > 8:
				self.__showMsg( mbmsgs[0x0804] )
			elif not rds.wordsProfanity.isPureString( text ):
				# "���Ʋ��Ϸ���"
				self.__showMsg( mbmsgs[0x0802] )
			elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
				# "����������н��ôʻ㣡"
				self.__showMsg( mbmsgs[0x0803] )
			else :
				if self.__currentBagID > -1 :
					self.__pyCustomBox.tabStop = False
					BigWorld.player().tong_renameStorageBag( self.__currentBagID, text )
			return True
		return False

	def __showMsg( self, msg ) :
		def query( res ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is None :
			self.__pyMsgBox = showMessage( msg, "", MB_OK, query, self )
		else :
			self.__pyMsgBox.show( msg, "", query, self )

	def __onSortByType( self, sortType ):
		player = BigWorld.player()
		self.__bankitemSort( self.__currentBagID, sortType )

	def __bankitemSort( self, kitOrder, sortType ): #����
		self.__pySortCB.pyBox_.text = self.__pySortCB.items[sortType]
		self.sortItemList = [ item[ 1 ] for item in self.__getItems( kitOrder ) ]
		if not self.sortItemList:
			return
		handlerDict = { csdefine.BANK_SORT_BY_ID : self.sortByID,
					csdefine.BANK_SORT_BY_QUALITY : self.sortByQuality,
					csdefine.BANK_SORT_BY_PRICE : self.sortByPrice,
					csdefine.BANK_SORT_BY_LEVEL : self.sortByLevel,
					}
		handlerDict[ sortType ]( self.sortItemList )
		self.sortItemList.reverse()		# �ź�����ȴӺ��潻��λ��
		self._moveItemForSort( kitOrder )

	def sortByID( self, itemList ):
		"""
		����������
		"""
		itemList.sort( key = lambda n : n.id )

	def sortByQuality( self, itemList ):
		"""
		��Ʒ�ʴӸߵ�������ͬƷ�ʰ��ȼ��Ӹߵ�������ͬƷ�ʡ��ȼ�����id����
		"""
		def func( item1, item2 ):
			if item1.quality == item2.quality and item1.level == item2.level:
				return cmp( item2.id, item1.id )	# item2��ǰ��ԭ���ǣ���id������ӵ͵����ţ���Ʒ�ʡ��������෴��
			elif item1.quality == item2.quality:
				return cmp( item2.level, item1.level )
			else:
				return cmp( item2.quality, item1.quality )
		itemList.sort( cmp = func )

	def sortByPrice( self, itemList ):
		"""
		���۸�Ӹߵ�������ͬ�۸񰴵ȼ��Ӹߵ�������ͬ�۸񡢵ȼ�����id����
		"""
		def func( item1, item2 ):
			if item1.price == item2.price and item1.level == item2.level:
				return cmp( item2.id, item1.id )	# item2��ǰ��ԭ���ǣ���id������ӵ͵����ţ���Ʒ�ʡ��������෴��
			elif item1.price == item2.price:
				return cmp( item2.level, item1.level )
			else:
				return cmp( item2.price, item1.price )
		itemList.sort( cmp = func )

	def sortByLevel( self, itemList ):
		"""
		���ȼ��Ӹߵ�������ͬ�ȼ���Ʒ�ʴӸߵ�������ͬ�ȼ���Ʒ�ʣ���id����
		"""
		def func( item1, item2 ):
			if item1.level == item2.level and item1.quality == item2.quality:
				return cmp( item2.id, item1.id )	# item2��ǰ��ԭ���ǣ���id������ӵ͵����ţ���Ʒ�ʡ��������෴��
			elif item1.level == item2.level:
				return cmp( item2.quality, item1.quality )
			else:
				return cmp( item2.level, item1.level )
		itemList.sort( cmp = func )

	def __getItems( self, bankOrder ):
		"""
		��ñ�����ΪbankOrder�����е���Ʒ��Ϣ�б�
		rtype : [ ( order, item ), ... ]
		"""
		items = []
		for i in xrange( bankOrder * csdefine.KB_MAX_SPACE, ( bankOrder + 1 ) * csdefine.KB_MAX_SPACE ):
			if self.__goods.has_key( i ):
				items.append( ( i, self.__goods[ i ] ) )
		return items

	def __setItemsNum( self, amount ):
		self.__pyStNum.text = "%d/%d"%( amount, STORAGEBAG_MAX_ORDER )

	def __clearItems( self ):
		for pyItem in self.__pyBankItems.itervalues():
			pyItem.update( None )

	def _getBagIndex( self ):
		return self.__currentBagID

	def _setBagIndex( self, bagIndex ):
		self.__currentBagID = bagIndex

	bagIndex = property( _getBagIndex, _setBagIndex )

	#----------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def setItems( self, bagIndex ):
		self.__clearItems()
		self.__currentBagID = bagIndex
		player = BigWorld.player()
		tongGrade = player.tong_grade
		self.__pySortCB.enable = tongGrade == csdefine.TONG_DUTY_CHIEF
		self.__pySortCB.selIndex = 0
		self.__pyCustomBox.enable = tongGrade == csdefine.TONG_DUTY_CHIEF #ֻ�а������ܶ���Ʒ����ͶӲֿ����
		for i in xrange( 0, STORAGEBAG_MAX_ORDER, 1 ):
			pyItem = self.__pyBankItems[i]
			pyItem.index = i
			if i >= STORAGEBAG_MAX_ORDER:
				pyItem.index = -1
				util.setGuiState( pyItem.getGui(), ( 2, 1 ), ( 2, 1 ) )
				continue
			pyItem.bagIndex = bagIndex
			pyItem.gbIndex = bagIndex * csdefine.KB_MAX_SPACE + i
		items = self.__getItems( bagIndex )
		self.__setItemsNum( len( items ) )
		for item in items:
			order = item[ 0 ] % csdefine.KB_MAX_SPACE
			pyItem = self.__pyBankItems[order]
			if pyItem is None:return
			pyItem.update( item[ 1 ] )
			pyItem.bagIndex = bagIndex	# ����λ����Ϣ
			pyItem.gbIndex = pyItem.index + csdefine.KB_MAX_SPACE * bagIndex
		for bagPopedom in player.storageBagPopedom:
			if bagPopedom["bagID"] == bagIndex:
				bagName = bagPopedom["bagName"]
				if bagName == "":
					self.__pyCustomBox.text = self.pyBinder._nums_map[bagIndex]
				else:
					self.__pyCustomBox.text = bagName

	def freezeItems( self ):
		for pyItem in self.__pyBankItems.itervalues():
			pyItem.foucs = False

	def onLeaveWorld( self ) :
		for pyItem in self.__pyBankItems.itervalues():
			pyItem.update( None )
		self.__goods = {}
		self.sortItemList = []
		self.__currentBagID = 0
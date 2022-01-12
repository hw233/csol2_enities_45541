# -*- coding: gb18030 -*-
#
# $Id: ItemsPanel.py,v 1.4 2008-07-07 11:10:00 wangshufeng Exp $
#
# rewrited by ganjinxing at 2009-12-17


from guis import *
from bwdebug import *
from guis.controls.TextBox import TextBox
from guis.controls.StaticText import StaticText
from guis.controls.StaticLabel import StaticLabel
from guis.controls.ODComboBox import ODComboBox
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.SelectableButton import SelectableButton
from guis.common.GUIBaseObject import GUIBaseObject
from StoreItem import StoreItem
from cscollections import MapList
from ItemsFactory import ObjectItem
from LabelGather import labelGather
from config.client.msgboxtexts import Datas as mbmsgs
import string
import csdefine
import csstatus

class ItemsPanel( GUIBaseObject ):

	# Ĭ�ϰ�������
	_DEF_PACKAGE_NAME = { 0:"btn_0",1:"btn_1",2:"btn_2",3:"btn_3",4:"btn_4",5:"btn_5",6:"btn_6"}

	def __init__( self, panel, pyBinder = None ):
		GUIBaseObject.__init__( self, panel )

		self.__pyItems = {}								# ������Ʒ��
		self.__storage = {}								# ����ֿ���Ʒ{ bagIndex: { itemOrder: itemInfo, ...}, ...}
		self.__pyMsgBox = None							# ������Ϣ���ڣ����ڿ��������ʾһ������
		self.__sortingItemDict = {}
		self.__sortHandlerMap = {}
		self.__operateCounter = 0						# ��¼����Ҫ�ȴ����η����������ټ����´β���

		self.__initialize( panel )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, panel ) :
		self.__pyBagName = TextBox( panel.customBox.box, self )
		self.__pyBagName.maxLength = 10
		self.__pyBagName.onKeyDown.bind( self.__ChangeName )
		self.__pyBagName.text = ""

		self.__pyItemsAmount = StaticText( panel.stItemNum )
		self.__setBagAmount( 0 )
		self.__initItems( panel )
		self.__initButtons( panel )
		self.__initSortBox( panel )

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setLabel( panel.st_taxisText, "StoreWndRole:Panel", "st_taxisText" )
		labelGather.setLabel( panel.st_customText, "StoreWndRole:Panel", "st_customText" )

	def __initItems( self, panel ):
		"""
		��ʼ����Ʒ��
		"""
		for name, item in panel.panel_0.children:
			index = int( name.split( "_" )[1] )
			pyItem = StoreItem( item, index, self )
			self.__pyItems[index] = pyItem

	def __initButtons( self, panel ) :
		"""
		��ʼ���ֿⰴť
		"""
		self.__btnsGroup = SelectorGroup()
		self.__btnsGroup.onSelectChanged.bind( self.__onBagSelected )
		for name, btn in panel.children :
			if "btn_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyBagBtn = SelectableButton( btn )
			pyBagBtn.setStatesMapping( UIState.MODE_R4C1 )
			pyBagBtn.disableForeColor = 237,230,155, 100
			pyBagBtn.enable = False
			pyBagBtn.bagIndex = index
			labelGather.setPyBgLabel( pyBagBtn, "StoreWndRole:Panel", self._DEF_PACKAGE_NAME[index] )
			self.__btnsGroup.addSelector( pyBagBtn )
		self.__btnsGroup.pyCurrSelector = self.__getPyBagBtn( 0 )		# Ĭ��ѡ�е�һ���ֿ�λ

	def __initSortBox( self, panel ) :
		"""
		��ʼ�����򴰿�
		"""
		tempMap = (
					( 0, "sbtext_type", self.__sortByType ),
					( 1, "sbtext_quality", self.__sortByQuality ),
					( 2, "sbtext_price", self.__sortByPrice ),
					( 3, "sbtext_level", self.__sortByLevel ),
					)
		self.__sortBox = ODComboBox( panel.sortCB )
		self.__sortBox.autoSelect = False
		self.__sortBox.ownerDraw = True
		self.__sortBox.pyBox_.foreColor = 236, 218, 157
		self.__sortBox.onViewItemInitialized.bind( self.onInitialized_ )
		self.__sortBox.onDrawItem.bind( self.onDrawItem_ )
		self.__sortBox.onItemLClick.bind( self.__onSort )
		labelGather.setPyBgLabel( self.__sortBox.pyBox_, "StoreWndRole:Panel", "sbtext_option" )
		for index, sortText, handler in tempMap :
			self.__sortBox.addItem( labelGather.getText( "StoreWndRole:Panel", sortText ) )
			self.__sortHandlerMap[index] = handler

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

	# -------------------------------------------------
	# function
	# -------------------------------------------------
	def __onBagSelected( self, pyBagBtn ) :
		"""
		ѡȡĳ������
		"""
		bagIndex = pyBagBtn.bagIndex
		self.__pyBagName.text = pyBagBtn.text
		self.__setBagAmount( bagIndex )
		bag = self.__storage.get( bagIndex, {} )
		bagAddress = bagIndex * csdefine.KB_MAX_SPACE
		for index, pyItem in self.__pyItems.iteritems() :
			itemInfo = bag.get( bagAddress + index, None )
			pyItem.update( itemInfo )

	def __ChangeName( self, key, mods ) :
		"""
		���س��ͱ����Զ�������
		"""
		if key == KEY_RETURN and mods == 0:
			text = self.__pyBagName.text.strip()
			if text == "":
				# "�������������Ч�����������롣"
				self.__showMsg( mbmsgs[0x0801] )
			elif self.__pyBagName.length > 8:
				self.__showMsg( mbmsgs[0x0804] )
			elif not rds.wordsProfanity.isPureString( text ):
				# "���Ʋ��Ϸ���"
				self.__showMsg( mbmsgs[0x0802] )
			elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
				# "����������н��ôʻ㣡"
				self.__showMsg( mbmsgs[0x0803] )
			else :
				currBagIndex = self.currBagIndex
				if currBagIndex > -1 :
					self.__pyBagName.tabStop = False
					BigWorld.player().base.bank_changeName( currBagIndex, text )
			return True
		return False

	def __getPyBagBtn( self, bagIndex ) :
		"""
		��ȡ�ͱ�����Ӧ�İ�ť
		"""
		pyBagBtns = self.__btnsGroup.pySelectors
		for pyBagBtn in pyBagBtns :
			if pyBagBtn.bagIndex == bagIndex :
				return pyBagBtn
		return None

	def __getBagAmount( self, bagIndex ) :
		"""
		��ȡĳ���ֿ��������Ʒ����
		"""
		return len( self.__storage.get( bagIndex, {} ) )

	def __setBagAmount( self, bagIndex ) :
		"""
		��ʾĳ����������Ʒ����
		"""
		amount = self.__getBagAmount( bagIndex )
		labelGather.setPyLabel( self.__pyItemsAmount, "StoreWndRole:Panel", "stItemNum", amount )

	def __showMsg( self, msg ) :
		def query( res ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is None :
			self.__pyMsgBox = showMessage( msg, "", MB_OK, query, self )
		else :
			self.__pyMsgBox.show( msg, "", query, self )

	# -------------------------------------------------
	# sort about
	# -------------------------------------------------
	def __moveItemForSort( self, bagIndex ) :
		"""
		��Ʒ�����У�������Ʒ
		"""
		self.__operateCounter -= 1
		if self.__operateCounter > 0 : return									# �ж��Ƿ������Ƿ��Ѵ����겢������

		if not self.__combineSortedItems( bagIndex ) :							# ���������Ʒ��Ҫ���ӣ��򲻽����ƶ�����
			self.__moveSortedItems( bagIndex )									# ����Ʒ��������ϣ��������Ʒ�ƶ�

	def __combineSortedItems( self, bagIndex ) :
		"""
		�����������Ʒ
		@return		: bool��True��ʾ������һ����Ʒ��False��ʾ��Ʒ�������
		"""
		itemsCombined = self.__sortingItemDict.get( bagIndex, ( None, None ) )[1]
		if not itemsCombined : return False
		for header, stackGroup in itemsCombined.items() :
			if stackGroup :														# �б���
				stackItem = stackGroup.pop( 0 )									# ȡ��һ�����е���
				srcItemOrder = stackItem.baseItem.order
				dstItemOrder = header.baseItem.order
				BigWorld.player().bank_moveItem( bagIndex, srcItemOrder, bagIndex, dstItemOrder )
				self.__operateCounter = 2										# ���Ӳ����������᷵������
				return True
			else :																# ���򽫸���ɾȥ
				del itemsCombined[ header ]
		return False

	def __moveSortedItems( self, bagIndex ) :
		"""
		�ƶ��������Ʒ
		@return		: bool��True��ʾ�ƶ���һ����Ʒ��False��ʾ��Ʒ�ƶ����
		"""
		itemsSorted = self.__sortingItemDict.get( bagIndex, ( None, None ) )[0]
		if itemsSorted is None : return False
		bagItems = self.__storage.get( bagIndex, {} )
		bagAddress = bagIndex * csdefine.KB_MAX_SPACE
		while itemsSorted :
			srcItem = itemsSorted.pop( 0 )
			srcItemOrder = srcItem.baseItem.order
			dstItemOrder = bagAddress + len( itemsSorted )
			while srcItemOrder != dstItemOrder :
				dstItem = bagItems.get( dstItemOrder, None )
				if dstItem and dstItem.id == srcItem.id and \
				srcItem.baseItem.isBinded() == dstItem.baseItem.isBinded() and \
				dstItem.amount == srcItem.amount :							# �������ȵ����ˣ����������������������Ȼ
					if dstItem in itemsSorted :								# �������ģ������ٽ�����ֱ�Ӽ����һ��λ��
						itemsSorted.remove( dstItem )
					dstItemOrder -= 1										# �����һ��λ�õ���Ʒ��������Ϊ������
				else :
					BigWorld.player().bank_moveItem( bagIndex, srcItemOrder, bagIndex, dstItemOrder )
					self.__operateCounter = 1
					return True
		else :
			INFO_MSG( " Sort complete!" )
			del self.__sortingItemDict[ bagIndex ]
		return False

	# -------------------------------------------------
	def __classifyForSort( self, sortItems ) :
		"""
		�Կɵ�����Ʒ���з��࣬�Ա�֪����Щ��Ʒ��Ҫ���ӣ���Щ����Ҫ
		�����㷨����˼�룺
		1���ȷ����ҳ������ܹ����ӵ���Ʒ��Ȼ�����һ��ĵ������ް�����˳��
		   ���з��飬����ĵ����㷨�����������㷨��
		2�����������ÿ��ĵ�һ����Ʒ��Ϊͷ��㣬����ͬ��������Ʒ���ӵ�
		   �����ϣ���ͷ���ͬ�������ܽ��е��ӵ���Ʒһ��μ�����
		3��������õ���Ʒ���ȵ��Ӻ���λ��˳�����������ÿ����һ��֮���
		   �������������ټ�����һ������Ϊ�������ķ��ؿ��ܵ�����Ʒ��������
		   λ�õ����Է����ı䣬��˱���õȷ��������ز��ܼ�����һ����
		˵�����������㷨��Է������˲ֿ����Ʒ��λ�������Ĳ���������д��
		û���κζ����ԣ������������ķ��ظı��ˣ������㷨��������Ӧ�޸ġ�
		"""
		itemsCombined = MapList()										# �����������ӵ���Ʒ(������ֵ䣬һ��Ҫ��˳�����)
		itemsSorted, combinedGroups = self.__collect( sortItems )
		for groupItems in combinedGroups.itervalues() :
			stackGroups = self.__splitToStack( groupItems )
			for subGroup in stackGroups :
				header = subGroup.pop( 0 )
				itemsSorted.append( header )							# ����Դ��ƷҲ�μ�����
				if subGroup :											# 2�����ϵ���Ʒ�������
					itemsCombined[ header ] = subGroup
		return itemsSorted, itemsCombined

	def __splitToStack( self, groupItems ) :
		"""
		����Ҫ���ӵ���Ʒ��Ϊ���������飬�Ա�֤ÿһ����Ӻ����պ���һ��
		"""
		stackGroups = []												# �������
		totalAmount = 0													# ���浱ǰ�����Ʒ������
		stackUpperLimit = groupItems[0].baseItem.getStackable()
		for item in groupItems :
			residualAmount = totalAmount % stackUpperLimit
			totalAmount += item.amount
			if residualAmount == 0 :									# ���֮ǰ�պ���һ��
				stackGroups.append( [ item ] )							# �򴴽�һ���µķ���
			else :
				lastGroup = stackGroups[-1]								# ȡ�����һ������
				laterAmount = residualAmount + item.amount				# ��������Ӹ���Ʒ��ķ�����Ʒ����
				if laterAmount <= stackUpperLimit :						# ������Ӻ���Ȼ����һ��
					lastGroup.append( item )							# �����Ʒ����÷���
				else :													# ������Ӻ󳬹���������
					lastGroup.append( item )							# ����Ʒ����÷���
					stackGroups.append( [ item ] )						# ͬʱ�Ը���ƷΪͷ��㴴��һ���·���
		return stackGroups

	def __collect( self, itemsList ) :
		"""
		�鲢�ɵ�����Ʒ��������ID����Ʒ���࣬ͬʱ���ְ󶨺Ͳ�����Ʒ��
		�����ɵ�����Ʒ�ŵ�������б��С�
		"""
		itemsSorted = []												# ��Ҫ�����������Ʒ
		combinedGroups = {}												# ��Ҫ���е��ӵ���Ʒ
		for item in itemsList :
			stackUpperLimit = item.baseItem.getStackable()
			if stackUpperLimit > 1 and item.amount < stackUpperLimit :	# �ɵ�����Ʒ
				isBinded = item.baseItem.isBinded()						# ���ְ��벻��
				combineList = combinedGroups.get( ( item.id, isBinded ), [] )
				if combineList :
					combineList.append( item )
				else :
					combineList.append( item )
					combinedGroups[( item.id, isBinded )] = combineList
			else :
				itemsSorted.append( item )								# ���ɵ�����Ʒ�μ�����
		return itemsSorted, combinedGroups

	# -------------------------------------------------
	def __onSort( self, selIndex ) :
		"""
		"""
		if selIndex < 0:return
		player = BigWorld.player()
		if player is None: return
		if not player.inWorld: return
		# ������������ֱ�ӷ���
		if player._isBankLocked():
			player.statusMessage( csstatus.BANK_ITEM_CANNOT_MOVE )
			return

		currBagIndex = self.currBagIndex
		if self.__sortingItemDict.has_key( currBagIndex ) :
			player.statusMessage( csstatus.SYSTEM_IS_BUSY )
			return
		INFO_MSG( " OK, now sort begin!" )
		self.__sortBox.pyBox_.text = self.__sortBox.selItem
		bagItemsList = self.__storage.get( currBagIndex, {} ).values()
		itemsSorted, itemsCombined = self.__classifyForSort( bagItemsList )
		self.__sortHandlerMap[selIndex]( itemsSorted )
		self.__sortingItemDict[currBagIndex] = ( itemsSorted, itemsCombined )
		self.__moveItemForSort( currBagIndex )

	def __sortByType( self, itemList ) :
		"""
		����������
		"""
		def func( item1, item2 ) :
			if item1.id != item2.id :
				return cmp( item1.id, item2.id )
			else :
				return cmp( item1.baseItem.isBinded(), item2.baseItem.isBinded() )
		itemList.sort( cmp = func, reverse = True )

	def __sortByQuality( self, itemList ):
		"""
		��Ʒ�ʴӸߵ�������ͬƷ�ʰ��ȼ��Ӹߵ�������ͬƷ�ʡ��ȼ�����id����
		"""
		def func( item1, item2 ) :
			if item1.quality != item2.quality :
				return cmp( item2.quality, item1.quality )					# �Ȱ�Ʒ������
			elif item1.level != item2.level :
				return cmp( item2.level, item1.level )						# ͬƷ�ʰ��ȼ�����
			elif item1.id != item2.id :
				return cmp( item1.id, item2.id )
			else :
				return cmp( item1.baseItem.isBinded(), item2.baseItem.isBinded() )
		itemList.sort( cmp = func, reverse = True )

	def __sortByPrice( self, itemList ):
		"""
		���۸�Ӹߵ�������ͬ�۸񰴵ȼ��Ӹߵ�������ͬ�۸񡢵ȼ�����id����
		"""
		def func( item1, item2 ) :
			if item1.price != item2.price :									# �Ȱ��۸�����
				return cmp( item2.price, item1.price )
			elif item1.quality != item2.quality :
				return cmp( item2.quality, item1.quality )					# ͬ�۸�Ʒ������
			elif item1.level != item2.level :
				return cmp( item2.level, item1.level )						# ͬƷ�ʰ��ȼ�����
			elif item1.id != item2.id :
				return cmp( item1.id, item2.id )
			else :
				return cmp( item1.baseItem.isBinded(), item2.baseItem.isBinded() )
		itemList.sort( cmp = func, reverse = True )

	def __sortByLevel( self, itemList ):
		"""
		���ȼ��Ӹߵ�������ͬ�ȼ���Ʒ�ʴӸߵ�������ͬ�ȼ���Ʒ�ʣ���id����
		"""
		def func( item1, item2 ) :
			if item1.level != item2.level :
				return cmp( item2.level, item1.level )						# �Ȱ��ȼ�����
			elif item1.quality != item2.quality :
				return cmp( item2.quality, item1.quality )					# ͬ�ȼ���Ʒ������
			elif item1.id != item2.id :
				return cmp( item1.id, item2.id )
			else :
				return cmp( item1.baseItem.isBinded(), item2.baseItem.isBinded() )
		itemList.sort( cmp = func, reverse = True )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onBagNameUpdated( self, bagIndex, name ) :
		"""
		�������Ƹı�
		"""
		pyRelativeBtn = self.__getPyBagBtn( bagIndex )
		if pyRelativeBtn is not None :
			if name == "" :
				name = labelGather.getText( "StoreWndRole:Panel", self._DEF_PACKAGE_NAME[bagIndex] )
			pyRelativeBtn.text = name
			pyRelativeBtn.enable = True
			if self.currBagIndex == pyRelativeBtn.bagIndex :
				self.__pyBagName.text = name
		else :
			ERROR_MSG( "Storage %d not found!" % bagIndex )

	def onItemAdded( self, bagIndex, itemOrder, baseItem ) :
		"""
		���һ����Ʒ���ֿ�
		"""
		if not self.__storage.has_key( bagIndex ) :
			self.__storage[ bagIndex ] = {}
		itemInfo = self.__storage[ bagIndex ].get( itemOrder, None )
		if itemInfo is None :
			itemInfo = ObjectItem( baseItem )
			self.__storage[ bagIndex ][ itemOrder ] = itemInfo
		else :
			itemInfo.update( baseItem )
		if bagIndex == self.currBagIndex :
			self.__setBagAmount( bagIndex )
			index = itemOrder % csdefine.KB_MAX_SPACE
			pyItem = self.__pyItems.get( index, None )
			if pyItem is None :
				ERROR_MSG( "Item %d is out of index!" % index )
				return
			pyItem.update( itemInfo )
		self.__moveItemForSort( bagIndex )

	def onItemSwaped( self, srcBagIndex, srcItemOrder, dstBagIndex, dstItemOrder ) :
		"""
		������Ʒ��λ��
		"""
		if srcBagIndex == dstBagIndex :
			if srcBagIndex == self.currBagIndex :
				pySrcItem = self.__pyItems.get( srcItemOrder % csdefine.KB_MAX_SPACE, None )
				pyDstItem = self.__pyItems.get( dstItemOrder % csdefine.KB_MAX_SPACE, None )
				dstItemInfo = pyDstItem.itemInfo
				pyDstItem.update( pySrcItem.itemInfo )
				pySrcItem.update( dstItemInfo )

			bag = self.__storage[srcBagIndex]
			if bag.has_key( srcItemOrder ) :
				if bag.has_key( dstItemOrder ) :
					temp = bag[ srcItemOrder ]							# order�Ĵ���Ƚ����⣬order������baseItem�����ԣ�
					bag[ srcItemOrder ] = bag[ dstItemOrder ]			# ��Ӧ����ui�����������ǳ��ڴ����Ż��Ŀ��ǣ�����
					bag[ srcItemOrder ].baseItem.order = srcItemOrder	# ʱ������ֻ����������������baseItem�����Գ���order
					bag[ dstItemOrder ] = temp							# ������䣬���order��ui��������á�
					bag[ dstItemOrder ].baseItem.order = dstItemOrder
				else :
					bag[ dstItemOrder ] = bag[ srcItemOrder ]
					bag[ dstItemOrder ].baseItem.order = dstItemOrder
					del bag[ srcItemOrder ]
			else :
				ERROR_MSG( "Detect that the source item is None��This condition should not appear!" )
				if bag.has_key( dstItemOrder ) :
					bag[ srcItemOrder ] = bag[ dstItemOrder ]
					del bag[ dstItemOrder ]
			self.__moveItemForSort( srcBagIndex )						# �����Ʒ�����ڽ��У����������
		else :
			ERROR_MSG( "Currently it is not supported swapping item between different storage!" )

	def onItemUpdated( self, bagIndex, itemOrder, baseItem ) :
		"""
		����ĳ���ض��������ض�����Ʒ
		"""
		bag = self.__storage.get( bagIndex, {} )
		if baseItem is None :
			if bag.has_key( itemOrder ) :
				del bag[ itemOrder ]
			else :
				ERROR_MSG( "item %d is not in the storage!" % itemOrder )
		itemInfo = bag.get( itemOrder, None )
		if itemInfo is not None :
			itemInfo.update( baseItem )
		elif baseItem :															# �ߵ�����˵���������Ʒ�������ϲ�Ӧ���ô˽ӿ������Ʒ
			INFO_MSG( "Should not use the update method to add a new item of %d at order %d" % ( baseItem.id, itemOrder ) )
			itemInfo = ObjectItem( baseItem )
			bag[ itemOrder ] = itemInfo
			self.__storage[ bagIndex ] = bag
		if bagIndex == self.currBagIndex :
			pyItem = self.__pyItems[ itemOrder % csdefine.KB_MAX_SPACE ]
			pyItem.update( itemInfo )
			self.__setBagAmount( bagIndex )
		self.__moveItemForSort( bagIndex )

	def onBagActivated( self, bagIndex ) :
		"""
		����ĳ���ֿ�
		"""
		pyBagBtn = self.__getPyBagBtn( bagIndex )
		if pyBagBtn is not None :
			pyBagBtn.enable = True
		else :
			ERROR_MSG( "Storage button %d not found!" % bagIndex )

	def dispose( self ) :
		GUIBaseObject.dispose( self )
		self.__sortHandlerMap = None

	def cleanPanel( self ) :
		"""
		�����Ʒ��壬����������Ʒ����
		"""
		self.__storage = {}
		self.__sortingItemDict = {}
		for pyItem in self.__pyItems.itervalues() :
			pyItem.update( None )
		for pyBagBtn in self.__btnsGroup.pySelectors :
			pyBagBtn.enable = False
			pyBagBtn.text = labelGather.getText( "StoreWndRole:Panel", self._DEF_PACKAGE_NAME[pyBagBtn.bagIndex] )
			if pyBagBtn.bagIndex == 0 :
				self.__btnsGroup.pyCurrSelector = pyBagBtn


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getCurrSelIndex( self ) :
		pyCurrSelBtn = self.__btnsGroup.pyCurrSelector
		if pyCurrSelBtn is not None :
			return pyCurrSelBtn.bagIndex
		return -1

	currBagIndex = property( _getCurrSelIndex )						# ��ȡ��ǰѡ�еı�������

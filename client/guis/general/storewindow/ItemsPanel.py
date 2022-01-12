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

	# 默认包裹名称
	_DEF_PACKAGE_NAME = { 0:"btn_0",1:"btn_1",2:"btn_2",3:"btn_3",4:"btn_4",5:"btn_5",6:"btn_6"}

	def __init__( self, panel, pyBinder = None ):
		GUIBaseObject.__init__( self, panel )

		self.__pyItems = {}								# 保存物品格
		self.__storage = {}								# 保存仓库物品{ bagIndex: { itemOrder: itemInfo, ...}, ...}
		self.__pyMsgBox = None							# 保存消息窗口，用于控制最多显示一个窗口
		self.__sortingItemDict = {}
		self.__sortHandlerMap = {}
		self.__operateCounter = 0						# 记录下需要等待几次服务器返回再继续下次操作

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
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( panel.st_taxisText, "StoreWndRole:Panel", "st_taxisText" )
		labelGather.setLabel( panel.st_customText, "StoreWndRole:Panel", "st_customText" )

	def __initItems( self, panel ):
		"""
		初始化物品格
		"""
		for name, item in panel.panel_0.children:
			index = int( name.split( "_" )[1] )
			pyItem = StoreItem( item, index, self )
			self.__pyItems[index] = pyItem

	def __initButtons( self, panel ) :
		"""
		初始化仓库按钮
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
		self.__btnsGroup.pyCurrSelector = self.__getPyBagBtn( 0 )		# 默认选中第一个仓库位

	def __initSortBox( self, panel ) :
		"""
		初始化排序窗口
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
			pyViewItem.pyLabel.foreColor = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyLabel.foreColor = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
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
		选取某个包裹
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
		按回车就保存自定义名称
		"""
		if key == KEY_RETURN and mods == 0:
			text = self.__pyBagName.text.strip()
			if text == "":
				# "您输入的名称无效，请重新输入。"
				self.__showMsg( mbmsgs[0x0801] )
			elif self.__pyBagName.length > 8:
				self.__showMsg( mbmsgs[0x0804] )
			elif not rds.wordsProfanity.isPureString( text ):
				# "名称不合法！"
				self.__showMsg( mbmsgs[0x0802] )
			elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
				# "输入的名称有禁用词汇！"
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
		获取和背包对应的按钮
		"""
		pyBagBtns = self.__btnsGroup.pySelectors
		for pyBagBtn in pyBagBtns :
			if pyBagBtn.bagIndex == bagIndex :
				return pyBagBtn
		return None

	def __getBagAmount( self, bagIndex ) :
		"""
		获取某个仓库包裹的物品个数
		"""
		return len( self.__storage.get( bagIndex, {} ) )

	def __setBagAmount( self, bagIndex ) :
		"""
		显示某个包裹的物品数量
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
		物品排序中，交换物品
		"""
		self.__operateCounter -= 1
		if self.__operateCounter > 0 : return									# 判断是服务器是否已处理完并返回了

		if not self.__combineSortedItems( bagIndex ) :							# 如果还有物品需要叠加，则不进行移动操作
			self.__moveSortedItems( bagIndex )									# 若物品都叠加完毕，则进行物品移动

	def __combineSortedItems( self, bagIndex ) :
		"""
		叠加排序的物品
		@return		: bool，True表示叠加了一个物品，False表示物品叠加完毕
		"""
		itemsCombined = self.__sortingItemDict.get( bagIndex, ( None, None ) )[1]
		if not itemsCombined : return False
		for header, stackGroup in itemsCombined.items() :
			if stackGroup :														# 列表不空
				stackItem = stackGroup.pop( 0 )									# 取第一个进行叠加
				srcItemOrder = stackItem.baseItem.order
				dstItemOrder = header.baseItem.order
				BigWorld.player().bank_moveItem( bagIndex, srcItemOrder, bagIndex, dstItemOrder )
				self.__operateCounter = 2										# 叠加操作服务器会返回两次
				return True
			else :																# 否则将该组删去
				del itemsCombined[ header ]
		return False

	def __moveSortedItems( self, bagIndex ) :
		"""
		移动排序的物品
		@return		: bool，True表示移动了一个物品，False表示物品移动完毕
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
				dstItem.amount == srcItem.amount :							# 由于是先叠加了，所以这里如果数量相等则必然
					if dstItem in itemsSorted :								# 都是满的，不必再交换，直接检查下一个位置
						itemsSorted.remove( dstItem )
					dstItemOrder -= 1										# 检查上一个位置的物品，减是因为反序了
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
		对可叠加物品进行分类，以便知道哪些物品需要叠加，哪些不需要
		排序算法大致思想：
		1、先分类找出所有能够叠加的物品，然后根据一组的叠加上限按叠加顺序
		   进行分组，这里的叠加算法并不是最优算法；
		2、经过分组后，每组的第一个物品作为头结点，以让同组其他物品叠加到
		   它身上，该头结点同其他不能进行叠加的物品一起参加排序；
		3、将整理好的物品按先叠加后移位的顺序发向服务器，每发送一个之后等
		   待服务器返回再继续下一个，因为服务器的返回可能导致物品的数量、
		   位置等属性发生改变，因此必须得等服务器返回才能继续下一个；
		说明：该排序算法针对服务器端仓库对物品移位、交换的操作反馈编写，
		没有任何独立性，将来服务器的返回改变了，排序算法还得作相应修改。
		"""
		itemsCombined = MapList()										# 保存用来叠加的物品(有序的字典，一定要按顺序叠加)
		itemsSorted, combinedGroups = self.__collect( sortItems )
		for groupItems in combinedGroups.itervalues() :
			stackGroups = self.__splitToStack( groupItems )
			for subGroup in stackGroups :
				header = subGroup.pop( 0 )
				itemsSorted.append( header )							# 叠加源物品也参加排序
				if subGroup :											# 2个以上的物品才需叠加
					itemsCombined[ header ] = subGroup
		return itemsSorted, itemsCombined

	def __splitToStack( self, groupItems ) :
		"""
		将需要叠加的物品分为几个叠加组，以保证每一组叠加后最多刚好满一组
		"""
		stackGroups = []												# 保存分组
		totalAmount = 0													# 保存当前类别物品的总数
		stackUpperLimit = groupItems[0].baseItem.getStackable()
		for item in groupItems :
			residualAmount = totalAmount % stackUpperLimit
			totalAmount += item.amount
			if residualAmount == 0 :									# 如果之前刚好满一组
				stackGroups.append( [ item ] )							# 则创建一个新的分组
			else :
				lastGroup = stackGroups[-1]								# 取出最后一个分组
				laterAmount = residualAmount + item.amount				# 计算出叠加该物品后的分组物品数量
				if laterAmount <= stackUpperLimit :						# 如果叠加后依然不满一组
					lastGroup.append( item )							# 则把物品加入该分组
				else :													# 如果叠加后超过叠加上限
					lastGroup.append( item )							# 则将物品加入该分组
					stackGroups.append( [ item ] )						# 同时以该物品为头结点创建一个新分组
		return stackGroups

	def __collect( self, itemsList ) :
		"""
		归并可叠加物品，并按照ID将物品分类，同时区分绑定和不绑定物品；
		将不可叠加物品放到另外的列表中。
		"""
		itemsSorted = []												# 需要进行排序的物品
		combinedGroups = {}												# 需要进行叠加的物品
		for item in itemsList :
			stackUpperLimit = item.baseItem.getStackable()
			if stackUpperLimit > 1 and item.amount < stackUpperLimit :	# 可叠加物品
				isBinded = item.baseItem.isBinded()						# 区分绑定与不绑定
				combineList = combinedGroups.get( ( item.id, isBinded ), [] )
				if combineList :
					combineList.append( item )
				else :
					combineList.append( item )
					combinedGroups[( item.id, isBinded )] = combineList
			else :
				itemsSorted.append( item )								# 不可叠加物品参加排序
		return itemsSorted, combinedGroups

	# -------------------------------------------------
	def __onSort( self, selIndex ) :
		"""
		"""
		if selIndex < 0:return
		player = BigWorld.player()
		if player is None: return
		if not player.inWorld: return
		# 背包被锁定，直接返回
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
		按类型排序
		"""
		def func( item1, item2 ) :
			if item1.id != item2.id :
				return cmp( item1.id, item2.id )
			else :
				return cmp( item1.baseItem.isBinded(), item2.baseItem.isBinded() )
		itemList.sort( cmp = func, reverse = True )

	def __sortByQuality( self, itemList ):
		"""
		按品质从高到低排序；同品质按等级从高到低排序；同品质、等级，按id排序。
		"""
		def func( item1, item2 ) :
			if item1.quality != item2.quality :
				return cmp( item2.quality, item1.quality )					# 先按品质排序
			elif item1.level != item2.level :
				return cmp( item2.level, item1.level )						# 同品质按等级排序
			elif item1.id != item2.id :
				return cmp( item1.id, item2.id )
			else :
				return cmp( item1.baseItem.isBinded(), item2.baseItem.isBinded() )
		itemList.sort( cmp = func, reverse = True )

	def __sortByPrice( self, itemList ):
		"""
		按价格从高到低排序；同价格按等级从高到低排序；同价格、等级，按id排序。
		"""
		def func( item1, item2 ) :
			if item1.price != item2.price :									# 先按价格排序
				return cmp( item2.price, item1.price )
			elif item1.quality != item2.quality :
				return cmp( item2.quality, item1.quality )					# 同价格按品质排序
			elif item1.level != item2.level :
				return cmp( item2.level, item1.level )						# 同品质按等级排序
			elif item1.id != item2.id :
				return cmp( item1.id, item2.id )
			else :
				return cmp( item1.baseItem.isBinded(), item2.baseItem.isBinded() )
		itemList.sort( cmp = func, reverse = True )

	def __sortByLevel( self, itemList ):
		"""
		按等级从高到低排序；同等级按品质从高到低排序；同等级、品质，按id排序。
		"""
		def func( item1, item2 ) :
			if item1.level != item2.level :
				return cmp( item2.level, item1.level )						# 先按等级排序
			elif item1.quality != item2.quality :
				return cmp( item2.quality, item1.quality )					# 同等级按品质排序
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
		包裹名称改变
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
		添加一个物品到仓库
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
		交换物品的位置
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
					temp = bag[ srcItemOrder ]							# order的处理比较特殊，order本来是baseItem的属性，
					bag[ srcItemOrder ] = bag[ dstItemOrder ]			# 不应该由ui层来管理，但是出于带宽优化的考虑，交换
					bag[ srcItemOrder ].baseItem.order = srcItemOrder	# 时服务器只发送了索引过来，baseItem的属性除了order
					bag[ dstItemOrder ] = temp							# 外均不变，因此order在ui层进行设置。
					bag[ dstItemOrder ].baseItem.order = dstItemOrder
				else :
					bag[ dstItemOrder ] = bag[ srcItemOrder ]
					bag[ dstItemOrder ].baseItem.order = dstItemOrder
					del bag[ srcItemOrder ]
			else :
				ERROR_MSG( "Detect that the source item is None！This condition should not appear!" )
				if bag.has_key( dstItemOrder ) :
					bag[ srcItemOrder ] = bag[ dstItemOrder ]
					del bag[ dstItemOrder ]
			self.__moveItemForSort( srcBagIndex )						# 如果物品排序还在进行，则继续排序
		else :
			ERROR_MSG( "Currently it is not supported swapping item between different storage!" )

	def onItemUpdated( self, bagIndex, itemOrder, baseItem ) :
		"""
		更新某个特定背包内特定的物品
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
		elif baseItem :															# 走到这里说明是添加物品，理论上不应该用此接口添加物品
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
		激活某个仓库
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
		清空物品面板，包括所有物品数据
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

	currBagIndex = property( _getCurrSelIndex )						# 获取当前选中的背包索引

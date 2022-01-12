# -*- coding: gb18030 -*-
#
# $Id: GooodsPanel.py, fangpengjun Exp $

"""
implement goods panel class

"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.TabCtrl import TabPanel
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.SelectableButton import SelectableButton
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.StaticText import StaticText
from guis.controls.ODPagesPanel import ODPagesPanel
from ItemsFactory import ObjectItem
from SpecialItem import SpecialItem
import csdefine
import csstatus

class GoodsPanel( TabPanel ):

	_cc_amount = 8 #ÿҳ��ʾ����
	_cc_items_rows = ( 4, 2 )
	
	_cc_sub_types = {csdefine.SPECIALSHOP_ESPECIAL_GOODS :{0:"��Ƕˮ��", 1:"�����챦"},
				csdefine.SPECIALSHOP_CURE_GOODS:{2:"�����鵤", 3:"�ָ�ҩƷ"},
				csdefine.SPECIALSHOP_VEHICLE_GOODS:{4:"½������", 5:"��������", 11:"�������"},
				csdefine.SPECIALSHOP_PET_GOODS:{6:"�������", 7:"��走", 8:"�����鼮"},
				csdefine.SPECIALSHOP_FASHION_GOODS:{9:"��װ", 10:"Ůװ"},
			}

	def __init__( self, panel, pyBinder = None ):
		TabPanel.__init__( self, panel, pyBinder )
		self.__pagesNum = -1
		self.__totalItemIDs = []							# ��������ӵ���Ʒ��Ŀ���Ƕ���˳��
		self.affirmBuy = True 								# ����ʱ�Ƿ񵯳�����ȷ��
		self.__triggers = {}
		self.__registerTriggers()

		self.__pyAffirmChecker = CheckBoxEx( panel.affirmChecker ) #ȷ�Ϲ���
		self.__pyAffirmChecker.checked = True
		self.__pyAffirmChecker.onCheckChanged.bind( self.__onAffirmCheck )
		
		self.__pyPagePanel = ODPagesPanel( panel.itemsPanel, panel.pgIdxBar )
		self.__pyPagePanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pyPagePanel.onDrawItem.bind( self.__drawListItem )
		self.__pyPagePanel.selectable = True
		self.__pyPagePanel.onItemSelectChanged.bind( self.__onItemSelectedChange )
		self.__pyPagePanel.onItemRClick.bind( self.__onClickToBuy )
		self.__pyPagePanel.viewSize = self._cc_items_rows
		
		self.__pySubGroup = SelectorGroup()
		for name, item in panel.children:
			if not name.startswith( "btn_" ):continue
			index = int( name.split( "_" )[1] )
			pySelBtn = SelectableButton( item )
			pySelBtn.setStatesMapping( UIState.MODE_R3C1 )
			pySelBtn.commonForeColor = ( 255, 248, 158, 255 )
			pySelBtn.selectedForeColor = ( 255, 255, 255, 255 )
			pySelBtn.index = index
			pySelBtn.visible = False
			self.__pySubGroup.addSelector( pySelBtn )
		self.__pySubGroup.onSelectChanged.bind( self.__onSubSelect )

		labelGather.setLabel( panel.stTips, "SpecialShop:main", "stTips" )
		labelGather.setLabel( panel.affirmChecker.stext, "SpecialShop:main", "affirmChecker" )
		labelGather.setLabel( panel.pageText, "SpecialShop:main", "page" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SPECIAL_GOODS_RECIEVE"] = self.__onReceiveGoods #ȫ����Ʒ����

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# ------------------------------------------------------------------
	def __onReceiveGoods( self, queryType, goods, moneyType = csdefine.SPECIALSHOP_MONEY_TYPE_GOLD ):
		"""
		�˷����Ѿ��޸�Ϊ����������ӵ��������Ʒ
		@param gType:	��Ʒ�����Ĵ���,��������Ʒ��
		@param goods:	��Ʒ��Ϣ
		@return:		none
		"""
		pyTabCtr = self.pyBinder.pyTabCtr
		if pyTabCtr.pySelPage is None :return
		type =  pyTabCtr.pySelPage.type
		currSelType = int( math.pow( 2, type - 1 ) )
		if currSelType == queryType : #���ӷ���
			if currSelType in self._cc_sub_types:
				subTypes = self._cc_sub_types[currSelType].keys()
				for index, subType in enumerate( subTypes ):
					pySelector = self.__pySubGroup.pySelectors[index]
					pySelector.visible = pySelector.index == index
					pySelector.subType = subType
					pySelector.text = self._cc_sub_types[currSelType][subType]
				self.__pySubGroup.pyCurrSelector = self.__pySubGroup.pySelectors[0]
				subType = self.__pySubGroup.pyCurrSelector.subType
				if goods[-1] == subType:
					self.__onItemUpdate( goods )
			else: #���ӷ���
				self.__onItemUpdate( goods )
		if queryType != csdefine.SPECIALSHOP_RECOMMEND_GOODS :	# �Ƽ���Ʒ�Ѱ��������������
			if not goods[0] in self.__totalItemIDs :
				self.__totalItemIDs.append( goods[0] )
			if type == 0 :								# ���ѡ����ȫ����Ʒ
				self.__onItemAdded( goods )
				
	def __initListItem( self, pyViewItem ) :
		"""
		��ʼ����ӵ���Ʒ�б���
		"""
		pySpecItem = SpecialItem( DragMark.SPECIAL_SHOP_WND, self )
		pyViewItem.pySpecItem = pySpecItem
		pyViewItem.addPyChild( pySpecItem )
		pyViewItem.focus = True
		pySpecItem.left = 0
		pySpecItem.top = 0

	def __drawListItem( self, pyViewItem ) :
		"""
		�ػ���Ʒ�б���
		"""
		itemInfo = pyViewItem.pageItem
		pySpecItem = pyViewItem.pySpecItem
		pySpecItem.selected = pyViewItem.selected
		pySpecItem.update( itemInfo )
		curPageIndex = self.__pyPagePanel.pageIndex
		totalPageIndex = self.__pyPagePanel.maxPageIndex
	
	def __onSubSelect(self, pySubBtn ):
		"""
		ѡ����������Ʒ
		"""
		pyTabCtr = self.pyBinder.pyTabCtr
		if pyTabCtr.pySelPage is None :return
		type =  pyTabCtr.pySelPage.type
		goodsType = int( math.pow( 2, type - 1 ) )
		index = pySubBtn.index
		player = BigWorld.player()
		goodsDict = player.specialItemData[csdefine.SPECIALSHOP_MONEY_TYPE_GOLD]
		if goodsType in self._cc_sub_types:
			self.__pyPagePanel.clearItems()
			subTypes = self._cc_sub_types[goodsType].keys()
			subType = subTypes[index]
			goodsIDs = player.goodsTypeMap[player.spe_moneyType][goodsType][0][subType]
			goodsList = [goodsDict.get( id, None ) for id in goodsIDs]
			self.__addItems( goodsList )

	def __onItemSelectedChange( self, index ):
		player = BigWorld.player()
		itemInfo = self.__pyPagePanel.selItem
		if itemInfo is None:return
		baseInfo = itemInfo.baseInfo
		baseItem = baseInfo.baseItem
		self.pyTopParent.setTryState( baseItem )
	
	def __onItemAdded( self, goods ) :
		"""
		ѡ��ȫ����Ʒʱ�ĸ���ͨ��
		"""
		itemID = goods[0]
		item = BigWorld.player().createDynamicItem( itemID )
		if item is None : return
		price = goods[2]
		dsp = goods[3]
		itemInfo = ItemInfo( item, price, dsp )
		if itemInfo not in self.__pyPagePanel.items:
			self.__pyPagePanel.addItem( itemInfo )

	def __onItemUpdate( self, goods ) :
		"""
		��ȫ����Ʒ���͵�����ĸ���ͨ��
		"""
		itemID = goods[0]
		item = BigWorld.player().createDynamicItem( itemID )
		if item is None : return
		price = goods[2]
		dsp = goods[3]
		itemInfo = ItemInfo( item, price, dsp )
		if itemInfo not in self.__pyPagePanel.items:
			self.__pyPagePanel.addItem( itemInfo )

	def __onClickToBuy( self, pyViewItem ) :
		pageItem = pyViewItem.pageItem
		if pageItem is None : return
		self.__pyPagePanel.selItem = pageItem						# ��Ϊѡ����
		pyViewItem = None
		for pyItem in self.__pyPagePanel.pyViewItems :
			if pyItem.selected :
				pyViewItem = pyItem
				break
		if pyViewItem is None : return
		isSingle = not( BigWorld.isKeyDown( KEY_RSHIFT ) or BigWorld.isKeyDown( KEY_LSHIFT ) )
		pyViewItem.pySpecItem.onClickToBuy( isSingle )

	def __onAffirmCheck( self, checked ):
		self.affirmBuy = checked

	def __showSpecialItems( self, goodsType ):
		self.__pyPagePanel.clearItems()
		items = self.__getTypeItems( goodsType )
		self.__addItems( items )
		
	def __addItems( self, items ):
		for index, item in enumerate( items ):
			if item is None:continue
			itemID = item[0]
			baseItem = BigWorld.player().createDynamicItem( itemID )
			if baseItem is None : continue
			price = item[2]
			dsp = item[3]
			itemInfo = ItemInfo( baseItem, price, dsp )
			if itemInfo not in self.__pyPagePanel.items:
				self.__pyPagePanel.addItem( itemInfo )
		
	def __onSetPages( self ):
		curPageIndex = self.__pyPagePanel.pageIndex
		totalPageIndex = self.__pyPagePanel.maxPageIndex
	
	def __getTypeItems( self, goodsType ):
		"""
		��ȡĳһ����Ʒ�б�
		"""
		player = BigWorld.player()
		goodsDict = player.specialItemData[csdefine.SPECIALSHOP_MONEY_TYPE_GOLD]
		if goodsType == 0 :					# ȫ����Ʒ
			goodsIDs = self.__totalItemIDs
		else :
			if goodsType in self._cc_sub_types:
				pyCurSel = self.__pySubGroup.pyCurrSelector
				if pyCurSel is None:return
				subType = pyCurSel.subType
				goodsIDs = player.goodsTypeMap[csdefine.SPECIALSHOP_MONEY_TYPE_GOLD][goodsType][0][subType]
			else:
				goodsIDs = player.goodsTypeMap[csdefine.SPECIALSHOP_MONEY_TYPE_GOLD][goodsType][0]
		goodsList = [goodsDict.get( id, None ) for id in goodsIDs]
		return goodsList

	def __resetSubBtns( self ):
		for pySelector in self.__pySubGroup.pySelectors:
			pySelector.visible = False
	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )
	
	def onGoodsTypeChange( self, type ):
		self.__pyPagePanel.clearItems()
		goodsType = int( math.pow( 2, type - 1 ) )
		self.__resetSubBtns()
		if type != 0:
			BigWorld.player().spe_queryGoods( goodsType, csdefine.SPECIALSHOP_MONEY_TYPE_GOLD )
		if goodsType in self._cc_sub_types:
			subTypes = self._cc_sub_types[goodsType].keys()
			for index, subType in enumerate( subTypes ):
				pySelector = self.__pySubGroup.pySelectors[index]
				pySelector.visible = pySelector.index == index
				pySelector.subType = subType
				pySelector.text = self._cc_sub_types[goodsType][subType]
			self.__pySubGroup.pyCurrSelector = self.__pySubGroup.pySelectors[0]
		self.__showSpecialItems( goodsType )
		BigWorld.callback( 1.0, self.__onSetPages )
	
	def onShopClose( self ):
		self.__pyPagePanel.clearItems()
		self.__totalItemIDs = []
	
	def clearGoods( self ):
		self.__pyPagePanel.clearItems()
	
	def getSelGoods( self ):
		return self.__pyPagePanel.selItem
		
	def queryItem( self, itemID ):
		"""
		"""
		qItem = None
		for item in self.__pyPagePanel.items:
			if item.baseInfo.id == itemID:
				qItem = item
		if qItem is not None:
			pageIndex, itemIndex = self.__pyPagePanel.queryItem( qItem )
			if pageIndex != -1:
				self.__pyPagePanel.pageIndex = pageIndex
				return True		
		return False

class ItemInfo:
	def __init__( self, baseItem, price, dsp, moneyType = csdefine.SPECIALSHOP_MONEY_TYPE_GOLD ):
		self.baseInfo = None
		if baseItem is not None:
			self.baseInfo = ObjectItem( baseItem )
		self.price = price
		self.dsp = dsp
		self.moneyType = moneyType
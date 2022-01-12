# -*- coding: gb18030 -*-
"""
implement goods panel class

"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from guis.controls.TabCtrl import TabPanel
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.StaticText import StaticText
from guis.controls.SelectorGroup import SelectorGroup
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.controls.SelectableButton import SelectableButton
from FittingPanel import FittingPanel
from ExplainWnd import ExplainWnd
from ItemsFactory import ObjectItem
from SpecialItem import SpecialItem
import ItemTypeEnum
import csdefine

class GoodsPanel( TabPanel ):
	_cc_amount = 8 #ÿҳ��ʾ����
	_cc_items_rows = ( 4, 2 )
	
	command_type = 2

	def __init__( self, panel, moneyType, pyBinder = None ):
		TabPanel.__init__( self, panel )
		self.affirmBuy = True 								# ����ʱ�Ƿ񵯳�����ȷ��
		self.__totalItemIDs = { csdefine.SPECIALSHOP_MONEY_TYPE_GOLD:[],# ��������ӵ���Ʒ��Ŀ���Ƕ���˳��
								csdefine.SPECIALSHOP_MONEY_TYPE_SILVER:[]
								}
		self.__triggers = {}
		self.__registerTriggers()
		self.moneyType = moneyType
		
		self.__pyTypesGroup = SelectorGroup()
		for name, item in panel.children:
			if not name.startswith( "typeBtn_" ):continue
			type = int( name.split( "_" )[1] )
			pyTypeBtn = SelectableButton( item )
			pyTypeBtn.setStatesMapping( UIState.MODE_R3C1 )
			pyTypeBtn.type = type
			labelGather.setPyBgLabel( pyTypeBtn, "SpecialShop:main", name )
			self.__pyTypesGroup.addSelector( pyTypeBtn )
		self.__pyTypesGroup.onSelectChanged.bind( self.__onTypeSelected )

		self.__pyBtnTry = Button( panel.btnTry ) #�Դ���ť
		self.__pyBtnTry.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnTry.enable = False
		self.__pyBtnTry.onLClick.bind( self.__onFitting )

		self.__pyBtnCharge = Button( panel.btnCharge ) #��ֵ��ť
		self.__pyBtnCharge.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCharge.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyBtnCharge.onMouseLeave.bind( self.__onMouseLeave )
		self.__pyBtnCharge.onLMouseDown.bind( self.__onLMouseDown )
		self.__pyBtnCharge.enable = True
		self.__pyBtnCharge.onLClick.bind( self.__onCharge )

		self.__pyStGold = StaticText( panel.stGold ) #��ҽ�Ԫ������
		self.__pyStGold.charSpace = -1.0
		self.__pyStGold.fontSize = 12
		self.__pyStGold.text = ""

		self.__pyBtnGuide = Button( panel.btnGuide ) #����ָ��
		self.__pyBtnGuide.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnGuide.onLClick.bind( self.__onShowGuide )

		self.__pyAffirmChecker = CheckBoxEx( panel.affirmChecker ) #ȷ�Ϲ���
		self.__pyAffirmChecker.checked = True
		self.__pyAffirmChecker.onCheckChanged.bind( self.__onAffirmCheck )
		
		self.__pyStPages = StaticText( panel.stPages )
		self.__pyStPages.text = ""

		self.__pyPagePanel = ODPagesPanel( panel.itemsPanel, panel.pgIdxBar )
		self.__pyPagePanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pyPagePanel.onDrawItem.bind( self.__drawListItem )
		self.__pyPagePanel.selectable = True
		self.__pyPagePanel.onItemSelectChanged.bind( self.__onItemSelectedChange )
		self.__pyPagePanel.onItemRClick.bind( self.__onClickToBuy )
		self.__pyPagePanel.viewSize = self._cc_items_rows

		labelGather.setPyBgLabel( self.__pyBtnTry, "SpecialShop:main", "btnTry" )
		labelGather.setPyBgLabel( self.__pyBtnGuide, "SpecialShop:main", "btnGuide" )
		labelGather.setPyBgLabel( self.__pyBtnCharge, "SpecialShop:main", "btnCharge" )
		labelGather.setLabel( panel.pgIdxBar.btnDec.lbText, "SpecialShop:main", "btnDec" )
		labelGather.setLabel( panel.pgIdxBar.btnInc.lbText, "SpecialShop:main", "btnInc" )
		labelGather.setLabel( panel.affirmChecker.stext, "SpecialShop:main", "buyConfirm" )

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
	def __onReceiveGoods( self, queryType, goods, index, moneyType ):
		"""
		�˷����Ѿ��޸�Ϊ����������ӵ��������Ʒ
		@param gType:	��Ʒ�����Ĵ���,��������Ʒ��
		@param goods:	��Ʒ��Ϣ
		@return:		none
		"""
		pyCurrTypeBtn = self.__pyTypesGroup.pyCurrSelector
		if pyCurrTypeBtn is None:return
		if self.moneyType != moneyType:return
		type = pyCurrTypeBtn.type
		currSelType = int( math.pow( 2, type - 1 ) )
		if currSelType == queryType :
			self.__onItemUpdate( goods, index )
		if queryType != csdefine.SPECIALSHOP_RECOMMEND_GOODS :	# �Ƽ���Ʒ�Ѱ��������������
			totalItemIDs = self.__totalItemIDs.get( moneyType, [] )
			if not goods[0] in totalItemIDs :
				totalItemIDs.append( goods[0] )
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
		pySpecItem = getattr( pyViewItem, "pySpecItem", None )
		if pySpecItem is not None:
			pySpecItem.selected = pyViewItem.selected
			pySpecItem.update( itemInfo )
		curPageIndex = self.__pyPagePanel.pageIndex
		totalPageIndex = self.__pyPagePanel.maxPageIndex
		self.__pyStPages.text = "%d/%d"%( curPageIndex + 1, totalPageIndex + 1 )

	def __onItemSelectedChange( self, index ):
		player = BigWorld.player()
		itemInfo = self.__pyPagePanel.selItem
		if itemInfo is None:return
		baseInfo = itemInfo.baseInfo
		baseItem = baseInfo.baseItem
		self.__pyBtnTry.enable = baseItem.isEquip() and baseItem.canWield( BigWorld.player() ) or baseItem.isType( 394497 )
	
	def __onItemAdded( self, goods ) :
		"""
		ѡ��ȫ����Ʒʱ�ĸ���ͨ��
		"""
		itemID = goods[0]
		item = BigWorld.player().createDynamicItem( itemID )
		if item is None : return
		price = goods[2]
		dsp = goods[3]
		moneyType = goods[-1]
		itemInfo = ItemInfo( item, price, dsp, moneyType )
		if itemInfo.id not in [item.id for item in self.__pyPagePanel.items]:
			self.__pyPagePanel.addItem( itemInfo )

	def __onItemUpdate( self, goods, index ) :
		"""
		��ȫ����Ʒ���͵�����ĸ���ͨ��
		"""
		itemID = goods[0]
		item = BigWorld.player().createDynamicItem( itemID )
		if item is None : return
		price = goods[2]
		dsp = goods[3]
		moneyType = goods[-1]
		itemInfo = ItemInfo( item, price, dsp, moneyType )
		if itemInfo.id not in [item.id for item in self.__pyPagePanel.items]:
			self.__pyPagePanel.addItem( itemInfo )

	def __onMouseEnter( self, pyBtn ):
		if pyBtn.pyText_:
			pyBtn.foreColor = 95, 255, 8, 255

	def __onMouseLeave( self, pyBtn ):
		if pyBtn.pyText_:
			pyBtn.foreColor = 255, 248, 158, 255

	def __onLMouseDown( self, pyBtn ):
		if pyBtn.pyText_:
			pyBtn.foreColor = 255, 248, 158, 255
	
	def __onFitting( self ):
		itemInfo = self.__pyPagePanel.selItem
		if itemInfo is None:return
		baseItem = itemInfo.baseInfo.baseItem
		if baseItem.isEquip() and baseItem.canWield( BigWorld.player() ):
			FittingPanel.instance().addNewModel( baseItem )
			if not FittingPanel.instance().rvisible:
				FittingPanel.instance().show( self )
		#�����
		elif baseItem.isType( ItemTypeEnum.ITEM_SYSTEM_VEHICLE ):
			FittingPanel.instance().addVehicleModel( baseItem )
			if not FittingPanel.instance().rvisible:
				FittingPanel.instance().show( self )
	
	def __onCharge( self ):
		import csol
		csol.openUrl( "http://gamemall.wayi.com.tw/shopping/default.asp?action=wgs_list " )
		
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
	
	def __onShowGuide( self ):
		ExplainWnd.instance().show( self )
	
	def __onTypeSelected( self, pyTypeBtn ):
		if pyTypeBtn is None:return
		if not rds.statusMgr.isInWorld():return
		type = pyTypeBtn.type
		self.onGoodsTypeChange( type )

	def __showSpecialItems( self, type ):
		items = self.__getTypeItems( type )
		for index, item in enumerate( items ):
			itemID = item[0]
			baseItem = BigWorld.player().createDynamicItem( itemID )
			if baseItem is None : continue
			price = item[2]
			dsp = item[3]
			moneyType = item[-1]
			itemInfo = ItemInfo( baseItem, price, dsp, moneyType )
			if itemInfo.id not in [item.id for item in self.__pyPagePanel.items]:
				self.__pyPagePanel.addItem( itemInfo )
		
	def __onSetPages( self ):
		curPageIndex = self.__pyPagePanel.pageIndex
		totalPageIndex = self.__pyPagePanel.maxPageIndex
		self.__pyStPages.text = "%d/%d"%( curPageIndex + 1, totalPageIndex + 1 )
	
	def __getTypeItems( self, type ):
		"""
		��ȡĳһ����Ʒ�б�
		"""
		player = BigWorld.player()
		goodsDict = player.specialItemData.get( self.moneyType, {} )
		goodsList = []
		if type == 0 :					# ȫ����Ʒ
			goodsIDs = self.__totalItemIDs[self.moneyType]
		else :
			goodsIDs = player.goodsTypeMap[self.moneyType][type][0]
		for id in goodsIDs:
			goods = goodsDict.get( id, None )
			if goods is None:continue
			goodsList.append( goods )
		return goodsList

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
		if type != 0:
			BigWorld.player().spe_queryGoods( goodsType, self.moneyType )
#		queryGoods = self.__getTypeItems( goodsType )
		self.__showSpecialItems( goodsType )
		BigWorld.callback( 1.0, self.__onSetPages )
	
	def onGoldChange( self, oldSilver, newSilver ):
		self.__pyStGold.text = str( newSilver )
	
	def onShopClose( self ):
		self.__pyPagePanel.clearItems()
		self.__totalItemIDs = { csdefine.SPECIALSHOP_MONEY_TYPE_GOLD:[],# ��������ӵ���Ʒ��Ŀ���Ƕ���˳��
								csdefine.SPECIALSHOP_MONEY_TYPE_SILVER:[]
								}
	
	def resetTypeBtns( self ):
		for pyTypeBtn in self.__pyTypesGroup.pySelectors:
			pyTypeBtn.selected = False
	
	def onShow( self ):
		TabPanel.onShow( self )
	
	def onSelected( self ):
		for pyTypeBtn in self.__pyTypesGroup.pySelectors:
			if pyTypeBtn.type == self.command_type:
				self.__pyTypesGroup.pyCurrSelector = pyTypeBtn
				break
	
	def clearGoods( self ):
		self.__pyPagePanel.clearItems()

class ItemInfo:
	def __init__( self, baseItem, price, dsp, moneyType = csdefine.SPECIALSHOP_MONEY_TYPE_GOLD ):
		self.baseInfo = None
		self.id = 0
		if baseItem is not None:
			self.baseInfo = ObjectItem( baseItem )
			self.id = baseItem.id
		self.price = price
		self.dsp = dsp
		self.moneyType = moneyType
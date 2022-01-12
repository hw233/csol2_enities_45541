# -*- coding: gb18030 -*-

# commission sale merchant search panel
# written by ganjinxing 2009-10-19

import math
import csconst
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.Frame import HVFrame
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.controls.TextBox import TextBox
from guis.controls.StaticText import StaticText
from guis.controls.ODPagesPanel import ODPagesPanel
from GoodsPanel import ColItem as CItem
from TaxisButton import TaxisButtonEx
from Function import Functor
from LabelGather import labelGather


class MerchantPanel( TabPanel ) :

	def __init__( self, pyBinder = None ) :
		panel = GUI.load( "guis/general/commissionsale/shopsviewer/merchantPanel.gui" )
		uiFixer.firstLoadFix( panel )
		TabPanel.__init__( self, panel, pyBinder )

		self.__pyTaxisBtns = []
		self.__initialize( panel )

		self.__queryDict = {}													# 记录当前正在查询的页面
		self.__currPage = 0
		self.__dirCBID = 0
		self.__initCBID1 = 0
		self.__initCBID2 = 0

		self.__triggers = {}
		self.__registerTriggers()

	def __del__( self ) :
		if Debug.output_del_CSMerchantPanel :
			INFO_MSG( str( self ) )
		MerchantItem._MERCHANT_ITEM = None

	def __initialize( self, panel ) :
		for cName, cGui in panel.frame_inner.header.children :
			if "header_" in cName :
				index = int( cName.split("_")[-1] )
				pyTxBtn = TaxisButtonEx( cGui )
				pyTxBtn.setExStatesMapping( UIState.MODE_R3C1 )
				pyTxBtn.taxisIndex = index
				pyTxBtn.onLClick.bind( self.__onTaxis )
				self.__pyTaxisBtns.append( pyTxBtn )
				labelGather.setPyBgLabel( pyTxBtn, "commissionsale:MerchantPanel", cName )

		self.__pySearchBtn = HButtonEx( panel.searchBtn )
		self.__pySearchBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySearchBtn.isOffsetText = True
		self.__pySearchBtn.onLClick.bind( self.__onSearch )
		self.__pySearchBtn.enable = False

		self.__pyKeyWord = TextBox( panel.ibox.box )							# 查找关键字

		self.__pyDirText = StaticText( panel.dirText )							# 操作提示文字
		self.__pyDirText.text = labelGather.getText( "commissionsale:MerchantPanel", "stClewCondition" )

		self.__pyPagesPanel = ODPagesPanel( panel.itemsPanel, panel.idxCtrl )
		self.__pyPagesPanel.onViewItemInitialized.bind( self.__onInitItem )
		self.__pyPagesPanel.onDrawItem.bind( self.__onDrawItem )
		self.__pyPagesPanel.onItemLDBClick.bind( self.__onMerchantItemDBClick )
		self.__pyPagesPanel.pyBtnInc.onLClick.bind( self.__onShowNextPage, True )
		self.__pyPagesPanel.selectable = True
		self.__pyPagesPanel.viewSize = 13, 1									# 13行1列
		self.__initViewItems()

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pySearchBtn, "commissionsale:MerchantPanel", "btnSearch" )
		labelGather.setLabel( panel.stObj, "commissionsale:MerchantPanel", "stKeyWord")

	def __initViewItems( self ) :
		"""
		慢速初始化
		"""
		pyViewItems = self.__pyPagesPanel.pyViewItems
		self.__addVIGradual( pyViewItems )

	def __addVIGradual( self, pyViewItems ) :
		if len( pyViewItems ) == 0 :
			self.__pySearchBtn.enable = True
			self.pyTabPage.enable = True
			self.pyBinder.initGradual()
			return
		pyViewItem = pyViewItems.pop()
		pyItem = MerchantItem( pyViewItem )
		pyViewItem.pyItem = pyItem
		pyViewItem.addPyChild( pyItem )
		pyItem.left = 0
		pyItem.top = 0
		pyItem.refreshInfo( pyViewItem )
		self.__initCBID = BigWorld.callback( 0.05, Functor( self.__addVIGradual, pyViewItems ) )

	def __registerTriggers( self ) :
		self.__triggers["ON_RECEIVE_COMMISSION_SHOP_INFO"] = self.__onReceiveShopInfo
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __desregisterTriggers( self ) :
		for trigger in self.__triggers :
			ECenter.unregisterEvent( trigger, self )

	def __onSearch( self ) :
		"""
		开始查找
		"""
		self.__pyPagesPanel.clearItems()
		self.__queryDict = {}
		keyWord = self.__pyKeyWord.text.strip()
		if keyWord != "" :
			self.__queryDict[csconst.TISHOU_SHOP_INFO] = keyWord
		self.__currPage = 0
		self.__notifySearchResult( "begin" )
		BigWorld.player().base.queryTishouShopInfo( 0, self.__queryDict )

	def __onShowNextPage( self ) :
		pageIndex = self.__pyPagesPanel.pageIndex
		itemCount = ( self.__currPage + 1 ) * csconst.TISHOU_SHOP_INFO_QUERY_PAGE_SIZE
		passPage = math.ceil( itemCount / float( self.__pyPagesPanel.viewCount ) )
		if pageIndex > passPage - 2 :
			self.__currPage += 1
			BigWorld.player().base.queryTishouShopInfo( self.__currPage, self.__queryDict )

	def __onTaxis( self, pyBtn ) :
		"""
		排序
		"""
		taxisIndex = pyBtn.taxisIndex
		taxisReverse = pyBtn.taxisReverse
		self.__pyPagesPanel.separateSort( key = lambda item : item[taxisIndex][0], reverse = taxisReverse )

	def __onInitItem( self, pyViewItem ) :
		pass

	def __onDrawItem( self, pyViewItem ):
		pyItem = getattr( pyViewItem, "pyItem", None )
		if pyItem is not None :
			pyItem.refreshInfo( pyViewItem )

	def __onReceiveShopInfo( self, merchantDBID, merchantName, shopName ) :
		self.__notifySearchResult( "found" )
		shopInfo = ( (shopName,(255,251,0,255 ) ), (merchantName,(204,255,148,255) ), merchantDBID )
		for index, item in enumerate( self.__pyPagesPanel.items ) :
			if merchantDBID == item[-1] :
				self.__pyPagesPanel.updateItem( index, shopInfo )
				print "---------->>> found repeat shop info!"
				break
		else :
			self.__pyPagesPanel.addItem( shopInfo )

	def __notifySearchResult( self, step = "not found" ) :
		if step == "begin" :
			self.__pyDirText.visible = True
			self.__pyDirText.text = labelGather.getText( "commissionsale:MerchantPanel", "stClewSearching" )
			self.__dirCBID = BigWorld.callback( 2, self.__notifySearchResult )			# 2秒后未收到任何数据则默认没有匹配数据
		elif step == "found" :
			self.__pyDirText.visible = False
			if self.__dirCBID > 0 :
				BigWorld.cancelCallback( self.__dirCBID )
				self.__dirCBID = 0
		elif step == "not found" :
			self.__pyDirText.visible = True
			self.__pyDirText.text = labelGather.getText( "commissionsale:MerchantPanel", "stClewNotFound" )
		else :
			self.__pyDirText.visible = False

	def __onMerchantItemDBClick( self, pyViewItem ) :
		"""
		双击某个item时查找店主寄售的所有商品
		"""
		infoItem = pyViewItem.pageItem
		if infoItem is None : return
		merchantName = infoItem[1][0]
		self.pyBinder.searchByMerchantName( merchantName )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isReady( self ) :
		return self.__pySearchBtn.enable

	def keyEventHandler( self, key, mods ) :
		if ( mods == 0 ) and ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# 如果按下了回车键
			if self.__pySearchBtn.enable :
				self.__onSearch()
				return True
		return False

	def onShow( self ) :
		self.__pyPagesPanel.resetState()

	def dispose( self ) :
		TabPanel.dispose( self )
		self.__triggers = {}
		BigWorld.cancelCallback( self.__initCBID )
		BigWorld.cancelCallback( self.__dirCBID )

	def onEnterWorld( self ) :
		pass

	def onRoleMoneyChanged( self, oldValue, newValue ) :
		pass

	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )


class MerchantItem( PyGUI ) :

	_MERCHANT_ITEM = None												# 店长信息项

	def __init__( self, pyBinder = None ) :
		if MerchantItem._MERCHANT_ITEM is None :
			MerchantItem._MERCHANT_ITEM = GUI.load( "guis/general/commissionsale/shopsviewer/merchantitem.gui" )
			uiFixer.firstLoadFix( MerchantItem._MERCHANT_ITEM )
		gui = util.copyGuiTree( MerchantItem._MERCHANT_ITEM )
		PyGUI.__init__( self, gui )

		self.__pyColItems = []
		self.__initialize( gui, pyBinder )

	def __initialize( self, gui, pyBinder ) :
		for name, colUI in gui.children :
			if "col_" in name :
				pyColItem = ColItem( colUI, pyBinder )
				self.__pyColItems.append( pyColItem )

	def __colorCols( self, color ) :
		"""设置列项的颜色"""
		for pyCol in self.__pyColItems :
			pyCol.pyText_.color = color


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def refreshInfo( self, pyViewItem ) :
		infoItem = pyViewItem.pageItem
		if infoItem is None :
			infoItem = ( ( "",(255,255,255,255) ), ( "",(255,255,255,255) ), -1 )
			pyViewItem.focus = False
		else :
			pyViewItem.focus = True
		for pyCItem, info in zip( self.__pyColItems, infoItem ) :
			pyCItem.update( info )

		if pyViewItem.selected and pyViewItem.itemIndex > -1 :
			self.__colorCols( ( 0, 255, 0, 255 ) )
		elif pyViewItem.highlight and infoItem is not None :
			self.__colorCols( ( 0, 255, 0, 255 ) )
		else :
			self.__colorCols( ( 255, 255, 255, 255 ) )


class ColItem( CItem ) :


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		self.pyBinder.onMouseEnter_()
		return CItem.onMouseEnter_( self )

	def onMouseLeave_( self ) :
		self.pyBinder.onMouseLeave_()
		return CItem.onMouseLeave_( self )
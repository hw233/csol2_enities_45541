# -*- coding: gb18030 -*-

# commission sale goods search panel
# written by ganjinxing 2009-10-19

import csdefine
import csconst
import ItemTypeEnum
from guis import *
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.controls.TextBox import TextBox
#from guis.controls.ComboBox import ComboBox
#from guis.controls.ComboBox import ComboItem
from guis.controls.ODComboBox import ODComboBox, InputBox
from guis.controls.TabSwitcher import TabSwitcher
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.tooluis.fulltext.FullText import FullText
from guis.common.UIStatesTab import HStatesTabEx
from TaxisButton import TaxisButtonEx
from Function import Functor

from ItemsFactory import ObjectItem
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
from guis.controls.StaticText import StaticText
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem

from ItemSystemExp import EquipQualityExp
QAColor = EquipQualityExp.instance().getColorByQuality
from LabelGather import labelGather
from guis.MLUIDefine import ItemQAColorMode
from guis.UIFixer import hfUILoader
import Language

class GoodsPanel( TabPanel ) :

	def __init__( self, pyBinder = None ) :
		panel = GUI.load( "guis/general/commissionsale/shopsviewer/goodsPanel.gui" )
		uiFixer.firstLoadFix( panel )
		TabPanel.__init__( self, panel, pyBinder )

		self.__pyCBBoxs = {}										# 保存所有ComboBox
		self.__pyTaxisBtns = []										# 保存所有排序按钮
		self.__initialize( panel )

		self.__queryDict = {}
		self.__currPage = 0
		self.__pyMsgBox = None
		self.__dirCBID = 0
		self.__initCBID1 = 0
		self.__initCBID2 = 0

		self.__triggers = {}
		self.__registerTriggers()

	def __del__( self ) :
		if Debug.output_del_CSGoodsPanel :
			INFO_MSG( str( self ) )
		GoodsItem._GOODS_ITEM = None

	def __initialize( self, panel ) :
		for cName, cGui in panel.frame_inner.header.children :
			if "header_" in cName :
				index = int( cName.split("_")[-1] )
				pyTxBtn = TaxisButtonEx( cGui )
				pyTxBtn.setExStatesMapping( UIState.MODE_R3C1 )
				pyTxBtn.taxisIndex = index
				pyTxBtn.onLClick.bind( self.__onTaxis )
				self.__pyTaxisBtns.append( pyTxBtn )
				labelGather.setPyBgLabel( pyTxBtn, "commissionsale:GoodsPanel", cName )

		self.__pySearchBtn = HButtonEx( panel.searchBtn )
		self.__pySearchBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pySearchBtn.isOffsetText = True
		self.__pySearchBtn.onLClick.bind( self.__onSearch )
		self.__pySearchBtn.enable = False

		self.__pyBuyBtn = HButtonEx( panel.buyBtn )
		self.__pyBuyBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBuyBtn.isOffsetText = True
		self.__pyBuyBtn.onLClick.bind( self.__onBuy )
		self.__pyBuyBtn.enable = False

		self.__pyMoneyBox = MoneyBar( panel.box_money )
		self.__pyMoneyBox.readOnly = True
		self.__updateMoney( 879 )

		self.__pyKeyWord = TextBox( panel.ibKW.box )				# 查找关键字

		self.__pyDirText = StaticText( panel.dirText )				# 操作提示文字
		self.__pyDirText.text = labelGather.getText( "commissionsale:GoodsPanel", "stClewCondition" )

		self.__pyUpperLimit = TextBox( panel.ibUL.box )			# 等级上限
		self.__pyUpperLimit.inputMode = InputMode.INTEGER			# 限制输入为整数类型
		self.__pyUpperLimit.maxLength = 3							# 最多输入三位数

		self.__pyLowerLimit = TextBox( panel.ibLL.box )			# 等级下限
		self.__pyLowerLimit.inputMode = InputMode.INTEGER
		self.__pyLowerLimit.maxLength = 3

		self.__pyTabSwitcher = TabSwitcher( [self.__pyLowerLimit, self.__pyUpperLimit, self.__pyKeyWord] )

		self.__pyPagesPanel = ODPagesPanel( panel.itemsPanel, panel.idxCtrl )
		self.__pyPagesPanel.onViewItemInitialized.bind( self.__onInitItem )
		self.__pyPagesPanel.onItemSelectChanged.bind( self.__onSelItem )
		self.__pyPagesPanel.pyBtnInc.onLClick.bind( self.__onShowNextPage, True )
		self.__pyPagesPanel.onDrawItem.bind( self.__onDrawItem )
		self.__pyPagesPanel.selectable = True
		self.__pyPagesPanel.viewSize = 6, 1							# 6行1列

		self.__initComboBoxs( panel )
		self.__initViewItems()

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pySearchBtn, "commissionsale:GoodsPanel", "btnSearch" )
		labelGather.setPyBgLabel( self.__pyBuyBtn, "commissionsale:GoodsPanel", "btnBuy" )
		labelGather.setLabel( panel.dObj, "commissionsale:GoodsPanel", "stLVRange" )
		labelGather.setLabel( panel.rObj, "commissionsale:GoodsPanel", "stSplit" )
		labelGather.setLabel( panel.stObj, "commissionsale:GoodsPanel", "stOwnMoney" )


	def __registerTriggers( self ) :
		self.__triggers["ON_RECEIVE_COMMISSION_GOODS_INFO"] = self.__onReceiveGoodsInfo
		self.__triggers["ON_REMOVE_COMMISSION_GOODS"] = self.__onRemoveGoods
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __desregisterTriggers( self ) :
		for trigger in self.__triggers :
			ECenter.unregisterEvent( trigger, self )

	def __initComboBoxs( self, panel ) :
		"""
		初始化ComboBox，每个ComboBox的内容是固定的，仅供选择作为
		查找条件
		"""
		tempDict = { "cbMR": (
						("cbMR_All", None ),
						("cbMR_Warrior", csconst.TI_SHOU_CLASS_FIGHTER ),
						("cbMR_Swordman", csconst.TI_SHOU_CLASS_SWORDMAN ),
						("cbMR_Archer", csconst.TI_SHOU_CLASS_ARCHER ),
						("cbMR_Magician", csconst.TI_SHOU_CLASS_MAGE ),
						),
					"cbTY": (
						("cbTY_All", None ),
						("cbTY_Weapon", csconst.TI_SHOU_WEAPON ),
						("cbTY_Armour", csconst.TI_SHOU_ARMOR ),
						("cbTY_Material", csconst.TI_SHOU_PRODUCE_STUFF ),
						("cbTY_Other", csconst.TI_SHOU_TYPE_NONE),		# csconst.ITEM_TYPE_OTHER
						),
					"cbQA" :{ Language.LANG_GBK:(("cbQA_All", None ),
							("cbQA_White", ItemTypeEnum.CQT_WHITE ),
							("cbQA_Blue", ItemTypeEnum.CQT_BLUE ),
							("cbQA_Yellow", ItemTypeEnum.CQT_GOLD ),
							("cbQA_Pink", ItemTypeEnum.CQT_PINK ),
							("cbQA_Green", ItemTypeEnum.CQT_GREEN )),
							Language.LANG_BIG5:(("cbQA_All", None ),
							("cbQA_White", ItemTypeEnum.CQT_WHITE ),
							("cbQA_Green", ItemTypeEnum.CQT_BLUE ),
							("cbQA_Blue", ItemTypeEnum.CQT_GOLD ),
							("cbQA_Purple", ItemTypeEnum.CQT_PINK ),
							("cbQA_Orange", ItemTypeEnum.CQT_GREEN ))
						}
					}
		self.__initCBID1 = BigWorld.callback( 0.2, Functor( self.__addCBGradual, tempDict ) )

	def __addCBGradual( self, tempDict ) :
		if len( tempDict ) == 0 : return
		panel = self.getGui()
		key, items = tempDict.popitem()
		cb = getattr( panel, key )
		pyCBBox = ODComboBox( cb, ODTextBox )
		pyCBBox.onViewItemInitialized.bind( self.__onInitCBXItem )
		pyCBBox.onDrawItem.bind( self.__onDrawCBXItem )
		pyCBBox.ownerDraw = True
		if key == "cbQA":
			items = items.get( Language.LANG, None )
		if items is None:return
		for name, content in items :
			label = labelGather.getText( "commissionsale:GoodsPanel", name )
			pyCBBox.addItem( ( label, content ) )
		pyCBBox.selIndex = 0
		self.__pyCBBoxs[key] = pyCBBox
		self.__initCBID1 = BigWorld.callback( 0.2, Functor( self.__addCBGradual, tempDict ) )

	def __initViewItems( self ) :
		"""
		慢速初始化
		"""
		pyViewItems = self.__pyPagesPanel.pyViewItems
		self.__initCBID2 = BigWorld.callback( 0.05, Functor( self.__addVIGradual, pyViewItems ) )

	def __addVIGradual( self, pyViewItems ) :
		if len( pyViewItems ) == 0 :
			self.__pySearchBtn.enable = True
			self.pyTabPage.enable = True
			self.pyBinder.initGradual()
			return
		pyViewItem = pyViewItems.pop()
		pyItem = GoodsItem()
		pyViewItem.pyItem = pyItem
		pyViewItem.addPyChild( pyItem )
		pyItem.left = 0
		pyItem.top = 0
		pyItem.refreshItem( pyViewItem )
		self.__initCBID2 = BigWorld.callback( 0.05, Functor( self.__addVIGradual, pyViewItems ) )

	def __onInitItem( self, pyViewItem ) :
		pass

	def __onDrawItem( self, pyViewItem ) :
		pyItem = getattr( pyViewItem, "pyItem", None )
		if pyItem is not None :
			pyItem.refreshItem( pyViewItem )

	def __onInitCBXItem( self, pyViewItem ) :
		"""初始化Combox的列表项"""
		staticText = hfUILoader.load( "guis/controls/odlistpanel/itemtext.gui" )
		pyText = StaticText( staticText )
		pyViewItem.addPyChild( pyText )
		pyText.r_left = uiFixer.toFixedX( pyText.r_left )
		pyText.middle = pyViewItem.height / 2
		pyViewItem.pyText = pyText

	def __onDrawCBXItem( self, pyViewItem ) :
		"""更新列表项"""
		pyText = pyViewItem.pyText
		listItem = pyViewItem.listItem
		pyText.text = listItem[0]
		pyPanel = pyViewItem.pyPanel
		pyViewItem.pyText.font = pyPanel.font
		if pyViewItem.selected :
			pyViewItem.pyText.color = pyPanel.itemSelectedForeColor			# 选中状态下的前景色
			pyViewItem.color = pyPanel.itemSelectedBackColor				# 选中状态下的背景色
		elif pyViewItem.highlight :
			pyViewItem.pyText.color = pyPanel.itemHighlightForeColor		# 高亮状态下的前景色
			pyViewItem.color = pyPanel.itemHighlightBackColor				# 高亮状态下的背景色
		else :
			pyViewItem.pyText.color = pyPanel.itemCommonForeColor
			pyViewItem.color = pyPanel.itemCommonBackColor

	def __onSelItem( self, selIndex ) :
		self.__pyBuyBtn.enable = selIndex != -1

	def __onSearch( self ) :
		"""
		开始查找
		"""
		self.__queryDict = {}
		self.__pyPagesPanel.clearItems()
		lowerLevel = self.__pyLowerLimit.text.strip()
		lowerLevel = ( lowerLevel != "" and ( int( lowerLevel ), ) or ( 0,) )[-1]
		upperLevel = self.__pyUpperLimit.text.strip()
		upperLevel = ( upperLevel != "" and ( int( upperLevel ), ) or ( 150,) )[-1]
		if lowerLevel > upperLevel :
			# "等级上限不能低于等级下限，请重新输入！"
			self.__showMessage( 0x02a1 )
			return
		if lowerLevel >= 0 :
			self.__queryDict[csconst.TISHOU_ITEM_LOWERLEVEL] = lowerLevel					# 等级下限
		if upperLevel >= 0 :
			self.__queryDict[csconst.TISHOU_ITEM_UPPERLEVEL] = upperLevel					# 等级上限
		keyWord = self.__pyKeyWord.text.strip()
		if keyWord != "" :
			self.__queryDict[csconst.TISHOU_ITEM_NAME] = keyWord							# 关键字
		QALimit = self.__pyCBBoxs["cbQA"].selItem[1]
		if QALimit is not None :
			self.__queryDict[csconst.TISHOU_ITEM_QALIMIT] = QALimit							# 品质限制
		metierLimit = self.__pyCBBoxs["cbMR"].selItem[1]
		if metierLimit is not None :
			self.__queryDict[csconst.TISHOU_ITEM_METIER] = metierLimit						# 职业需求限制
		typeLimit = self.__pyCBBoxs["cbTY"].selItem[1]
		if typeLimit is not None :
			self.__queryDict[csconst.TISHOU_ITEM_TYPELIMIT] = typeLimit						# 类型限制
		self.__currPage = 0																	# 从第一页开始
		self.__notifySearchResult( "begin" )
		BigWorld.player().base.queryTishouItemInfo( 0, self.__queryDict )

	def __onShowNextPage( self ) :
		pageIndex = self.__pyPagesPanel.pageIndex
		itemCount = ( self.__currPage + 1 ) * csconst.TISHOU_ITEM_INFO_QUERY_PAGE_SIZE
		passPage = math.ceil( itemCount / float( self.__pyPagesPanel.viewCount ) )
		if pageIndex > passPage - 2 :
			self.__currPage += 1
			BigWorld.player().base.queryTishouItemInfo( self.__currPage, self.__queryDict )

	def __onBuy( self ) :
		"""
		购买物品
		"""
		selItem = self.__pyPagesPanel.selItem
		if selItem is None : return
		player = BigWorld.player()
		cost = selItem[3][0]
		if cost > player.money :
			# "您的金钱不足以购买该物品！"
			self.__showMessage( 0x02a2 )
			return
		itemInfo = selItem[-1]
		player.cell.buyTSItemFromTishouMgr( itemInfo.uid, itemInfo.id, itemInfo.amount, selItem[3][0] )

	def __onTaxis( self, pyBtn ) :
		"""
		排序
		"""
		taxisIndex = pyBtn.taxisIndex
		taxisReverse = pyBtn.taxisReverse
		if taxisIndex == 4 :
			def cmpByQA( item1, item2 ) :
				if item1[ taxisIndex ] != item2[ taxisIndex ] :
					return cmp( item1[ taxisIndex ], item2[ taxisIndex ] )
				else :
					return cmp( item1[ 0 ], item2[ 0 ] )
			self.__pyPagesPanel.separateSort( cmp = cmpByQA, reverse = taxisReverse )
		else :
			self.__pyPagesPanel.separateSort( key = lambda item : item[taxisIndex], reverse = taxisReverse )

	def __updateMoney( self, money ) :
		self.__pyMoneyBox.money = money

	def __onReceiveGoodsInfo( self, merchantDBID, itemUID, baseItem, price, merchantName, shopName ) :
		"""
		接收到服务器发来的物品信息
		"""
		self.__notifySearchResult( "found" )
		player = BigWorld.player()
		itemInfo = ObjectItem( baseItem )
		itemName = itemInfo.name()
		itemLevel = itemInfo.reqLevel
		itemQA = itemInfo.quality
		playerLevel = player.level
		playerMoney = player.money
		levelColor = itemLevel> playerLevel and  ( 255,0,0,255 ) or (255,225,255,255)
		priceColor = price> playerMoney and  ( 255,0,0,255 ) or (255,225,255,255)
		rowInfo = ( ( itemName, QAColor( itemQA ) + (255.0,) ),					 # 物品名称
					( itemLevel, levelColor ),									 # 物品等级
					( merchantName, (255,255,255,255) ),						 # 店主名
					( price, priceColor ),								 # 价格
					itemQA,														 # 品质(为了方便排序而加的)
					itemInfo,													 # 物品信息
					)
		for index, goodsInfo in enumerate( self.__pyPagesPanel.items ) :		# 检查是否重复
			if itemUID == goodsInfo[-1].uid :
				self.__pyPagesPanel.updateItem( index, rowInfo )
				break
		else :
			self.__pyPagesPanel.addItem( rowInfo )

	def __onRemoveGoods( self, goodsUID ) :
		for index, goodsInfo in enumerate( self.__pyPagesPanel.items ) :
			if goodsUID == goodsInfo[-1].uid :
				self.__pyPagesPanel.removeItemOfIndex( index )
				break

	def __showMessage( self, msg ) :
		def query( result ) :
			self.__pyMsgBox = None
		if self.__pyMsgBox is not None :
			self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", MB_OK, query )

	def __notifySearchResult( self, step = "not found" ) :
		if step == "begin" :
			self.__pyDirText.visible = True
			self.__pyDirText.text = labelGather.getText( "commissionsale:GoodsPanel", "stClewSearching" )
			self.__dirCBID = BigWorld.callback( 2, self.__notifySearchResult )			# 2秒后未收到任何数据则默认没有匹配数据
		elif step == "found" :
			self.__pyDirText.visible = False
			if self.__dirCBID > 0 :
				BigWorld.cancelCallback( self.__dirCBID )
				self.__dirCBID = 0
		elif step == "not found" :
			self.__pyDirText.visible = True
			self.__pyDirText.text = labelGather.getText( "commissionsale:GoodsPanel", "stClewNotFound" )
		else :
			self.__pyDirText.visible = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def searchByMerchantName( self, merchantName ) :
		"""
		查找某个商人所有的寄售宠物
		"""
		self.__pyPagesPanel.clearItems()
		self.__currPage = 0
		self.__notifySearchResult( "begin" )
		self.__queryDict = {}
		self.__queryDict[csconst.TISHOU_OWNER_NAME] = merchantName
		BigWorld.player().base.queryTishouItemInfo( self.__currPage, self.__queryDict )

	def keyEventHandler( self, key, mods ) :
		if ( mods == 0 ) and ( key == KEY_RETURN  or key == KEY_NUMPADENTER ) :			# 如果按下了回车键
			if self.__pySearchBtn.enable :
				self.__onSearch()
				return True
		return False

	def isReady( self ) :
		return self.__pySearchBtn.enable

	def onEnterWorld( self ) :
		self.__updateMoney( BigWorld.player().money )

	def onRoleMoneyChanged( self, oldValue, newValue ) :
		self.__updateMoney( newValue )

	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )

	def dispose( self ) :
		TabPanel.dispose( self )
		self.__triggers = {}
		BigWorld.cancelCallback( self.__dirCBID )
		BigWorld.cancelCallback( self.__initCBID1 )
		BigWorld.cancelCallback( self.__initCBID2 )



class GoodsItem( HStatesTabEx ) :

	_GOODS_ITEM = None

	def __init__( self ) :
		if GoodsItem._GOODS_ITEM is None :
			GoodsItem._GOODS_ITEM = GUI.load( "guis/general/commissionsale/shopsviewer/goodsitem.gui" )
			uiFixer.firstLoadFix( GoodsItem._GOODS_ITEM )
		gui = util.copyGuiTree( GoodsItem._GOODS_ITEM )
		HStatesTabEx.__init__( self, gui )
		self.setExStatesMapping( UIState.MODE_R3C1 )

		self.__pyColItems = []
		self.__initialize( gui )

	def __initialize( self, gui ) :
		for i in xrange( 1, 4 ) :
			colItem = getattr( gui, "col_" + str( i ) )
			pyCItem = ColItem( colItem )
			self.__pyColItems.append( pyCItem )
		colItem = getattr( gui, "col_4" )
		pyCItem = MoneyCol( colItem )
		self.__pyColItems.append( pyCItem )

		self.__pyIcon = GoodsIcon( gui.item )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def refreshItem( self, pyViewItem ) :
		rowInfo = pyViewItem.pageItem
		if rowInfo is None :
			rowInfo = ( ( "", (255,255,255,255) ),
						( "", (255,255,255,255) ),
						( "", (255,255,255,255) ),
						( 0, (255,255,255,255) ),
						None,
						)
			pyViewItem.focus = False
		else :
			pyViewItem.focus = True
		for pyCItem, info in zip( self.__pyColItems, rowInfo ) :
			pyCItem.update( info )
		itemInfo = rowInfo[-1]
		if itemInfo != self.__pyIcon.itemInfo :							# 检查物品是否改变
			self.__pyIcon.update( itemInfo )
		if itemInfo is None :
			self.setStateView_( UIState.COMMON )
		elif pyViewItem.selected :
			self.setStateView_( UIState.PRESSED )
		elif pyViewItem.highlight :
			self.setStateView_( UIState.HIGHLIGHT )
		else :
			self.setStateView_( UIState.COMMON )


class ColItem( Control ) :

	def __init__( self, colItem, pyBinder = None ) :
		Control.__init__( self, colItem, pyBinder )
		self.focus = False
		self.crossFocus = True

		self.pyText_ = None
		self.initialize_( colItem )

	def initialize_( self, colItem ) :
		self.pyText_ = StaticText( colItem.lbText )
		self.pyText_.text = ""


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		if self.pyText_.left < 0 or self.pyText_.right > self.width :
			FullText.show( self, self.pyText_ )
		return Control.onMouseEnter_( self )

	def onMouseLeave_( self ) :
		FullText.hide()
		return Control.onMouseLeave_( self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, info ) :
		self.pyText_.text = info[0]
		self.pyText_.getGui().colour = info[1]
		if self.isMouseHit() and \
		( self.pyText_.left < 0 or self.pyText_.right > self.width ) :
			FullText.show( self, self.pyText_, False )


class MoneyCol( ColItem ) :

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initialize_( self, colItem ) :
		self.pyText_ = CSRichText( colItem.lbText )
		self.pyText_.align = "R"
		self.pyText_.autoNewline = False
		self.pyText_.text = ""


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, info ) :
		self.pyText_.text = utils.currencyToViewText( info[0] )
		self.pyText_.foreColor = info[1]
		if self.isMouseHit() and \
		( self.pyText_.left < 0 or self.pyText_.right > self.width ) :
			FullText.show( self, self.pyText_, False )


class GoodsIcon( PyGUI ) :

	def __init__( self, item ) :
		PyGUI.__init__( self, item )

		self.__initialize( item )
		self.update( None )

	def __initialize( self, item ) :
		self.__pyBOItem = BOItem( item.item )
		self.__pyBOItem.focus = False


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		self.__pyBOItem.update( itemInfo )
		quality = 0
		if itemInfo is not None :
			quality = itemInfo.quality
		util.setGuiState( self.getGui(), ( 4, 2 ), ItemQAColorMode[quality] )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	@property
	def itemInfo( self ) :
		return self.__pyBOItem.itemInfo


class ODTextBox( InputBox ) :

	def onItemSelectChanged_( self, index ) :
		"""
		选项改变时被调用
		"""
		pyCombo = self.pyComboBox
		self.text = "" if index < 0 else pyCombo.items[index][0]
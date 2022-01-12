# -*- coding: gb18030 -*-
#
## $Id: KitBag.py,v 1.71 2008-09-02 04:47:57 pengju Exp $


from bwdebug import *
import copy
from guis import *
import ItemTypeEnum
from LabelGather import labelGather
from guis.util import getGuiMapping
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.Control import Control
from guis.controls.ODComboBox import ODComboBox
from guis.controls.StaticText import StaticText
from guis.controls.StaticLabel import StaticLabel
from ItemPanel import BagWindow
from ItemPanel import ItemPanel
from KitbagItem import KitbagItem
import ItemTypeEnum as ItemType
from casketwindow.CasketWindow import CasketWindow
from Helper import courseHelper
import GUIFacade
from ItemsFactory import ObjectItem as ItemInfo
import event.EventCenter as ECenter
import csdefine
import csstatus
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from guis.general.kitbag.SplitBox import SplitBox
from guis.tooluis.passwordbox.PasswordWindow import PasswordWindow
import BigWorld
import reimpl_kitBag
from guis.OpIndicatorObj import OpIndicatorObj

class KitBag( Window, OpIndicatorObj ):

	drug_types = [ItemTypeEnum.ITEM_DRUG_ROLE_HP, ItemTypeEnum.ITEM_DRUG_ROLE_MP]
	catchWare_ids = [60201001, 60201023]

	def __init__( self ):
		wnd = self.__getGUI()
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		OpIndicatorObj.__init__( self )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
#		self.currentExpendBagID	= 0 #当前背包
		self.h_dockStyle = "RIGHT"					# 在屏幕上的水平停靠方式( hyw - 2008.06.20 )

		self.__triggers = {}
		self.__registerTriggers()
		self.__pyKitBags = {}  #背包面板
		self.__pyKitItems = {} #背包位
		self.__showKitBags = [] #显示的背包

		self.tempTotalItem = [] 	#所有的物品
		self.kitOrderFactor = {} 	#现有所有背包的容量
		self.combineItem = []		#[ (物品1，物品2), ..... ]
		self.desertItem = []		#[ 物品1, ..... ]
		self.sortItem = []			#[(源背包号，源位置索引，目的背包号，目的位置索引),...........]
		self.lastSortTime = 0
		self.tipItems = {}			# 互动型帮助提示
		self.__initialize( wnd )

		self.treasureOrder = 0		# 藏宝图的order


	@reimpl_kitBag.deco_guiKitBagGetGUI
	def __getGUI( self ):
		return GUI.load( "guis/general/kitbag/kitbag.gui" )

	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "KitBag:main", "lbTitle" )
#		labelGather.setLabel( wnd.optionText, "KitBag:main", "optionText" )
		self.__pyTxtGold = StaticText( wnd.goldPanel.lbPoint ) # 金元宝
		self.__pyTxtGold.text = ""
		self.__pyTxtSilver = StaticText( wnd.silverPanel.lbSilverPoint )	# 银元宝
		self.__pyTxtSilver.text = ""

		self.__pyTxtMoneyGold = StaticText( wnd.moneyPanel.lbGold )#金
		self.__pyTxtMoneyGold.text = ""

		self.__pyTxtMoneySilver = StaticText( wnd.moneyPanel.lbSilver ) #银
		self.__pyTxtMoneySilver.text = ""

		self.__pyTxtMoneyCopper = StaticText( wnd.moneyPanel.lbCopper ) #铜
		self.__pyTxtMoneyCopper.text = ""

		self.__pybtnSplit = Button( wnd.btnSplit ) #拆分按钮
		self.__pybtnSplit.setStatesMapping( UIState.MODE_R2C2 )
		self.__pybtnSplit.description = labelGather.getText( "KitBag:main", "splitText" )
		self.__pybtnSplit.onLClick.bind( self.__onSplit )
		self.__pybtnSplit.onMouseEnter.bind( self.__onMouseEnter )
		self.__pybtnSplit.onMouseLeave.bind( self.__onMouseLeave )
		self.__pybtnSplit.onLMouseDown.bind( self.__onMouseDown )

		self.__pyBtnLock = Button( wnd.btnLock ) #密码按钮
		self.__pyBtnLock.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnLock.description = labelGather.getText( "KitBag:main", "lockStatus" )
		self.__pyBtnLock.onLClick.bind( self.__onLockCode )
		self.__pyBtnLock.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyBtnLock.onMouseLeave.bind( self.__onMouseLeave )
		self.__pyBtnLock.onLMouseDown.bind( self.__onMouseDown )

		self.__pyUnlockBtn = Button( wnd.btnUnlock )
		self.__pyUnlockBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyUnlockBtn.description = labelGather.getText( "KitBag:main", "unLockStatus" )
		self.__pyUnlockBtn.onLClick.bind( self.__onUnlockCode )
		self.__pyUnlockBtn.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyUnlockBtn.onMouseLeave.bind( self.__onMouseLeave )
		self.__pyUnlockBtn.onLMouseDown.bind( self.__onMouseDown )

		self.__pyBtnVend = Button( wnd.btnVend )
		self.__pyBtnVend.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnVend.description = labelGather.getText( "KitBag:main", "vendText" )
		self.__pyBtnVend.scTag = "UI_TOGGLE_STALLAGE"
		self.__pyBtnVend.onLClick.bind( self.__onPlayerVend )
		self.__pyBtnVend.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyBtnVend.onMouseLeave.bind( self.__onMouseLeave )
		self.__pyBtnVend.onLMouseDown.bind( self.__onMouseDown )

		self.__pyDefPanel = ItemPanel( csdefine.KB_COMMON_ID, 42, wnd.itemsPanel ) #默认背包模板
		self.__pyKitBags[csdefine.KB_COMMON_ID] = self.__pyDefPanel

		self.pyCasketWnd = CasketWindow( csdefine.KB_CASKET_ID, self )
		self.__pyKitBags[csdefine.KB_CASKET_ID] = self.pyCasketWnd

		self.__pyBtnSort = HButtonEx( wnd.btnSort )
		self.__pyBtnSort.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnSort, "KitBag:main", "sortout" )		
		self.__pyBtnSort.onLClick.bind( self.__onPopSortMenu )

		# 增加引路蜂、自动寻路界面
		pyMenu = ContextMenu()
		pyMenuItem0 = DefMenuItem( labelGather.getText( "KitBag:main", "leadBee" ), MIStyle.COMMON )
		pyMenuItem0.handler =  self.__flyToSpacePosition
		pyMenuItem1 = DefMenuItem( labelGather.getText( "KitBag:main", "autoText" ), MIStyle.COMMON  )
		pyMenuItem1.handler =  self.__runToSpacePosition
		pySplitter = DefMenuItem( style = MIStyle.SPLITTER )
		pyMenu.pyItems.adds( [pyMenuItem0, pySplitter, pyMenuItem1] )
		pyMenu.onItemClick.bind( self.__onMenuItemClick )
		self.__pyCMenu = pyMenu
		
		self.__pySortMenu = ContextMenu()
		sortMaps = {0: labelGather.getText( "KitBag:main", "typeText" ),
				1: labelGather.getText( "KitBag:main", "qualityText" ),
				2: labelGather.getText( "KitBag:main", "priceText" ),
				3: labelGather.getText( "KitBag:main", "levelText" ),		
		}
		for index, sortText in sortMaps.items():
			pyMenuItem = DefMenuItem( sortText, MIStyle.COMMON )
			pyMenuItem.index = index
			self.__pySortMenu.pyItems.add( pyMenuItem )
		self.__pySortMenu.onItemClick.bind( self.__selectType )		
		self.__initKitbags( wnd )

	# ------------------------------------------------------------
	# private
	# ------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_TOGGLE_KITBAG"] = self.__toggleVisible
		self.__triggers["EVT_ON_TOGGLE_SUBKITBAGS"] = self.__toggleSubKitbags
		self.__triggers["EVT_ON_KITBAG_ADD_ITEM"] = self.__onAddItems
		self.__triggers["EVT_ON_UNWIELD_ADD_KITBAGITEM"] = self.__onAddUnwieldItems		#添加从装备栏中卸下到背包的装备
		#包裹相关操作
		self.__triggers["EVT_ON_KITBAG_ITEM_INFO_CHANGED"] = self.__onInfoChanged		#某个物品信息发生改变
		self.__triggers["EVT_ON_UNWIELD_TO_KITBAG"] = self.__onEquipUnwield				#当装备卸下到背包中
		self.__triggers["EVT_ON_UPDATE_PACK_ITEMS"] = self.__onupDatePackItem 			#被选中后的背包的物品显示
		self.__triggers["EVT_ON_UPDATE_PACK_ITEM"] = self.__onSetPackItem #设置背包位信息
		self.__triggers["EVT_ON_KITBAG_SET_CURRENT"] = self.__onSetCurrent #点击某个包裹位

		self.__triggers["EVT_ON_ROLE_GOLD_CHANGED"] = self.__onGoldChanged 		# 金元宝数量发生变化
		self.__triggers["EVT_ON_ROLE_SILVER_CHANGED"] = self.__onSilverChanged	# 银元宝数量发生变化
		self.__triggers["EVT_ON_ROLE_MONEY_CHANGED"] = self.__onMoneyChanged 	#金钱数量发生变化
		self.__triggers["EVT_ON_SWRAP_PACK_ITEMS"] = self.__onSwapKitBags		#背包位互换
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onRemoveItem
		self.__triggers["EVT_ON_WIELD_REMOVE_KITBAGITEM"] = self.__onWieldRemoveItem
		self.__triggers["EVT_ON_KITBAG_SWAP_ITEM"] = self.__onSwapItems
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onUpdateItems
		self.__triggers["EVT_ON_ITEM_COLOR_CHANGE"] = self.__itemColorChange #锁定物品并改变物品颜色

		self.__triggers["EVT_ON_BAGLOCK_FLAG_CHANGE"] = self.__onLockFlagChange
		self.__triggers["EVT_ON_BAGLOCK_TIME_CHANGE"] = self.__onLockTimeChange
		self.__triggers["EVT_ON_BAGLOCK_STATUAS_CHANGE"] = self.__onLockStatusChange

		self.__triggers["EVT_ON_SHOW_AUTO_FIND_PATH_MENU"] = self.__onShowAutoFindPathMenu		# 打开“引路蜂、自动寻路”菜单
		self.__triggers["EVT_ON_RESOLUTION_CHANGED"] = self.__onResolutionChanged

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	# ------------------------------------------------------------
	def __initKitbags( self, wnd ):
		"""
		初始化背包位
		"""
		for name, item in wnd.children:
			if "kitbag_" not in name: continue
			index = int( name.split( "_" )[1] )
			pyKitItem = KitbagItem( index, item )
			pyKitItem.update( None )
			self.__pyKitItems[index] = pyKitItem

	def __toggleVisible( self, isVisible = None ) :
#		self.clearIndications()							# 缓兵之计，先清掉旧的提示
		if isVisible is None :
			self.visible = not self.visible
		else :
			self.visible = isVisible
		if self.visible:
			rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_visible","kitBag" ) )
		else:
			self.clearIndications()

	def __toggleSubKitbags( self ) :
		"""
		显示/隐藏所有子背包
		"""
		pass

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

	def __onSetCurrent( self, currentID ):
		"""
		选择某个背包
		"""
		if currentID == csdefine.KB_CASKET_ID:
			self.clearIndications()
			return
		pyKitBag = self.__pyKitBags[currentID]
		if pyKitBag.visible: #如果背包已经打开，则将其关闭
			pyKitBag.hide()
			self.__layoutKits()
		else:
			self.__showKitBags.append( pyKitBag )
			self.__layoutKits()
		for kitID in self.__pyKitItems.iterkeys(): #设置背包位状态
			if kitID == csdefine.KB_CASKET_ID:
				continue
			if self.__pyKitBags.has_key( kitID ):
				if self.__pyKitBags[kitID].visible:
					self.__pyKitItems[kitID].cover.visible = True
				else:
					self.__pyKitItems[kitID].cover.visible = False
			else:continue

	def __onSetPackItem( self, kitbagID, itemInfo ):
		"""
		设置背包格物品信息（是背包，不是背包里面的物品）
		"""
		if self.__pyKitItems.has_key( kitbagID ): #在初始化的时候就包含了 有背包格框架信息
			self.__pyKitItems[kitbagID].update( itemInfo )
			if kitbagID == csdefine.KB_CASKET_ID: #如果是神机会匣不需要 没被选中的 遮片
				self.__pyKitItems[kitbagID].cover.visible = False

			if itemInfo is None:
				if kitbagID == csdefine.KB_CASKET_ID:
					try:
						casket = self.__pyKitBags[kitbagID]
					except:
						ERROR_MSG( "src(%i) Can't find kitCasket in kitbag %s" % ( BigWorld.player().id, csdefine.KB_CASKET_ID ) )
						return
					casket.hide()
					return
				else: #普通背包
					if self.__pyKitBags.has_key( kitbagID ):
						pykitBag = self.__pyKitBags.pop( kitbagID )
						if pykitBag in self.__showKitBags:
							self.__showKitBags.remove( pykitBag )
							self.__layoutKits()
						pykitBag.dispose()
			else:
				if kitbagID == csdefine.KB_CASKET_ID: #神机匣
					pyCasketBag = self.__pyKitItems[kitbagID]
#					toolbox.infoTip.hideOperationTips( 0x00a0 )
#					toolbox.infoTip.showOperationTips( 0x00a1, pyCasketBag )
					return
				else: #普通背包
					if self.__pyKitBags.has_key( kitbagID ): #如果背包已加载，取得背包信息
						pykitBag = self.__pyKitBags[kitbagID]
						if pykitBag.visible:
							self.__showKitBags.remove( pykitBag )
						pykitBag.dispose()
						del self.__pyKitBags[kitbagID]
					#else: #如果背包未加载，则加载背包信息
					maxSpace = itemInfo.query("kb_maxSpace") #得到背包的最大空间
					name = itemInfo.query("name") #得到背包的名字
					rows = (maxSpace-1) / csdefine.KB_MAX_COLUMN  + 1
					pyKitBag = BagWindow( kitbagID, maxSpace, pyBinder=self ) #加载背包信息
					pyKitBag.title = name
					self.__pyKitBags[kitbagID] = pyKitBag

	def __onAddItems( self, itemInfo ):
		player  = BigWorld.player()
		kitbagID = itemInfo.kitbagID
		orderID = itemInfo.orderID
		if self.__pyKitBags.has_key( kitbagID ):
			pyItem = self.__pyKitBags[kitbagID].getItem( orderID )
			if pyItem:
				pyItem.update( itemInfo )
		itemType = itemInfo.itemType
		if itemType == ItemTypeEnum.ITEM_WAREHOUSE_CASKET and \
		self.visible:
			pyCasketBag = self.__pyKitItems[csdefine.KB_CASKET_ID]
#			if not pyCasketBag.itemInfo:
#				toolbox.infoTip.showOperationTips( 0x00a0, pyCasketBag )

	def __onAddUnwieldItems( self, itemInfo ):
		"""
		增加一个从装备栏卸下的装备到背包中，单独强调是从装备栏中卸下的原因是从装备栏总卸下装备需要再背包的相应位置处显示闪烁效果
		"""
		player  = BigWorld.player()
		kitbagID = itemInfo.kitbagID
		orderID = itemInfo.orderID
		if self.__pyKitBags.has_key( kitbagID ):
			pyItem = self.__pyKitBags[kitbagID].getItem( orderID )
			pyItem.unwield_update( itemInfo )

	def __onInfoChanged( self, kitbagID, orderID, itemInfo ):
		if self.__pyKitBags.has_key( kitbagID ):
			pyItem = self.__pyKitBags[kitbagID].getItem( orderID )
			pyItem.update( itemInfo )

	def __onEquipUnwield( self, kitbagID, orderID, itemInfo ):
		"""
		找出相应的位置 跟新该格的物品的属性以及显示闪烁标志
		"""
		if self.__pyKitBags.has_key( kitbagID ):
			pyItem = self.__pyKitBags[kitbagID].getItem( orderID )
			pyItem.unwield_update( itemInfo )		#卸下某个物品到背包后更新该格的信息

	def __onupDatePackItem( self, kitbagID ): # 更新某个背包物品信息
		if self.__pyKitBags.has_key( kitbagID ):
			if kitbagID == csdefine.KB_CASKET_ID:
				if self.visible:
					if self.__pyKitBags[kitbagID].visible:
						self.__pyKitBags[kitbagID].hide()
						return
					self.__pyKitBags[kitbagID].show( self )

	def __clearPanel( self, kitbagID ):
		for kitID, itemsPanel in self.__pyKitBags.iteritems(): #遍历所有背包
			if kitbagID != kitID: #如果当前背包不等于传入背包
				if kitbagID == csdefine.KB_CASKET_ID or kitbagID == csdefine.KB_COMMON_ID:continue
				if kitID == csdefine.KB_CASKET_ID or kitID == csdefine.KB_COMMON_ID:continue
				if self.__pyKitItems[kitID].itemInfo != None:
					self.__pyKitItems[kitID].cover.visible = True
			else:
				self.__pyKitItems[kitID].cover.visible = False

	def __onGoldChanged( self, oldGold, newGold ):
		self.__pyTxtGold.text = str( newGold )

	def __onSilverChanged( self, oldValue, newValue ):
		"""
		"""
		DEBUG_MSG( "---->>>oldValue:%i,newValue:%i." % ( oldValue, newValue ) )
		self.__pyTxtSilver.text = str( newValue )
	
	def __onPopSortMenu( self ):
		self.__pySortMenu.popup( self.__pyBtnSort )
		self.__pySortMenu.top = self.__pyBtnSort.bottomToScreen
		self.__pySortMenu.center = self.__pyBtnSort.centerToScreen
		
	def __onMoneyChanged( self, oldMoney, newMoney ):
		gold = newMoney/10000
		sliver = ( newMoney/100 )%100
		copper = ( newMoney%100 )%100
		self.__pyTxtMoneyGold.text = str( gold )
		self.__pyTxtMoneySilver.text = str( sliver )
		self.__pyTxtMoneyCopper.text = str( copper )

	def __onRemoveItem( self, itemInfo ) :
		kitbagID = itemInfo.kitbagID
		index = itemInfo.orderID
		if self.__pyKitBags[kitbagID]:
			pyItem = self.__pyKitBags[kitbagID].getItem( index )
			if pyItem.isLocked == True: #如果物品被锁定，则解锁
				pyItem.unlock()
			pyItem.itemInfo.baseItem.unfreeze() # 物品被删后没有解冻，暂时这样解决
			pyItem.update( None )
		self.pyTopParent.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_visible","kitBag" ) )

	def __onWieldRemoveItem( self, itemInfo ) :
		kitbagID = itemInfo.kitbagID
		index = itemInfo.orderID
		if self.__pyKitBags[kitbagID]:
			pyItem = self.__pyKitBags[kitbagID].getItem( index )
			if pyItem.isLocked == True: #如果物品被锁定，则解锁
				pyItem.unlock()
			pyItem.itemInfo.baseItem.unfreeze() # 物品被删后没有解冻，暂时这样解决
			pyItem.unwield_update( None )

	def __onSwapItems( self, srcKitbagID, srcIndex, srcItemInfo, dstKitbagID, dstIndex, dstItemInfo ):
		srcItem = self.__pyKitBags[srcKitbagID].getItem( srcIndex )
		dstItem = self.__pyKitBags[dstKitbagID].getItem( dstIndex )
		for tipid, pyItem in self.tipItems.iteritems() :
			if pyItem == srcItem :
				toolbox.infoTip.moveOperationTips( tipid, dstItem.posToScreen )
				self.tipItems[tipid] = dstItem
			elif pyItem == dstItem :
				toolbox.infoTip.moveOperationTips( tipid, srcItem.posToScreen )
				self.tipItems[tipid] = srcItem
		if self.__pyKitBags.has_key( srcKitbagID ) and self.__pyKitBags[srcKitbagID]:
			if srcItemInfo == None:
				srcItem.update( srcItemInfo )
			else:
				ECenter.fireEvent( "EVT_ON_KITBAG_UPDATE_ITEM", srcItemInfo )
		if self.__pyKitBags.has_key( dstKitbagID ) and self.__pyKitBags[dstKitbagID]:
			if dstItemInfo == None:
				dstItem.update( dstItemInfo )
			else:
				ECenter.fireEvent( "EVT_ON_KITBAG_UPDATE_ITEM", dstItemInfo )
		if srcItem.isLocked == True and dstItem.isLocked == False: #如果拖动时物品的颜色是红的，则互相交换颜色
			srcItem.unlock()
			dstItem.lock()
		elif dstItem.isLocked == True and srcItem.isLocked == False: #如果拖动时物品的颜色是红的，则互相交换颜色
			dstItem.unlock()
			srcItem.lock()
		if srcKitbagID == csdefine.KB_CASKET_ID or dstKitbagID == csdefine.KB_CASKET_ID :
			ECenter.fireEvent( "EVT_ON_CASKET_ITEM_CHANGE", None )
		if self.sortItem:
			self.__doSwapItem()

	def __onUpdateItems( self, itemInfo ) :
		kitbagID = itemInfo.kitbagID  #背包ID
		index = itemInfo.orderID #物品所在背包的索引
		if self.__pyKitBags.has_key( kitbagID ) and self.__pyKitBags[kitbagID]:
			pyItem = self.__pyKitBags[kitbagID].getItem( index )
			pyItem.update( itemInfo )
			for item in self.__pyKitBags[kitbagID].getItems().itervalues():
				item.kitbagID = kitbagID
		if self.combineItem :
			self.__doCombineItem()
		else:
			self.__doSwapItem()
	def __onUpdateItemsForSwap( self, itemInfo, orderID ) :
		#kitbagID = itemInfo.kitbagID  #背包ID
		index = itemInfo.orderID #物品所在背包的索引
		pyItem = self.__pyKitBags[orderID].getItem( index )
		pyItem.update( itemInfo )
		pyItem.kitbagID = itemInfo.kitbagID

	def __onSwapKitBags( self, srckitID, srckitInfo, dstkitID, dstkitInfo ): # 交换背包
		#SRC 非当前  DST 当前
		#SRC 变成当前  DST 变成非当前
		distVisible = False
		srcVisible = False
		if self.__pyKitBags.has_key(srckitID) and self.__pyKitBags[srckitID]:
			pyKitBag = self.__pyKitBags.pop( srckitID )
			srcVisible = pyKitBag.visible
			if pyKitBag in self.__showKitBags:
				self.__showKitBags.remove( pyKitBag )
			pyKitBag.dispose()
		if srckitInfo:
			if self.__pyKitBags.has_key(dstkitID) and self.__pyKitBags[dstkitID]:
				pyKitBag = self.__pyKitBags.pop( dstkitID )
				distVisible = pyKitBag.visible
				if pyKitBag in self.__showKitBags:
					self.__showKitBags.remove( pyKitBag )
				pyKitBag.dispose()
		self.__onSetPackItem( dstkitID, dstkitInfo )
		if distVisible:
			GUIFacade.upDateKitBagItems( dstkitID )
		self.__onSetPackItem( srckitID, srckitInfo )
		if srcVisible:
			GUIFacade.upDateKitBagItems( srckitID )

	def __layoutKits( self ):
		"""
		排序背包
		"""
		for index, pyKitBag in enumerate( self.__showKitBags ):
			if index > 0:
				pyKitBag.top = self.__showKitBags[index - 1].bottom - 5.0
			else:
				pyKitBag.top = self.top
			pyKitBag.right = self.left
			pyKitBag.show( self )
	
	

	def __onLockFlagChange( self, flag ):
		player = BigWorld.player()
		lockStatus = player.kitbagsLockerStatus
		if flag == 0:
			if lockStatus != 0:
				# "包裹密码已经成功设定，请牢记您的密码"
				showMessage( 0x03c1,"", MB_OK )
			else:
				# "包裹已经成功永久解锁"
				showMessage( 0x03c2,"", MB_OK )
				self.__pyUnlockBtn.visible = True
				self.__pyBtnLock.visible = False
			PasswordWindow.instance().hide()
		elif flag == 1:
			# "包裹密码已经成功修改，请牢记您的密码"
			showMessage( 0x03c3,"", MB_OK )
			PasswordWindow.instance().hide()
		elif flag == 2:
			# "您输入的密码不正确，请重新输入"
			showMessage( 0x03c4,"", MB_OK )
		elif flag == 3:
			# "您输入的旧密码不正确，请重新输入"
			showMessage( 0x03ca,"", MB_OK )
		elif flag == 4:
			# "背包上锁成功。"
			showMessage( 0x03c5, "", MB_OK )
			self.__pyUnlockBtn.visible = False
			self.__pyBtnLock.visible = True
		elif flag == 5:
			# "背包解锁成功。"
			showMessage( 0x03c6, "", MB_OK )
			self.__pyUnlockBtn.visible = True
			self.__pyBtnLock.visible = False
		#elif flag == 6 :			# 只有3秒锁定时间，没必要提示此信息。
			#showMessage( 0x03c7,"", MB_OK )
		elif flag == 7 :
			# "成功进行永久开锁，之前的密码已被清空。"
			showMessage( 0x03c8,"", MB_OK )

	def __onLockTimeChange( self, time ):
		if time > 0:
			# "您已经输入密码错误三次，请稍候再试"
			showMessage( 0x03c7,"", MB_OK )

	def __onLockStatusChange( self, status ):
		if status == 0:
			self.__pyBtnLock.visible = False
			self.__pyUnlockBtn.visible = True
		pswWindow = PasswordWindow.getInstance()
		if pswWindow is not None :
			pswWindow.updateLockStatus( status, self )

	def __itemColorChange( self, kitbagID, orderID, color = False ): #锁定物品并改变物品颜色
		pyItem = self.__pyKitBags[kitbagID].getItem( orderID )
		if color:
			itemInfo = pyItem.itemInfo
			if itemInfo is None:return
			type = itemInfo.baseItem.getType()
			if type in ItemType.EQUIP_TYPE_SET:
				pyItem.hideSuParticle()
			pyItem.lock()
		else:
			pyItem.unlock()

	def __onClose( self, pyBtn ):
		self.hide()
	# ------------------------------------------
	def __onLockCode( self ):
		player = BigWorld.player()
		lockStatus = player.kitbagsLockerStatus
		def operate( result, text ):
			if result == PassResult.LOCK:
				self.__doLock()
			if result == PassResult.UNLOCK:
				player.kitbags_unlock( text )
			if result == PassResult.FOREUNLOCK:
				player.kitbags_clearPassword( text )
		passwordWnd = PasswordWindow.instance()
		if not passwordWnd.visible:
			passwordWnd.show( operate, lockStatus, self )
		else:
			passwordWnd.hide()

	def __onUnlockCode( self ):
		player = BigWorld.player()
		lockStatus = player.kitbagsLockerStatus
		def operate( result, text ):
			if result == PassResult.LOCK:
				self.__doLock()
			if result == PassResult.UNLOCK:
				player.kitbags_unlock( text )
			if result == PassResult.FOREUNLOCK:
				player.kitbags_clearPassword( text )
		passwordWnd = PasswordWindow.instance()
		if not passwordWnd.visible:
			passwordWnd.show( operate, lockStatus, self )
		else:
			passwordWnd.hide()

	def __onMouseEnter( self, pyBtn ):
		if pyBtn is None:return
		dsp = pyBtn.description
		if hasattr( pyBtn, "scTag" ) :
			dsp = dsp % rds.shortcutMgr.getShortcutInfo( pyBtn.scTag ).shortcutString
		toolbox.infoTip.showItemTips( self, dsp )

	def __onMouseLeave( self ):
		toolbox.infoTip.hide()

	def __onMouseDown( self ):
		toolbox.infoTip.hide()

	def __onPlayerVend( self ):
		ECenter.fireEvent( "EVT_ON_TOGGLE_VENDWINDOW" )

	def __onSplit( self ):
		splitBox=SplitBox.instance()
		if not splitBox.visible:
			splitBox.show( self )
		else:
			splitBox.hide()

	def __doLock( self ):
		p = BigWorld.player()
		if p.si_myState != csdefine.TRADE_SWAP_DEFAULT:
			self.__showCancelTradeNotice() # 正在交易时上锁要给个提示，不在交易则直接上锁
		else:
			p.kitbags_lock()

	def __showCancelTradeNotice( self ):
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().kitbags_lock()
		# "给包裹上锁会导致交易取消,确定吗?"
		showMessage( 0x03c9, "", MB_OK_CANCEL, query, self )
		
	def __showOpenCasketWindowIndication( self, idtId, *args ):
		"""
		"""
		player = BigWorld.player()
		if  len(args) ==0 and player.kitbags.has_key( csdefine.KB_CASKET_ID ) and not self.pyCasketWnd.visible: #指引打开神机匣
			casketItem = self.__pyKitItems[ csdefine.KB_CASKET_ID ]
			toolbox.infoTip.showHelpTips( idtId, casketItem )
			self.addVisibleOpIdt( idtId )
		elif len( args ) == 1 :#指引玩家使用某物品
			itemID = args[0]
			item = player.findItemEx_( ( csdefine.KB_COMMON_ID,), itemID )
			if item is not None:
				uid = item.uid
				orderID = player.uid2order( uid )
				guiIndex = orderID - csdefine.KB_MAX_SPACE
				guiItem = self.__pyKitBags[ csdefine.KB_COMMON_ID ].getItem( guiIndex )
				toolbox.infoTip.showHelpTips( idtId, guiItem )
				self.addVisibleOpIdt( idtId )
		
	def _initOpIndicationHandlers( self ) :
		"""
		"""
		trigger = ( "gui_visible","kitBag" )
		condition = ( "quest_uncompleted", )
		idtIds = rds.opIndicator.idtIdsOfCmd( condition, trigger )
		for i in idtIds :
			self._opIdtHandlers[i] = self.__showOpenCasketWindowIndication

	
	# -----------------------------------------------------
	# public
	# -----------------------------------------------------
	def setPassWord( self, oldPassWord, newPassWord ):
		player = BigWorld.player()
		player.kitbags_setPassword( oldPassWord, newPassWord )

	def affirmOldWord( self, oldPassWord ):
		"""
		玩家确认旧密码,待定接口
		"""
		player = BigWorld.player()
		player.kitbag_afirmPassWord( oldPassWord )

	def onKitBagHide( self, kitBagID ): #某个背包关闭
		self.__pyKitItems[kitBagID].cover.visible = False
		if self.__pyKitBags.has_key( kitBagID ):
			pyKitBag = self.__pyKitBags[kitBagID]
			if pyKitBag in self.__showKitBags:
				self.__showKitBags.remove( pyKitBag )
				self.__layoutKits()

	def show( self ):
		player = BigWorld.player()
		lockStatus = player.kitbagsLockerStatus
		isUnLocked = lockStatus == 0 or lockStatus == 1
		self.__pyBtnLock.visible = not isUnLocked
		self.__pyUnlockBtn.visible = isUnLocked
		Window.show( self )
		self.__showUIOHTips()
		rds.helper.courseHelper.openWindow( "beibao_chuangkou" )

	def hide( self ):
		self.__showKitBags = [] #显示的背包
		for tipid in self.tipItems.iterkeys() :
			toolbox.infoTip.hideOperationTips( tipid )
		self.tipItems = {}
		toolbox.infoTip.hideOperationTips( 0x00a0 )
		toolbox.infoTip.hideOperationTips( 0x00a1 )
		Window.hide( self )

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.clearBag()
		self.hide()

	def getNormalKitBag( self ):
		return self.__pyKitItems[1]

	def getNormalPanel( self ):
		return self.__pyKitBags[1]

	def onCasketShow( self ):
		toolbox.infoTip.hideOperationTips( 0x00a1 )

	def clearBag( self ):
		for index, kitbag in self.__pyKitBags.items():
			if index != csdefine.KB_COMMON_ID and index != csdefine.KB_CASKET_ID:
				if kitbag:
					kitbag.dispose()
					self.__pyKitBags.pop( index )
		self.__pyKitBags[ csdefine.KB_COMMON_ID ].delItems()
		self.__pyKitBags[ csdefine.KB_CASKET_ID ].delItems()

		for Kitbag in self.__pyKitItems.itervalues():
			Kitbag.update( None )

	"""
	以下是自动排序和自动叠加的代码
	"""
	def __selectType( self, pyMenuItem ):
		"""
		noParam在函数中没有任何用处，但必须存在。
		否则ExtraEvents.py会报错
		"""
		"""
		判断前后排序时间，以免当玩家连续点击排序按钮
		"""
		if pyMenuItem is None:return
		selectedIndex = pyMenuItem.index
		if abs(BigWorld.stime() - self.lastSortTime) < 5:
			BigWorld.player().statusMessage( csstatus.GB_OPERATE_FREQUENTLY )
			return
		self.lastSortTime = BigWorld.stime()
		tempTotalItem = []
		self.kitOrderFactor = {}
		self.combineItem = []
		self.sortItem = []
		tempTotalItem = self.__getCommonKitBagItems()
		if tempTotalItem is None:return
		for item in tempTotalItem: #用于判断背包中是否有冻结物品，有则不能排序
			if item.isFrozen():
				BigWorld.player().statusMessage( csstatus.CIB_MSG_BAG_CANNOT_SORT )
				return
		desertItem = self.__getValidCombineItems( tempTotalItem )
		for i in desertItem:
			tempTotalItem.remove( i )
		if selectedIndex == 0:   # 类型
	 		self.__sortByID(tempTotalItem)
		elif selectedIndex == 1: # 品质
			self.__sortByQuality(tempTotalItem)
		elif selectedIndex==2:   # 价格
			self.__sortByPrice(tempTotalItem)
		else:               # 等级
			self.__sortByLevel(tempTotalItem)
		self.__getValidSortItem( tempTotalItem )
		if self.combineItem:
			self.__doCombineItem()
		else :
			self.__doSwapItem()

	def __getValidCombineItems( self,itemList ):
		"""
		算法思路：先去掉已到达叠加上限的物品，然后对itemList按id排序，
		这样相邻的两个物品如果id一样且绑定状态一样，则一定可以叠加。
		先取出第一个可以叠加的item1，
		然后从item后的队列中取出下一个可以和item叠加的元素item2，
		如果小于item1的叠加上限，则保留item1，重新取item2
		如果等于item1的叠加上限，则重新取item1，item2
		如果大于item1的叠加上限，则item1 = item2，重新取item2
		通过重复上面的过程可以获得所有叠加的元素对。
		该函数主要是取得可以叠加的物品，并存储在一个list中
		@param：itemlist
		@type： list
		return：排序不需要考虑的物品
		"""
		if not itemList:return []
		canStackableItems = []
		for item in itemList:		# 先把不能叠加的物品除掉
			if item.amount < item.getStackable():
				canStackableItems.append( item )
		if len( canStackableItems ) < 2 : return []
		desertItems = []
		self.__sortByID( canStackableItems )
		item = canStackableItems[0]			#取出itemlist中第一个可以叠加的元素
		(dstAmout, dstItem) = (item.getStackable()-item.amount,item)
		i=1 								#从第二个元素开始找
		while  ( i<len( canStackableItems ) ):
			item = canStackableItems[i]
			srcAmount = item.getStackable()-item.amount
			if dstItem.id != item.id or dstItem.isBinded() != item.isBinded():
				i = i+1
				(dstAmout, dstItem) = (srcAmount, item)
			else:
				self.combineItem.append( ( item.getKitID(),item.order%csdefine.KB_MAX_SPACE,
					dstItem.getKitID(),dstItem.order%csdefine.KB_MAX_SPACE ) )
				if dstAmout > item.amount:
					desertItems.append( item )
					dstAmout = dstAmout - item.amount
					i = i+1
				elif dstAmout < item.amount:
					dstAmout = item.getStackable()-(item.amount - dstAmout)
					(dstAmout, dstItem) = (srcAmount, item)
					i = i+1
				else:
					desertItems.append( item )
					if i+2 < len( canStackableItems ):
						next = canStackableItems[i+1]
						(dstAmout, dstItem) = ( next.getStackable()-next.amount,next )
						i = i+2
					else:
						break
		return desertItems

	def __doCombineItem(self):
		"""
		每次从self.combineItem取出一对要叠加的item进行叠加
		当self.combineItem为空时返回
		"""
		if not self.combineItem:
			return
		(a,b,c,d) = self.combineItem.pop(0)
		BigWorld.player().combineItem(a,b,c,d)

	def __getCommonKitBagItems(self):
		#获取现有背包中的物品和每个背包的最大容量
		if not rds.statusMgr.isInWorld():return
		temp = []
		player = BigWorld.player()
		kitbagDict = player.kitbags
		commKitBagIDs=[ kitID for kitID in kitbagDict if kitID in range(csdefine.KB_COMMON_ID,csdefine.KB_CASKET_ID)]
		for kitbagID in commKitBagIDs:
			self.kitOrderFactor[kitbagID] = kitbagDict[ kitbagID ].query("kb_maxSpace")
			for item in player.getItems( kitbagID ):
				temp.append( copy.copy( item ) )
				#temp.extend( player.getItems(kitbagID) )
		return temp

	def __sortByID( self, itemList ):
		"""
		按类型排序
		"""
		def func( item1, item2 ):
			if item1.id == item2.id:
				return cmp( item1.isBinded(), item2.isBinded() )
			else:
				return cmp(item1.id, item2.id)
		itemList.sort( cmp = func )

	def __sortByQuality( self, itemList ):
		"""
		按品质从高到低排序；同品质按等级从高到低排序；同品质、等级，按id排序。
		"""
		def func( item1, item2 ):
			if item1.getQuality() == item2.getQuality() and item1.getLevel() == item2.getLevel():
				return cmp( item2.id, item1.id )	# item2在前的原因是：按id排序需从低到高排，和品质、级别正相反。
			elif item1.getQuality() == item2.getQuality():
				return cmp( item2.getLevel(), item1.getLevel() )
			else:
				return cmp( item2.getQuality(), item1.getQuality() )
		itemList.sort( cmp = func )

	def __sortByPrice( self, itemList ):
		"""
		按价格从高到低排序；同价格按等级从高到低排序；同价格、等级，按id排序。
		"""
		def func( item1, item2 ):
			if item1.getPrice() == item2.getPrice() and item1.getLevel() == item2.getLevel():
				return cmp( item2.id, item1.id )	# item2在前的原因是：按id排序需从低到高排，和品质、级别正相反。
			elif item1.getPrice() == item2.getPrice():
				return cmp( item2.getLevel(), item1.getLevel() )
			else:
				return cmp( item2.getPrice(), item1.getPrice() )
		itemList.sort( cmp = func )


	def __sortByLevel( self, itemList ):
		"""
		按等级从高到低排序；同等级按品质从高到低排序；同等级、品质，按id排序。
		"""
		def func( item1, item2 ):
			if item1.getLevel() == item2.getLevel() and item1.getQuality() == item2.getQuality():
				return cmp( item2.id, item1.id )	# item2在前的原因是：按id排序需从低到高排，和品质、级别正相反。
			elif item1.getLevel() == item2.getLevel():
				return cmp( item2.getQuality(), item1.getQuality() )
			else:
				return cmp( item2.getLevel(), item1.getLevel() )
		itemList.sort( cmp = func )

	def __doSwapItem( self ):
		if not self.sortItem:
			return
		(srcKitOrder,srcOrder,dstKitOrder,dstOrder) = self.sortItem.pop( 0 )
		srcItem = BigWorld.player().getItem_( srcKitOrder * csdefine.KB_MAX_SPACE + srcOrder )
		dstItem = BigWorld.player().getItem_( dstKitOrder * csdefine.KB_MAX_SPACE + dstOrder )
		if  dstItem is not None and srcItem.id == dstItem.id:
			BigWorld.player().cell.swapItem( srcKitOrder * csdefine.KB_MAX_SPACE + srcOrder, dstKitOrder * csdefine.KB_MAX_SPACE + dstOrder )
		else:
			BigWorld.player().swapItem( srcKitOrder, srcOrder, dstKitOrder, dstOrder )

	def __getValidSortItem( self,itemList ):
		srcOrder      = -1
		srcKitOrder   = -1
		dstKitOrder   = -1
		dstOrder      = -1
		if not itemList:
			return
		while itemList:
			(dstKitOrder,dstOrder) = self.__getKitOrder( itemList )
			srcItem = itemList.pop()
			srcOrder = srcItem.order%csdefine.KB_MAX_SPACE
			srcKitOrder = srcItem.getKitID()
			if ( srcKitOrder, srcOrder ) != ( dstKitOrder, dstOrder ):
				self.sortItem.append( ( srcKitOrder, srcOrder, dstKitOrder, dstOrder ) )
			#模拟真实的排序过程
			srcItem.order = dstKitOrder * csdefine.KB_MAX_SPACE + dstOrder
			for i in itemList:
				if i.order == dstKitOrder * csdefine.KB_MAX_SPACE + dstOrder:
					i.order = srcKitOrder * csdefine.KB_MAX_SPACE + srcOrder
					break

	def __getKitOrder( self, itemList ):
		#根据总的物品数计算物品的背包号和在背包中的索引
		length = len( itemList )
		temp=0					#前i个背包的总容量
		tempOrder = length 		#物品新背包位的变量
		for kit, i in self.kitOrderFactor.iteritems():
			temp += i
			if length <= temp:
				return (kit,tempOrder-1)
			else:
				tempOrder -= i
		return (-1,-1)

	def __onMenuItemClick( self, pyItem ) :
		pyItem.handler()

	def __flyToSpacePosition( self ):
		"""
		"""
		player = BigWorld.player()
		items = []
		items = player.findItemsByIDFromNKCK( 50101003 )
		if items == []:
			items = player.findItemsByIDFromNKCK( 50101002 )
		if items == []:
			player.statusMessage( csstatus.ROLE_HAS_NOT_FIY_ITEM )
			return
		if not player.getState() == csdefine.ENTITY_STATE_FIGHT:
			player.stopMove()									# 必须先停止移动，以保证追踪目标不被清空
			player.cell.flyToSpacePosition( self.treasureOrder, items[0].order )
		else:
			player.statusMessage( csstatus.SKILL_USE_ITEM_WHILE_FIGHTING )

	def __runToSpacePosition( self ):
		"""
		"""
		player = BigWorld.player()
		treasure_item = player.getItem_( self.treasureOrder )
		treasureSpace = treasure_item.query( "treasure_space", "" )		# 取出藏宝图中的地图信息
		treasurePosStr = treasure_item.query( "treasure_position", None )# 取出藏宝图中的坐标信息
		treasurePos = eval( treasurePosStr )
		player.autoRun( treasurePos, 8, treasureSpace )

	def __onShowAutoFindPathMenu( self, order ):
		"""
		"""
		self.treasureOrder = order
		self.__pyCMenu.popup( self )

	def __onResolutionChanged( self, preReso ):
		"""
		分辨率改变
		"""
		self.__layoutKits()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __showUIOHTips( self ) :
		pass
#		self.tipItems = self.__searchOHItems()
#		for tipid, pyItem in self.tipItems.items() :
#			if not toolbox.infoTip.showOperationTips( tipid, pyItem ) :
#				del self.tipItems[ tipid ]

	def __searchOHItems( self ) :
		"""
		查找需要显示提示的物品
		"""
		player = BigWorld.player()
		def wieldEquip( baseItem ) :
			"""
			检测是否可装备物品
			"""
			return baseItem.isEquip() and baseItem.canWield( player )

		def wieldVehicle( baseItem ) :
			"""
			检测是否可使用的坐骑
			"""
			if baseItem.getType() == ItemTypeEnum.ITEM_SYSTEM_VEHICLE \
				and baseItem.getReqLevel() <= player.level :
					return True
			return False

		def useDrug( baseItem ) :
			"""
			检测是否可使用的药品
			"""
			if baseItem.getType() in \
				[ ItemTypeEnum.ITEM_DRUG_ROLE_HP, ItemTypeEnum.ITEM_DRUG_ROLE_MP ] \
				and baseItem.getReqLevel() <= player.level :
					return True
			return False

		def useCatcher( baseItem ) :
			"""
			检测是否可使用的捕兽器
			"""
			return baseItem.id in [ 60201023, 60201001, 60201050 ] \
			and baseItem.getReqLevel() <= player.level

		def useCasket( baseItem ) :
			"""
			检测是否是神机匣
			"""
			return baseItem.id == 70101008

		tipItems = {}
		pyItems = self.__pyDefPanel.getItems()
		for pyItem in pyItems.itervalues() :
			if pyItem.itemInfo is None : continue
			if wieldEquip( pyItem.itemInfo.baseItem ) :
				if 0x0050 not in tipItems :
					tipItems[ 0x0050 ] = pyItem
			elif wieldVehicle( pyItem.itemInfo.baseItem ) :
				if 0x0044 not in tipItems :
					tipItems[ 0x0044 ] = pyItem
			elif useDrug( pyItem.itemInfo.baseItem ) :
				if 0x0051 not in tipItems :
					tipItems[ 0x0051 ] = pyItem
			elif useCatcher( pyItem.itemInfo.baseItem ) :
				if 0x0052 not in tipItems :
					tipItems[ 0x0052 ] = pyItem
			elif useCasket( pyItem.itemInfo.baseItem ) :
				if 0x00a0 not in tipItems :
					pyCasketBag = self.__pyKitItems[csdefine.KB_CASKET_ID]
					if pyCasketBag.itemInfo is None :
						tipItems[ 0x00a0 ] = pyCasketBag
		return tipItems

	# ----------------------------------------------------------------
	# protected
	# ---------------------------------------------------------------
	def onMove_( self, dx, dy ) :
		self.relocateIndications()
#		for tipid, pyItem in self.tipItems.iteritems() :
#			toolbox.infoTip.moveOperationTips( tipid, pyItem.posToScreen )
#		toolbox.infoTip.moveOperationTips( 0x00a0 )
#		toolbox.infoTip.moveOperationTips( 0x00a1 )


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _setPos( self, ( left, top ) ) :
		Window._setPos( self, ( left, top ) )
#		for tipid, pyItem in self.tipItems.iteritems() :
#			toolbox.infoTip.moveOperationTips( tipid, pyItem.posToScreen )
#		toolbox.infoTip.moveOperationTips( 0x00a0 )
#		toolbox.infoTip.moveOperationTips( 0x00a1 )

	pos = property( Window._getPos, _setPos )
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
#		self.currentExpendBagID	= 0 #��ǰ����
		self.h_dockStyle = "RIGHT"					# ����Ļ�ϵ�ˮƽͣ����ʽ( hyw - 2008.06.20 )

		self.__triggers = {}
		self.__registerTriggers()
		self.__pyKitBags = {}  #�������
		self.__pyKitItems = {} #����λ
		self.__showKitBags = [] #��ʾ�ı���

		self.tempTotalItem = [] 	#���е���Ʒ
		self.kitOrderFactor = {} 	#�������б���������
		self.combineItem = []		#[ (��Ʒ1����Ʒ2), ..... ]
		self.desertItem = []		#[ ��Ʒ1, ..... ]
		self.sortItem = []			#[(Դ�����ţ�Դλ��������Ŀ�ı����ţ�Ŀ��λ������),...........]
		self.lastSortTime = 0
		self.tipItems = {}			# �����Ͱ�����ʾ
		self.__initialize( wnd )

		self.treasureOrder = 0		# �ر�ͼ��order


	@reimpl_kitBag.deco_guiKitBagGetGUI
	def __getGUI( self ):
		return GUI.load( "guis/general/kitbag/kitbag.gui" )

	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "KitBag:main", "lbTitle" )
#		labelGather.setLabel( wnd.optionText, "KitBag:main", "optionText" )
		self.__pyTxtGold = StaticText( wnd.goldPanel.lbPoint ) # ��Ԫ��
		self.__pyTxtGold.text = ""
		self.__pyTxtSilver = StaticText( wnd.silverPanel.lbSilverPoint )	# ��Ԫ��
		self.__pyTxtSilver.text = ""

		self.__pyTxtMoneyGold = StaticText( wnd.moneyPanel.lbGold )#��
		self.__pyTxtMoneyGold.text = ""

		self.__pyTxtMoneySilver = StaticText( wnd.moneyPanel.lbSilver ) #��
		self.__pyTxtMoneySilver.text = ""

		self.__pyTxtMoneyCopper = StaticText( wnd.moneyPanel.lbCopper ) #ͭ
		self.__pyTxtMoneyCopper.text = ""

		self.__pybtnSplit = Button( wnd.btnSplit ) #��ְ�ť
		self.__pybtnSplit.setStatesMapping( UIState.MODE_R2C2 )
		self.__pybtnSplit.description = labelGather.getText( "KitBag:main", "splitText" )
		self.__pybtnSplit.onLClick.bind( self.__onSplit )
		self.__pybtnSplit.onMouseEnter.bind( self.__onMouseEnter )
		self.__pybtnSplit.onMouseLeave.bind( self.__onMouseLeave )
		self.__pybtnSplit.onLMouseDown.bind( self.__onMouseDown )

		self.__pyBtnLock = Button( wnd.btnLock ) #���밴ť
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

		self.__pyDefPanel = ItemPanel( csdefine.KB_COMMON_ID, 42, wnd.itemsPanel ) #Ĭ�ϱ���ģ��
		self.__pyKitBags[csdefine.KB_COMMON_ID] = self.__pyDefPanel

		self.pyCasketWnd = CasketWindow( csdefine.KB_CASKET_ID, self )
		self.__pyKitBags[csdefine.KB_CASKET_ID] = self.pyCasketWnd

		self.__pyBtnSort = HButtonEx( wnd.btnSort )
		self.__pyBtnSort.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnSort, "KitBag:main", "sortout" )		
		self.__pyBtnSort.onLClick.bind( self.__onPopSortMenu )

		# ������·�䡢�Զ�Ѱ·����
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
		self.__triggers["EVT_ON_UNWIELD_ADD_KITBAGITEM"] = self.__onAddUnwieldItems		#��Ӵ�װ������ж�µ�������װ��
		#������ز���
		self.__triggers["EVT_ON_KITBAG_ITEM_INFO_CHANGED"] = self.__onInfoChanged		#ĳ����Ʒ��Ϣ�����ı�
		self.__triggers["EVT_ON_UNWIELD_TO_KITBAG"] = self.__onEquipUnwield				#��װ��ж�µ�������
		self.__triggers["EVT_ON_UPDATE_PACK_ITEMS"] = self.__onupDatePackItem 			#��ѡ�к�ı�������Ʒ��ʾ
		self.__triggers["EVT_ON_UPDATE_PACK_ITEM"] = self.__onSetPackItem #���ñ���λ��Ϣ
		self.__triggers["EVT_ON_KITBAG_SET_CURRENT"] = self.__onSetCurrent #���ĳ������λ

		self.__triggers["EVT_ON_ROLE_GOLD_CHANGED"] = self.__onGoldChanged 		# ��Ԫ�����������仯
		self.__triggers["EVT_ON_ROLE_SILVER_CHANGED"] = self.__onSilverChanged	# ��Ԫ�����������仯
		self.__triggers["EVT_ON_ROLE_MONEY_CHANGED"] = self.__onMoneyChanged 	#��Ǯ���������仯
		self.__triggers["EVT_ON_SWRAP_PACK_ITEMS"] = self.__onSwapKitBags		#����λ����
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onRemoveItem
		self.__triggers["EVT_ON_WIELD_REMOVE_KITBAGITEM"] = self.__onWieldRemoveItem
		self.__triggers["EVT_ON_KITBAG_SWAP_ITEM"] = self.__onSwapItems
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onUpdateItems
		self.__triggers["EVT_ON_ITEM_COLOR_CHANGE"] = self.__itemColorChange #������Ʒ���ı���Ʒ��ɫ

		self.__triggers["EVT_ON_BAGLOCK_FLAG_CHANGE"] = self.__onLockFlagChange
		self.__triggers["EVT_ON_BAGLOCK_TIME_CHANGE"] = self.__onLockTimeChange
		self.__triggers["EVT_ON_BAGLOCK_STATUAS_CHANGE"] = self.__onLockStatusChange

		self.__triggers["EVT_ON_SHOW_AUTO_FIND_PATH_MENU"] = self.__onShowAutoFindPathMenu		# �򿪡���·�䡢�Զ�Ѱ·���˵�
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
		��ʼ������λ
		"""
		for name, item in wnd.children:
			if "kitbag_" not in name: continue
			index = int( name.split( "_" )[1] )
			pyKitItem = KitbagItem( index, item )
			pyKitItem.update( None )
			self.__pyKitItems[index] = pyKitItem

	def __toggleVisible( self, isVisible = None ) :
#		self.clearIndications()							# ����֮�ƣ�������ɵ���ʾ
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
		��ʾ/���������ӱ���
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

	def __onSetCurrent( self, currentID ):
		"""
		ѡ��ĳ������
		"""
		if currentID == csdefine.KB_CASKET_ID:
			self.clearIndications()
			return
		pyKitBag = self.__pyKitBags[currentID]
		if pyKitBag.visible: #��������Ѿ��򿪣�����ر�
			pyKitBag.hide()
			self.__layoutKits()
		else:
			self.__showKitBags.append( pyKitBag )
			self.__layoutKits()
		for kitID in self.__pyKitItems.iterkeys(): #���ñ���λ״̬
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
		���ñ�������Ʒ��Ϣ���Ǳ��������Ǳ����������Ʒ��
		"""
		if self.__pyKitItems.has_key( kitbagID ): #�ڳ�ʼ����ʱ��Ͱ����� �б���������Ϣ
			self.__pyKitItems[kitbagID].update( itemInfo )
			if kitbagID == csdefine.KB_CASKET_ID: #����������ϻ����Ҫ û��ѡ�е� ��Ƭ
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
				else: #��ͨ����
					if self.__pyKitBags.has_key( kitbagID ):
						pykitBag = self.__pyKitBags.pop( kitbagID )
						if pykitBag in self.__showKitBags:
							self.__showKitBags.remove( pykitBag )
							self.__layoutKits()
						pykitBag.dispose()
			else:
				if kitbagID == csdefine.KB_CASKET_ID: #���ϻ
					pyCasketBag = self.__pyKitItems[kitbagID]
#					toolbox.infoTip.hideOperationTips( 0x00a0 )
#					toolbox.infoTip.showOperationTips( 0x00a1, pyCasketBag )
					return
				else: #��ͨ����
					if self.__pyKitBags.has_key( kitbagID ): #��������Ѽ��أ�ȡ�ñ�����Ϣ
						pykitBag = self.__pyKitBags[kitbagID]
						if pykitBag.visible:
							self.__showKitBags.remove( pykitBag )
						pykitBag.dispose()
						del self.__pyKitBags[kitbagID]
					#else: #�������δ���أ�����ر�����Ϣ
					maxSpace = itemInfo.query("kb_maxSpace") #�õ����������ռ�
					name = itemInfo.query("name") #�õ�����������
					rows = (maxSpace-1) / csdefine.KB_MAX_COLUMN  + 1
					pyKitBag = BagWindow( kitbagID, maxSpace, pyBinder=self ) #���ر�����Ϣ
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
		����һ����װ����ж�µ�װ���������У�����ǿ���Ǵ�װ������ж�µ�ԭ���Ǵ�װ������ж��װ����Ҫ�ٱ�������Ӧλ�ô���ʾ��˸Ч��
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
		�ҳ���Ӧ��λ�� ���¸ø����Ʒ�������Լ���ʾ��˸��־
		"""
		if self.__pyKitBags.has_key( kitbagID ):
			pyItem = self.__pyKitBags[kitbagID].getItem( orderID )
			pyItem.unwield_update( itemInfo )		#ж��ĳ����Ʒ����������¸ø����Ϣ

	def __onupDatePackItem( self, kitbagID ): # ����ĳ��������Ʒ��Ϣ
		if self.__pyKitBags.has_key( kitbagID ):
			if kitbagID == csdefine.KB_CASKET_ID:
				if self.visible:
					if self.__pyKitBags[kitbagID].visible:
						self.__pyKitBags[kitbagID].hide()
						return
					self.__pyKitBags[kitbagID].show( self )

	def __clearPanel( self, kitbagID ):
		for kitID, itemsPanel in self.__pyKitBags.iteritems(): #�������б���
			if kitbagID != kitID: #�����ǰ���������ڴ��뱳��
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
			if pyItem.isLocked == True: #�����Ʒ�������������
				pyItem.unlock()
			pyItem.itemInfo.baseItem.unfreeze() # ��Ʒ��ɾ��û�нⶳ����ʱ�������
			pyItem.update( None )
		self.pyTopParent.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_visible","kitBag" ) )

	def __onWieldRemoveItem( self, itemInfo ) :
		kitbagID = itemInfo.kitbagID
		index = itemInfo.orderID
		if self.__pyKitBags[kitbagID]:
			pyItem = self.__pyKitBags[kitbagID].getItem( index )
			if pyItem.isLocked == True: #�����Ʒ�������������
				pyItem.unlock()
			pyItem.itemInfo.baseItem.unfreeze() # ��Ʒ��ɾ��û�нⶳ����ʱ�������
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
		if srcItem.isLocked == True and dstItem.isLocked == False: #����϶�ʱ��Ʒ����ɫ�Ǻ�ģ����ཻ����ɫ
			srcItem.unlock()
			dstItem.lock()
		elif dstItem.isLocked == True and srcItem.isLocked == False: #����϶�ʱ��Ʒ����ɫ�Ǻ�ģ����ཻ����ɫ
			dstItem.unlock()
			srcItem.lock()
		if srcKitbagID == csdefine.KB_CASKET_ID or dstKitbagID == csdefine.KB_CASKET_ID :
			ECenter.fireEvent( "EVT_ON_CASKET_ITEM_CHANGE", None )
		if self.sortItem:
			self.__doSwapItem()

	def __onUpdateItems( self, itemInfo ) :
		kitbagID = itemInfo.kitbagID  #����ID
		index = itemInfo.orderID #��Ʒ���ڱ���������
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
		#kitbagID = itemInfo.kitbagID  #����ID
		index = itemInfo.orderID #��Ʒ���ڱ���������
		pyItem = self.__pyKitBags[orderID].getItem( index )
		pyItem.update( itemInfo )
		pyItem.kitbagID = itemInfo.kitbagID

	def __onSwapKitBags( self, srckitID, srckitInfo, dstkitID, dstkitInfo ): # ��������
		#SRC �ǵ�ǰ  DST ��ǰ
		#SRC ��ɵ�ǰ  DST ��ɷǵ�ǰ
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
		���򱳰�
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
				# "���������Ѿ��ɹ��趨�����μ���������"
				showMessage( 0x03c1,"", MB_OK )
			else:
				# "�����Ѿ��ɹ����ý���"
				showMessage( 0x03c2,"", MB_OK )
				self.__pyUnlockBtn.visible = True
				self.__pyBtnLock.visible = False
			PasswordWindow.instance().hide()
		elif flag == 1:
			# "���������Ѿ��ɹ��޸ģ����μ���������"
			showMessage( 0x03c3,"", MB_OK )
			PasswordWindow.instance().hide()
		elif flag == 2:
			# "����������벻��ȷ������������"
			showMessage( 0x03c4,"", MB_OK )
		elif flag == 3:
			# "������ľ����벻��ȷ������������"
			showMessage( 0x03ca,"", MB_OK )
		elif flag == 4:
			# "���������ɹ���"
			showMessage( 0x03c5, "", MB_OK )
			self.__pyUnlockBtn.visible = False
			self.__pyBtnLock.visible = True
		elif flag == 5:
			# "���������ɹ���"
			showMessage( 0x03c6, "", MB_OK )
			self.__pyUnlockBtn.visible = True
			self.__pyBtnLock.visible = False
		#elif flag == 6 :			# ֻ��3������ʱ�䣬û��Ҫ��ʾ����Ϣ��
			#showMessage( 0x03c7,"", MB_OK )
		elif flag == 7 :
			# "�ɹ��������ÿ�����֮ǰ�������ѱ���ա�"
			showMessage( 0x03c8,"", MB_OK )

	def __onLockTimeChange( self, time ):
		if time > 0:
			# "���Ѿ���������������Σ����Ժ�����"
			showMessage( 0x03c7,"", MB_OK )

	def __onLockStatusChange( self, status ):
		if status == 0:
			self.__pyBtnLock.visible = False
			self.__pyUnlockBtn.visible = True
		pswWindow = PasswordWindow.getInstance()
		if pswWindow is not None :
			pswWindow.updateLockStatus( status, self )

	def __itemColorChange( self, kitbagID, orderID, color = False ): #������Ʒ���ı���Ʒ��ɫ
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
			self.__showCancelTradeNotice() # ���ڽ���ʱ����Ҫ������ʾ�����ڽ�����ֱ������
		else:
			p.kitbags_lock()

	def __showCancelTradeNotice( self ):
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().kitbags_lock()
		# "�����������ᵼ�½���ȡ��,ȷ����?"
		showMessage( 0x03c9, "", MB_OK_CANCEL, query, self )
		
	def __showOpenCasketWindowIndication( self, idtId, *args ):
		"""
		"""
		player = BigWorld.player()
		if  len(args) ==0 and player.kitbags.has_key( csdefine.KB_CASKET_ID ) and not self.pyCasketWnd.visible: #ָ�������ϻ
			casketItem = self.__pyKitItems[ csdefine.KB_CASKET_ID ]
			toolbox.infoTip.showHelpTips( idtId, casketItem )
			self.addVisibleOpIdt( idtId )
		elif len( args ) == 1 :#ָ�����ʹ��ĳ��Ʒ
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
		���ȷ�Ͼ�����,�����ӿ�
		"""
		player = BigWorld.player()
		player.kitbag_afirmPassWord( oldPassWord )

	def onKitBagHide( self, kitBagID ): #ĳ�������ر�
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
		self.__showKitBags = [] #��ʾ�ı���
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
	�������Զ�������Զ����ӵĴ���
	"""
	def __selectType( self, pyMenuItem ):
		"""
		noParam�ں�����û���κ��ô�����������ڡ�
		����ExtraEvents.py�ᱨ��
		"""
		"""
		�ж�ǰ������ʱ�䣬���⵱��������������ť
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
		for item in tempTotalItem: #�����жϱ������Ƿ��ж�����Ʒ������������
			if item.isFrozen():
				BigWorld.player().statusMessage( csstatus.CIB_MSG_BAG_CANNOT_SORT )
				return
		desertItem = self.__getValidCombineItems( tempTotalItem )
		for i in desertItem:
			tempTotalItem.remove( i )
		if selectedIndex == 0:   # ����
	 		self.__sortByID(tempTotalItem)
		elif selectedIndex == 1: # Ʒ��
			self.__sortByQuality(tempTotalItem)
		elif selectedIndex==2:   # �۸�
			self.__sortByPrice(tempTotalItem)
		else:               # �ȼ�
			self.__sortByLevel(tempTotalItem)
		self.__getValidSortItem( tempTotalItem )
		if self.combineItem:
			self.__doCombineItem()
		else :
			self.__doSwapItem()

	def __getValidCombineItems( self,itemList ):
		"""
		�㷨˼·����ȥ���ѵ���������޵���Ʒ��Ȼ���itemList��id����
		�������ڵ�������Ʒ���idһ���Ұ�״̬һ������һ�����Ե��ӡ�
		��ȡ����һ�����Ե��ӵ�item1��
		Ȼ���item��Ķ�����ȡ����һ�����Ժ�item���ӵ�Ԫ��item2��
		���С��item1�ĵ������ޣ�����item1������ȡitem2
		�������item1�ĵ������ޣ�������ȡitem1��item2
		�������item1�ĵ������ޣ���item1 = item2������ȡitem2
		ͨ���ظ�����Ĺ��̿��Ի�����е��ӵ�Ԫ�ضԡ�
		�ú�����Ҫ��ȡ�ÿ��Ե��ӵ���Ʒ�����洢��һ��list��
		@param��itemlist
		@type�� list
		return��������Ҫ���ǵ���Ʒ
		"""
		if not itemList:return []
		canStackableItems = []
		for item in itemList:		# �ȰѲ��ܵ��ӵ���Ʒ����
			if item.amount < item.getStackable():
				canStackableItems.append( item )
		if len( canStackableItems ) < 2 : return []
		desertItems = []
		self.__sortByID( canStackableItems )
		item = canStackableItems[0]			#ȡ��itemlist�е�һ�����Ե��ӵ�Ԫ��
		(dstAmout, dstItem) = (item.getStackable()-item.amount,item)
		i=1 								#�ӵڶ���Ԫ�ؿ�ʼ��
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
		ÿ�δ�self.combineItemȡ��һ��Ҫ���ӵ�item���е���
		��self.combineItemΪ��ʱ����
		"""
		if not self.combineItem:
			return
		(a,b,c,d) = self.combineItem.pop(0)
		BigWorld.player().combineItem(a,b,c,d)

	def __getCommonKitBagItems(self):
		#��ȡ���б����е���Ʒ��ÿ���������������
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
		����������
		"""
		def func( item1, item2 ):
			if item1.id == item2.id:
				return cmp( item1.isBinded(), item2.isBinded() )
			else:
				return cmp(item1.id, item2.id)
		itemList.sort( cmp = func )

	def __sortByQuality( self, itemList ):
		"""
		��Ʒ�ʴӸߵ�������ͬƷ�ʰ��ȼ��Ӹߵ�������ͬƷ�ʡ��ȼ�����id����
		"""
		def func( item1, item2 ):
			if item1.getQuality() == item2.getQuality() and item1.getLevel() == item2.getLevel():
				return cmp( item2.id, item1.id )	# item2��ǰ��ԭ���ǣ���id������ӵ͵����ţ���Ʒ�ʡ��������෴��
			elif item1.getQuality() == item2.getQuality():
				return cmp( item2.getLevel(), item1.getLevel() )
			else:
				return cmp( item2.getQuality(), item1.getQuality() )
		itemList.sort( cmp = func )

	def __sortByPrice( self, itemList ):
		"""
		���۸�Ӹߵ�������ͬ�۸񰴵ȼ��Ӹߵ�������ͬ�۸񡢵ȼ�����id����
		"""
		def func( item1, item2 ):
			if item1.getPrice() == item2.getPrice() and item1.getLevel() == item2.getLevel():
				return cmp( item2.id, item1.id )	# item2��ǰ��ԭ���ǣ���id������ӵ͵����ţ���Ʒ�ʡ��������෴��
			elif item1.getPrice() == item2.getPrice():
				return cmp( item2.getLevel(), item1.getLevel() )
			else:
				return cmp( item2.getPrice(), item1.getPrice() )
		itemList.sort( cmp = func )


	def __sortByLevel( self, itemList ):
		"""
		���ȼ��Ӹߵ�������ͬ�ȼ���Ʒ�ʴӸߵ�������ͬ�ȼ���Ʒ�ʣ���id����
		"""
		def func( item1, item2 ):
			if item1.getLevel() == item2.getLevel() and item1.getQuality() == item2.getQuality():
				return cmp( item2.id, item1.id )	# item2��ǰ��ԭ���ǣ���id������ӵ͵����ţ���Ʒ�ʡ��������෴��
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
			#ģ����ʵ���������
			srcItem.order = dstKitOrder * csdefine.KB_MAX_SPACE + dstOrder
			for i in itemList:
				if i.order == dstKitOrder * csdefine.KB_MAX_SPACE + dstOrder:
					i.order = srcKitOrder * csdefine.KB_MAX_SPACE + srcOrder
					break

	def __getKitOrder( self, itemList ):
		#�����ܵ���Ʒ��������Ʒ�ı����ź��ڱ����е�����
		length = len( itemList )
		temp=0					#ǰi��������������
		tempOrder = length 		#��Ʒ�±���λ�ı���
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
			player.stopMove()									# ������ֹͣ�ƶ����Ա�֤׷��Ŀ�겻�����
			player.cell.flyToSpacePosition( self.treasureOrder, items[0].order )
		else:
			player.statusMessage( csstatus.SKILL_USE_ITEM_WHILE_FIGHTING )

	def __runToSpacePosition( self ):
		"""
		"""
		player = BigWorld.player()
		treasure_item = player.getItem_( self.treasureOrder )
		treasureSpace = treasure_item.query( "treasure_space", "" )		# ȡ���ر�ͼ�еĵ�ͼ��Ϣ
		treasurePosStr = treasure_item.query( "treasure_position", None )# ȡ���ر�ͼ�е�������Ϣ
		treasurePos = eval( treasurePosStr )
		player.autoRun( treasurePos, 8, treasureSpace )

	def __onShowAutoFindPathMenu( self, order ):
		"""
		"""
		self.treasureOrder = order
		self.__pyCMenu.popup( self )

	def __onResolutionChanged( self, preReso ):
		"""
		�ֱ��ʸı�
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
		������Ҫ��ʾ��ʾ����Ʒ
		"""
		player = BigWorld.player()
		def wieldEquip( baseItem ) :
			"""
			����Ƿ��װ����Ʒ
			"""
			return baseItem.isEquip() and baseItem.canWield( player )

		def wieldVehicle( baseItem ) :
			"""
			����Ƿ��ʹ�õ�����
			"""
			if baseItem.getType() == ItemTypeEnum.ITEM_SYSTEM_VEHICLE \
				and baseItem.getReqLevel() <= player.level :
					return True
			return False

		def useDrug( baseItem ) :
			"""
			����Ƿ��ʹ�õ�ҩƷ
			"""
			if baseItem.getType() in \
				[ ItemTypeEnum.ITEM_DRUG_ROLE_HP, ItemTypeEnum.ITEM_DRUG_ROLE_MP ] \
				and baseItem.getReqLevel() <= player.level :
					return True
			return False

		def useCatcher( baseItem ) :
			"""
			����Ƿ��ʹ�õĲ�����
			"""
			return baseItem.id in [ 60201023, 60201001, 60201050 ] \
			and baseItem.getReqLevel() <= player.level

		def useCasket( baseItem ) :
			"""
			����Ƿ������ϻ
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
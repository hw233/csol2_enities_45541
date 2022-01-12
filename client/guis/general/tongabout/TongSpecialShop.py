# -*- coding: gb18030 -*-
#
# $Id: StatWindow.py,fangpengjun Exp $

"""
implement StoreWindow
"""
from Time import Time
from bwdebug import *
from guis import *
import BigWorld
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.general.tradewindow.WareItem import WareItem
from guis.controls.ODComboBox import ODComboBox
from guis.controls.ComboBox import ComboItem
from guis.controls.TextBox import TextBox
from guis.controls.StaticText import StaticText
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ListItem import MultiColListItem
from guis.controls.CheckBox import CheckBoxEx
import event.EventCenter as ECenter
from GUIFacade import MerchantFacade
from config.client.msgboxtexts import Datas as mbmsgs
import csstatus
import csdefine
import csconst
import GUIFacade
import Const
import ShareTexts

g_chs_class = { csdefine.CLASS_FIGHTER	: ShareTexts.PROFESSION_FIGHTER,
			csdefine.CLASS_SWORDMAN	: ShareTexts.PROFESSION_SWORD,
			csdefine.CLASS_ARCHER	: ShareTexts.PROFESSION_ARCHER,
			csdefine.CLASS_MAGE		: ShareTexts.PROFESSION_MAGIC,
		}
		
class TongSpecialShop( Window ):
	"""
	帮会特殊商城
	"""
	
	_cc_items_rows = ( 6, 2 )
	
	_item_dragMark = DragMark.TONG_SPECIAL_ITEM

	def __init__( self ):
		wnd = GUI.load( "guis/general/tongabout/specialshop/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True
		self.__memberInfos = {}
		self.__selPost = 0
		self.__selProf = 0
		self.__offlineChecked = True
		self.__pyMsgBox = None
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )
	
	def __initialize( self, wnd ):
		itemsBg = wnd.itemsBg												# 商品面板
		self.__pageItemsPanel = ODPagesPanel( itemsBg.itemsPanel, itemsBg.pgIdxBar )			#商品购买界面
		self.__pageItemsPanel.onViewItemInitialized.bind( self.__initInvoiceItem )
		self.__pageItemsPanel.onDrawItem.bind( self.__drawInvoiceItem )
		self.__pageItemsPanel.selectable = True
		self.__pageItemsPanel.onItemSelectChanged.bind( self.__onItemSelectedChange )
		self.__pageItemsPanel.viewSize = self._cc_items_rows
		
		self.__pyLbGold = StaticText( wnd.moneyPanel.lbGold )
		self.__pyLbGold.text = ""
		self.__pyLbSilver = StaticText( wnd.moneyPanel.lbSilver )
		self.__pyLbSilver.text = ""
		self.__pyLbCopper = StaticText( wnd.moneyPanel.lbCoin )
		self.__pyLbCopper.text = ""
		
		cdtPanel = wnd.conditPanel
		self.__pyTbName = TextBox( cdtPanel.tbName.box )						#名称输入框
		self.__pyTbName.inputMode = InputMode.COMMON
		self.__pyTbName.text = ""
		self.__pyTbName.onTextChanged.bind( self.__onChangeName )
		self.__pyTbName.text = ""
	
		self.__pyTbMin = TextBox( cdtPanel.tbMin.box )							#最小输入
		self.__pyTbMin.inputMode = InputMode.INTEGER
		self.__pyTbMin.filterChars = ['-', '+']
		self.__pyTbMin.onTextChanged.bind( self.__onChangeMin )
		self.__pyTbMin.text = ""
		
		self.__pyTbMax = TextBox( cdtPanel.tbMax.box )							#最大输入
		self.__pyTbMax.inputMode = InputMode.INTEGER
		self.__pyTbMax.filterChars = ['-', '+']
		self.__pyTbMax.onTextChanged.bind( self.__onChangeMax )
		self.__pyTbMax.text = ""
		
		self.__pyCBPost = ODComboBox( cdtPanel.cbPost )							#职务下拉菜单
		self.__pyCBPost.autoSelect = False
		self.__pyCBPost.pyBox_.foreColor = ( 236, 215, 157, 255 )
		self.__pyCBPost.pyBox_.text = labelGather.getText( "TongAbout:SpecialShop", "post" )
		self.__pyCBPost.onItemSelectChanged.bind( self.__onPostSelected )
		duties = Const.TONG_GRADE_MAPPING.keys()
		duties.sort( reverse = True )
		for duty in duties:
			if duty == 0:continue
			dutyName = Const.TONG_GRADE_MAPPING.get( duty, "" )
			if len( dutyName ) <= 0:continue
			self.__pyCBPost.addItem( dutyName )
#		self.__pyCBPost.selItem = Const.TONG_GRADE_MAPPING[self.__selPost]

		self.__pyCBProf = ODComboBox( cdtPanel.cbProf )							#职业下拉菜单
		self.__pyCBProf.autoSelect = False
		self.__pyCBProf.pyBox_.foreColor = ( 236, 215, 157, 255 )
		self.__pyCBProf.pyBox_.text = labelGather.getText( "TongAbout:SpecialShop", "prof" )
		self.__pyCBProf.onItemSelectChanged.bind( self.__onProfSelected )
		profs = g_chs_class.keys()
		profs.sort()
		for prof in profs:
			profName = g_chs_class.get( prof )
			if profName is None:continue
			self.__pyCBProf.addItem( profName )
#		self.__pyCBProf.selItem = g_chs_class[self.__selProf]
		
		self.__pyBtnSearch = HButtonEx( cdtPanel.btnSearch )						#搜索
		self.__pyBtnSearch.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSearch.onLClick.bind( self.__onSearch )
		labelGather.setPyBgLabel( self.__pyBtnSearch, "TongAbout:SpecialShop", "reaschBtn" )

		self.__pyBtnReset = HButtonEx( cdtPanel.btnReset )							#重置
		self.__pyBtnReset.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnReset.onLClick.bind( self.__onReset )
		labelGather.setPyBgLabel( self.__pyBtnReset, "TongAbout:SpecialShop", "resetBtn" )
	
		self.__pyCKOffline = CheckBoxEx( cdtPanel.ckOffline ) 			#是否离线
		self.__pyCKOffline.checked = True
		self.__pyCKOffline.onCheckChanged.bind( self.__onOfflineCheck )
		labelGather.setPyLabel( self.__pyCKOffline.pyText_, "TongAbout:SpecialShop", "showOffline" )
	
		memPanel = wnd.memberPanel					#成员面板
		self.__pyCndBtns = {}
		for name, child in memPanel.children:
			if not name.startswith( "cndBtn_" ):continue
			index = int( name.split( "_" )[-1] )
			pyCndBtn = HButtonEx( child )
			pyCndBtn.setExStatesMapping( UIState.MODE_R3C1 )
			pyCndBtn.isSort = True
			pyCndBtn.sortByCnd = False
			pyCndBtn.sortIndex = index
			pyCndBtn.onLClick.bind( self.__sortByCnd )
			labelGather.setPyBgLabel( pyCndBtn, "TongAbout:SpecialShop", "cnd_%d"%index )
			self.__pyCndBtns[index] = pyCndBtn
	
		self.__pageMembersPanel = ODPagesPanel( memPanel.itemsPanel, memPanel.pgIdxBar )			#帮会成员列表
		self.__pageMembersPanel.onViewItemInitialized.bind( self.__initMemberItem )
		self.__pageMembersPanel.onDrawItem.bind( self.__drawMemberItem )
		self.__pageMembersPanel.ownerDraw = True
		self.__pageMembersPanel.selectable = True
		self.__pageMembersPanel.onItemSelectChanged.bind( self.__onMemberSeleted )
		self.__pageMembersPanel.viewSize = (10, 1)
		
		self.__pyBtnConfirm = HButtonEx( wnd.btnConfirm )
		self.__pyBtnConfirm.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnConfirm, "TongAbout:SpecialShop", "confirm" )
		self.__pyBtnConfirm.onLClick.bind( self.__onConfirm )
		self.__pyBtnConfirm.enable = False
		
		labelGather.setPyLabel( self.pyLbTitle_,"TongAbout:SpecialShop", "title" )
		labelGather.setLabel( itemsBg.title.stTitle, "TongAbout:SpecialShop", "invioceList" )
		labelGather.setLabel( cdtPanel.title.stTitle, "TongAbout:SpecialShop", "invioceAssign" )
		labelGather.setLabel( cdtPanel.cdtRangeText, "TongAbout:SpecialShop", "searchrange" )
		labelGather.setLabel( cdtPanel.nameText, "TongAbout:SpecialShop", "name" )
	
	def __initInvoiceItem( self, pyViewItem ):
		"""
		初始化商品
		"""
		item = GUI.load( "guis/general/tradewindow/item.gui" )
		uiFixer.firstLoadFix( item )
		pyInvoice = WareItem( item, self._item_dragMark, self )
		pyViewItem.pyInvoice = pyInvoice
		pyViewItem.addPyChild( pyInvoice )
		pyViewItem.dragFocus = False
		pyInvoice.left = 0
		pyInvoice.top = 0
	
	def __drawInvoiceItem( self, pyViewItem ):
		"""
		重置商品信息
		"""
		itemInfo = pyViewItem.pageItem
		pyInvoice = pyViewItem.pyInvoice
		pyViewItem.focus = itemInfo is not None
		pyInvoice.crossFocus = itemInfo is not None
		pyInvoice.selected = pyViewItem.selected
		pyInvoice.update( itemInfo )
	
	def __initMemberItem( self, pyViewItem ):
		"""
		初始化成员
		"""
		pyMember = MemberItem()
		pyMember.focus = False
		pyViewItem.addPyChild( pyMember )
		pyViewItem.focus = True
		pyMember.pos = -1.0, 1
		pyViewItem.pyItem = pyMember
	
	def __drawMemberItem( self, pyViewItem ):
		"""
		设置成员信息
		"""
		pyMember = pyViewItem.pyItem
		itemInfo = pyViewItem.pageItem
		pyMember.setMemberInfo( itemInfo )
		pyViewItem.focus = itemInfo is not None
		pyMember.crossFocus = itemInfo is not None
		pyViewItem.visible = itemInfo is not None
		pyMember.selected = pyViewItem.selected
		
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TRADE_WITH_TONG_SPECIAL_CHAPMAN"] = self.__onShopShow
		self.__triggers["EVT_ON_TONG_SEPCIAL_ITEM_ADDED"] = self.__onAddSpecialItem
		self.__triggers["EVT_ON_TONG_SEPCIAL_ITEM_AMOUNT_CHANGED"] = self.__onItemAmountChanged
		self.__triggers["EVT_ONTRADE_STATE_LEAVE"] = self.__onStateLeave
		self.__triggers["EVT_ON_TOGGLE_TONG_MONEY_CHANGE"] = self.__onTongMoneyChanged
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_ONLINE_STATE"] = self.__onMemberOnlineStateChanged
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_CONTRIBUTE"] = self.__onContributeChange 
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_TCONTRIBUTE"] = self.__onTContributeChange

		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )
	# ---------------------------------------------------------------
	def __onShopShow( self, chapman ):
		"""
		显示商店界面
		"""
		player = BigWorld.player()
		self.__onReset( self.__pyBtnReset )
		self.__setTongCanUseMoney( player.tong_getCanUseMoney() )
		self.show()
	
	def __onAddSpecialItem( self, index, invoiceInfo, tradeObj = "" ):
		"""
		商店添加商品
		"""
		itemInfo = ItemInfo( index, invoiceInfo, tradeObj )
		if not itemInfo in self.__pageItemsPanel.items:
			self.__pageItemsPanel.addItem( itemInfo )
	
	def __onItemAmountChanged( self, index, itemInfo, tradeObject ):
		"""
		物品数量改变
		"""
		if index < 1:
			return
		else:
			for pyViewItem in self.__pageItemsPanel.pyViewItems:
				pyInvoice = pyViewItem.pyInvoice
				if pyInvoice.index == index:
					itemInfo = ItemInfo( index, itemInfo, tradeObject )
					pyInvoice.update( itemInfo )
					break
	
	def __onStateLeave( self, state ):
		"""
		离开交易状态
		"""
		if state == csdefine.TRADE_CHAPMAN:
			GUIFacade.tradeOverWithNPC()
			self.hide()
			BigWorld.player().tradeState = csdefine.TRADE_NONE
	
	def __onTongMoneyChanged( self, money ):
		"""
		帮会资金改变
		"""
		money = BigWorld.player().tong_getCanUseMoney()
		if money <= 0:
			money = 0
		self.__setTongCanUseMoney( money )
	
	def __setTongCanUseMoney( self, money ):
		"""
		设置可用资金
		"""
		gold = money/10000
		sliver = ( money/100 )%100
		copper = ( money%100 )%100
		self.__pyLbGold.text = str( gold )
		self.__pyLbSilver.text = str( sliver )
		self.__pyLbCopper.text = str( copper )
	
	def __onMemberOnlineStateChanged( self, memberDBID, isOnline ):
		"""
		帮会成员在线状态改变
		"""
		stateText = ""
		if isOnline:
			stateText = labelGather.getText( "TongAbout:SpecialShop", "online" )
		else:
			stateText = labelGather.getText( "TongAbout:SpecialShop", "offline" )
		self.__onMemberInfoChange( memberDBID, 7, 6, stateText )

	def __onContributeChange( self, memberID, contribute ):
		"""
		成员帮贡改变
		"""
		self.__onMemberInfoChange( memberDBID, 5, 4, contribute )
	
	def __onTContributeChange( self, memberDBID, totalContribute ):
		"""
		成员总帮贡改变
		"""
		self.__onMemberInfoChange( memberDBID, 6, 5, totalContribute )

	def __onMemberInfoChange( self, memberDBID, infoIndex, colIndex, infoValue ):
		"""
		帮会成员属性值统一更新接口
		"""
		for pyViewItem in self.__pageMembersPanel.pyViewItems:
			member = pyViewItem.pageItem
			if member is None:continue
			if member[0] == memberDBID:
				member = self.__memberInfos.get( memberDBID )
				if member is None:return
				member[infoIndex] = str( infoValue )
				pyMember = pyViewItem.pyItem
				pyMember.pyCols[colIndex].text = str( infoValue )
	
	def __onItemSelectedChange( self, index ):
		"""
		选取某个商品
		"""
		if index < 0: return
		itemInfo = self.__pageItemsPanel.selItem
		if itemInfo is None:return
		baseInfo = itemInfo.baseInfo
		baseItem = baseInfo.baseItem
		memberInfo = self.__pageMembersPanel.selItem
		self.__pyBtnConfirm.enable = itemInfo is not None and memberInfo is not None
	
	def __onMemberSeleted( self, index ):
		"""
		选择帮会成员
		"""
		if index < 0: return
		memberInfo = self.__pageMembersPanel.selItem
		for pyViewItem in self.__pageMembersPanel.pyViewItems:
			member = pyViewItem.pageItem
			if member is None:continue
			pyMember = pyViewItem.pyItem
			pyMember.selected = member[0] == memberInfo[0]
		itemInfo = self.__pageItemsPanel.selItem
		self.__pyBtnConfirm.enable = memberInfo is not None and itemInfo is not None
	
	def __onChangeName( self ):
		"""
		姓名改变
		"""
		pass
	
	def __onChangeMin( self ):
		"""
		最小值改变
		"""
		pass
	
	def __onChangeMax( self ):
		"""
		最大值改变
		"""
		pass
	
	def __onPostSelected( self, index ):
		"""
		职务选择
		"""
		if index < 0:return
		post_map = {0:csdefine.TONG_DUTY_CHIEF, 1:csdefine.TONG_DUTY_DEPUTY_CHIEF, 2:csdefine.TONG_DUTY_TONG, 3:csdefine.TONG_DUTY_MEMBER}
		self.__selPost = post_map.get( index )
	
	def __onProfSelected( self, index ):
		"""
		职业选择
		"""
		if index < 0:return
		prof_map = {0:csdefine.CLASS_FIGHTER, 1:csdefine.CLASS_SWORDMAN, 2:csdefine.CLASS_ARCHER, 3:csdefine.CLASS_MAGE}
		self.__selProf = prof_map.get( index )
	
	def __onSearch( self, pyBtn ):
		"""
		搜索
		"""
		if pyBtn is None:return
		player = BigWorld.player()
		memberName = self.__pyTbName.text
		min = 0
		max = 0
		minText = self.__pyTbMin.text
		maxText =  self.__pyTbMax.text
		if len( minText ) > 0:
			min = int( minText )
		if len( maxText ) > 0:
			max = int( maxText )
		if min > max:
			if self.__pyMsgBox is not None:
				self.__pyMsgBox.visible = False
				self.__pyMsgBox = None
			self.__pyMsgBox = showMessage( mbmsgs[0x11b1],"", MB_OK, None, pyOwner = self )
			return
		self.__pageMembersPanel.clearItems()
		members = player.tong_memberInfos
		for dbid, member in members.items():
			prof = member._class&csdefine.RCMASK_CLASS
			if not self.__offlineChecked and not member.isOnline():
				continue
			if min > 0 and member._contribute < min:
				continue
			if max > 0 and member._contribute > max:
				continue
			if self.__selPost > 0 and self.__selPost != member._grade:
				continue
			if self.__selProf > 0 and self.__selProf != prof:
				continue
			if len( memberName ) > 0 and member._name != memberName:
				continue
			memberInfo = [dbid, member._name, member._level, prof, member._grade, str(member._contribute), str(member._totalContribute), member._isOnline]
			self.__pageMembersPanel.addItem( memberInfo )
	
	def __onReset( self, pyBtn ):
		"""
		重置
		"""
		if pyBtn is None:return
		self.__pyTbName.text = ""
		self.__pyTbMin.text = ""
		self.__pyTbMax.text = ""
		self.__selPost = 0
		self.__selProf = 0
		self.__offlineChecked = True
		self.__pyCBPost.pyBox_.text = labelGather.getText( "TongAbout:SpecialShop", "post" )
		self.__pyCBProf.pyBox_.text = labelGather.getText( "TongAbout:SpecialShop", "prof" )
		self.__pyCKOffline.checked = self.__offlineChecked
		player = BigWorld.player()
		self.__memberInfos = {}
		self.__pageMembersPanel.clearItems()
		self.__pyTbName.tabStop = True
		for dbid, member in player.tong_memberInfos.items():
			if not dbid in self.__memberInfos:
				prof = member._class&csdefine.RCMASK_CLASS
				memberInfo = [dbid, member._name, member._level, prof, member._grade, str(member._contribute), str(member._totalContribute), member._isOnline]
				self.__memberInfos[dbid] = memberInfo
				self.__pageMembersPanel.addItem( memberInfo )
	
	def __onOfflineCheck( self, checked ):
		"""
		是否显示离线
		"""
		self.__offlineChecked = checked
		if checked:
			self.__showAlls()
		else:
			self.__showOnlines()
		
	def __showAlls( self ):
		"""
		显示全部
		"""
		self.__pageMembersPanel.clearItems()
		onlineMembers = []
		offlineMembers = []
		members = BigWorld.player().tong_memberInfos
		for dbid, member in members.iteritems():
			if member.isOnline():
				onlineMembers.append( member )
			else:
				offlineMembers.append( member )
		onlineMembers.sort( key = lambda n: n.getGrade(), reverse = True )
		offlineMembers.sort( key = lambda n: n.getGrade(), reverse = True )
		allMembers = onlineMembers + offlineMembers
		for member in allMembers:
			prof = member._class&csdefine.RCMASK_CLASS
			memberInfo = [dbid, member._name, member._level, prof, member._grade, str(member._contribute), str(member._totalContribute), member._isOnline]
			self.__pageMembersPanel.addItem( memberInfo )
	
	def __showOnlines( self ):
		"""
		显示在线
		"""
		self.__pageMembersPanel.clearItems()
		onlineMembers = []
		members = BigWorld.player().tong_memberInfos
		for dbid, member in members.iteritems():
			if member.isOnline():
				onlineMembers.append( member )
		onlineMembers.sort( key = lambda n: n.getGrade(), reverse = True )
		for member in onlineMembers:
			prof = member._class&csdefine.RCMASK_CLASS
			memberInfo = [dbid, member._name, member._level, prof, member._grade, str(member._contribute), str(member._totalContribute), member._isOnline]
			self.__pageMembersPanel.addItem( memberInfo )
	
	def __sortByCnd( self, pyCnd ):
		"""
		按条件排序
		"""
		if pyCnd is None:return
		sortIndex = pyCnd.sortIndex + 1
		flag = pyCnd.sortByCnd and True or False
		self.__pageMembersPanel.sort( key = lambda item : item[sortIndex], reverse = flag )
		pyCnd.sortByCnd = not pyCnd.sortByCnd
	
	def __onConfirm( self, pyBtn ):
		"""
		确认分配
		"""
		if pyBtn is None:return
		chapman = MerchantFacade.chapman
		memInfo = self.__pageMembersPanel.selItem
		itemInfo = self.__pageItemsPanel.selItem
		itemName = itemInfo.baseInfo.name_()
		amount = 1
		if chapman and chapman.__class__.__name__ == "TongSpecialChapman":
			def query( rs_id ):
				if rs_id == RS_OK:
					chapman.cell.sellArrayTo( memInfo[0], [itemInfo.index], [amount] )
		if self.__pyMsgBox is not None:
			self.__pyMsgBox.visible = False
			self.__pyMsgBox = None
		self.__pyMsgBox = showMessage( mbmsgs[0x11b0] %( itemName, memInfo[1] ),"", MB_OK_CANCEL, query, pyOwner = self )

	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		self.hide()

	def show( self ):
		Window.show( self )

	def hide( self ):
		if rds.statusMgr.isInWorld() :
			GUIFacade.tradeOverWithNPC()
			BigWorld.player().tradeState = csdefine.TRADE_NONE
		self.__pageItemsPanel.clearItems()
		self.__pageMembersPanel.clearItems()
		self.__memberInfos = {}
		Window.hide( self )

# ------------------------------------------------------------------------------------------
# 帮会成员信息列表
class MemberItem( MultiColListItem ):
	
	_ITEM = None
	
	def __init__( self ):
		if MemberItem._ITEM is None:
			MemberItem._ITEM = GUI.load( "guis/general/tongabout/specialshop/membitem.gui" )
		item = util.copyGuiTree( MemberItem._ITEM )
		uiFixer.firstLoadFix( item )
		MultiColListItem.__init__( self, item )
		self.commonBackColor = ( 255, 255, 255, 255 )
		self.selectedBackColor = ( 255, 255, 255, 255 )
		self.highlightBackColor = ( 255, 255, 255, 255 )
		self._selected = False
	
	def setMemberInfo( self, member ):
		"""
		更新成员信息
		"""
		if member is None:return
		online = member[-1]
		state = labelGather.getText( "TongAbout:SpecialShop", "online" )
		self.pyCols[-1].foreColor = (255, 248, 158, 255)
		if not online:
			self.pyCols[-1].foreColor = ( 128, 128, 128, 255 )
			state = labelGather.getText( "TongAbout:SpecialShop", "offline" )
		levelText = "%d级"%member[2]
		profName = g_chs_class.get( member[3], "" )
		dutyName = Const.TONG_GRADE_MAPPING.get( member[4], "" )
		self.setTextes( member[1],
					levelText,
					profName,
					dutyName,
					member[5],
					member[6],
					state
		 )

	def onStateChanged_( self, state ) :
		"""
		状态改变时调用
		"""
		elements = self.getGui().elements
		for element in elements.values():
			element.visible = state in [ UIState.HIGHLIGHT, UIState.SELECTED ]

	def onMouseEnter_( self ):
		MultiColListItem.onMouseEnter_( self )
		if self.selected:return
		self.setState( UIState.HIGHLIGHT )

	def onMouseLeave_( self ):
		MultiColListItem.onMouseLeave_( self )
		if self.selected:return
		self.setState( UIState.COMMON )

	def _select( self ):
		self.setState( UIState.HIGHLIGHT )

	def _deselect( self ):
		self.setState( UIState.COMMON )

	def _getSelected( self ):
		return self._selected

	def _setSelected( self, selected ):
		if selected:
			self._select()
		else:
			self._deselect()
		self._selected = selected

	selected = property( _getSelected, _setSelected )

class ItemInfo:
	def __init__( self, index, baseInfo, npcName = "" ):
		self.index = index
		self.baseInfo = baseInfo
		self.npcName = npcName
		self.uid = -1
		
	def update( self, uid, itemInfo ):
		self.uid = uid
		self.baseInfo = itemInfo
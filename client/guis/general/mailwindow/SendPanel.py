# -*- coding: gb18030 -*-
#
# $Id: SendPanel.py,v 1.7 2008-08-26 02:15:38 huangyongwei Exp $

"""
implement sendpanel  class
"""

import csdefine
import csstatus_msgs
import csconst
import csstatus
import event.EventCenter as ECenter
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.TextBox import TextBox
from guis.controls.TabCtrl import TabPanel
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.TabSwitcher import TabSwitcher
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from ItemsFactory import ObjectItem as ItemInfo
from InputPanel import InputPanel
from MailItem import MailItem
from config.client.msgboxtexts import Datas as mbmsgs
from guis.general.StoreWindow.CompareDspItem import CompareDspItem
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar

class SendPanel( TabPanel ):
	def __init__( self, panel, pyBinder ):
		TabPanel.__init__( self, panel, pyBinder )
		self.posZSegment = ZSegs.L4			# in uidefine.py
		self.activable_ = True				# if a root gui can be ancriated, when it becomes the top gui, it will rob other gui's input focus
		self.escHide_ 		 = True
		self.__sendType = csdefine.MAIL_TYPE_NORMAL
		self.__pySendItems = {}
		self.__uids = {} #保存邮寄物品uid
		self.__itemTotal = 0 #全局物品统计 by姜毅
		self.__totalRequireMoney = 0 #全局需金钱
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( panel )

	def __initialize( self, panel ):
		labelGather.setLabel( panel.themeText, "MailWindow:panel_1", "themeText" )
		labelGather.setLabel( panel.addresseeText, "MailWindow:panel_1", "addresseeText" )
		labelGather.setLabel( panel.moneyText, "MailWindow:panel_1", "moneyText" )
		self.__pyRtPostage = CSRichText( panel.rtPostage )
		self.__pyRtPostage.text = ""
		
		self.__moneyInput = MoneyBar( panel.moneyPanel )
		self.__moneyInput.money = 0
		self.__moneyInput.onTextChanged.bind( self.__onSendMoneyChange )
		
		self.__pyBtnSend = HButtonEx( panel.btnSend )
		self.__pyBtnSend.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSend.onLClick.bind( self.__onSend )
		labelGather.setPyBgLabel( self.__pyBtnSend, "MailWindow:panel_1", "btnSend" )

		self.__pyBtnClear = HButtonEx( panel.btnClear )
		self.__pyBtnClear.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnClear.onLClick.bind( self.__onClear)
		labelGather.setPyBgLabel( self.__pyBtnClear, "MailWindow:panel_1", "btnClear" )

		self.__pyNameBox = TextBox( panel.nameBox.box ) # 收信人名称
		self.__pyNameBox.inputMode = InputMode.COMMON
		self.__pyNameBox.onTextChanged.bind( self.__onTextChanged_ )
		self.__pyNameBox.text = ""
		self.__pyNameBox.maxLength = 14

		self.__pyTitleBox = TextBox( panel.titleBox.box ) # 信件标题
		self.__pyTitleBox.inputMode = InputMode.COMMON
		self.__pyTitleBox.onTextChanged.bind( self.__onTextChanged_ )
		self.__pyTitleBox.text = ""
		self.__pyTitleBox.maxLength = 20

		self.__pyCheckType = CheckBoxEx( panel.cbExType )
		self.__pyCheckType.onCheckChanged.bind( self.__onTypeCheck )
		self.__pyCheckType.checked = False
		self.__pyCheckType.text = labelGather.getText( "MailWindow:panel_1", "cbExType" )

		self.__pyInputPanel = InputPanel( panel.inputPanel, panel.scrollBar )
		self.__pyInputPanel.text = ""
		
		tabInCtrls = [self.__pyNameBox, self.__pyTitleBox, self.__pyInputPanel.pyBox]
		tabInCtrls.extend( self.__moneyInput.pyTabInControls )
		self.__pyTabSwitcher = TabSwitcher( tabInCtrls )	# 焦点转移控件

		for name, item in panel.children: #初始化发送物品格
			if name.startswith( "sdItem_" ):
				index = int( name.split( "_" )[1] )
				pySendItem = MailItem( item, DragMark.MAIL_SEND_ITEM, index )
				pySendItem.index = index
				self.__pySendItems[index] = pySendItem

	def __getMailCost( self, mailType ):
		"""
		实时邮资计算 by姜毅
		@param mailType : 邮件类型
		@type  mailType : int8
		"""
		if mailType == csdefine.MAIL_TYPE_QUICK:	# 快递收费是普通邮件总邮费的2倍
			mailCost = 2
		elif mailType == csdefine.MAIL_TYPE_NORMAL:	# 普通信件
			mailCost = 1
		mmoney = self.__moneyInput.money
		value = ( mmoney * csconst.MAIL_SEND_MONEY_RATE + csconst.MAIL_FARE ) * mailCost

		itemDatas = self.__itemTotal
		if itemDatas != 0:
			value += csconst.MAIL_SEND_ITEM_FARE * itemDatas * mailCost

		self.__totalRequireMoney = mmoney + value
		postageText = utils.currencyToViewText( int( value ) )
		self.__pyRtPostage.text = PL_Font.getSource(labelGather.getText( "MailWindow:panel_1", "rtPostage", postageText ), fc = ( 230, 227, 185 ) )


	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_MAIL_ADD_SENDITEM"] = self.__onAddSendItem
		self.__triggers["EVT_ON_MAIL_DEL_SENDITEM"] = self.__onDelSendItem
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onKitbagUpdateItem #背包物品信息发生改变时调用
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onKitbagRemoveItem #背包物品被删除时调用
		self.__triggers["EVT_ON_MAIL_SWAP_ITEMS"]    = self.__onSwapItems #交换信件物品
		self.__triggers["EVT_ON_MAIL_SEND_SUCCED"] = self.__onSendSucced
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	# ------------------------------------------------------------
	def __onSendMoneyChange( self ):
		self.__getMailCost( self.__sendType )

	def __onAddSendItem( self, kitbagID, gbIndex, index ):
		player = BigWorld.player()
		orderID = gbIndex + kitbagID * csdefine.KB_MAX_SPACE
		item = player.getItem_( orderID )
		itemInfo = ItemInfo( item )
		if itemInfo.baseItem.isBinded() :        #如果物品绑定/不可出售,则不能拖入邮寄栏,同时产生系统提示,加入者姜毅2009-5-27
			player.statusMessage( csstatus.MAIL_FORBID_BINDED_ITEM )
			return
		if itemInfo.baseItem.reqYinpiao() :        #如果物品绑定/不可出售,则不能拖入邮寄栏,同时产生系统提示,加入者姜毅2009-5-27
			player.statusMessage( csstatus.MAIL_FORBID_YINPIAO_ITEM )
			return
		if item.uid in [pyItem.uid for pyItem in self.__pySendItems.itervalues()]: #该物品已经在邮寄列表中
			return
		mailItem = self.__pySendItems.get( index, None )
		if mailItem is None : return
		if mailItem.itemInfo is not None :
			self.__onDelSendItem( index )
		mailItem.update( itemInfo )
		ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, gbIndex, True )
		self.__itemTotal += 1
		self.__getMailCost( self.__sendType )

	def __onDelSendItem( self, index ):
		sendItem = self.__pySendItems.get( index )
		if sendItem is None:return
		itemInfo = sendItem.itemInfo
		kitbagID = itemInfo.kitbagID
		orderID = itemInfo.orderID
		ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, False )
		sendItem.update( None )
		self.__itemTotal -= 1
		self.__getMailCost( self.__sendType )

	def __onKitbagUpdateItem( self, itemInfo ):
		if itemInfo is None:return
		uid = itemInfo.baseItem.uid
		for pyItem in self.__pySendItems.itervalues():
			if pyItem.uid == uid:
				pyItem.update( itemInfo )

	def __onKitbagRemoveItem( self, itemInfo ):
		if itemInfo is None:return
		uid = itemInfo.baseItem.uid
		for pyItem in self.__pySendItems.itervalues():
			if pyItem.uid == uid:
				pyItem.update( None )

	def __onSendSucced( self, isSucced ):
		if isSucced:
			self.reset()
			self.__itemTotal = 0
			self.__getMailCost( csdefine.MAIL_TYPE_NORMAL )

	def __onSwapItems( self, srcIndex, dstIndex ):
		pyScrItem = self.__pySendItems.get( srcIndex, None )
		pyDstItem = self.__pySendItems.get( dstIndex, None )
		if not pyScrItem and not pyScrItem.itemInfo :return
		tmpInfo = pyScrItem.itemInfo
		pyScrItem.update( pyDstItem.itemInfo )
		pyDstItem.update( tmpInfo )
		self.__getMailCost( self.__sendType )

	def __onTextChanged_( self ):
		self.__pyBtnSend.enable = self.__pyNameBox.text != "" and self.__pyTitleBox.text != ""
		self.__getMailCost( self.__sendType )

	def __onTypeCheck( self, checked ):
		if checked:
			self.__sendType = csdefine.MAIL_TYPE_QUICK
		else:
			self.__sendType = csdefine.MAIL_TYPE_NORMAL
		self.__getMailCost( self.__sendType )

	def __getItemsInfo( self ): #获取待发送物品的背包和索引列表
		uids = []
		for pySendItem in self.__pySendItems.itervalues():
			itemInfo = pySendItem.itemInfo
			if itemInfo is None:continue
			uids.append( itemInfo.uid )
		return uids

	def __onSend( self ): # 发信
		player = BigWorld.player()
		addresseeName = self.__pyNameBox.text
		title = self.__pyTitleBox.text
		if addresseeName == BigWorld.player().getName():  #增加不能给自己发邮件的提示 by姜毅
			player.statusMessage( csstatus.MAIL_FORBID_YOURSELF )
			return
		money = self.__moneyInput.money
		if money > player.money:
			player.statusMessage( csstatus.MAIL_SEND_MONEY_NO_ENOUGH )
			return
		if self.__totalRequireMoney > player.money:
			player.statusMessage( csstatus.MAIL_MONEY_NO_ENOUGH )
			return
		uids = self.__getItemsInfo()
		content = self.__pyInputPanel.text
		if content == "":
			showMessage( mbmsgs[0x0443], "", MB_OK, None, self )
		else:
			if len( uids ) or money > 0:
				def query( rs_id ):
					if rs_id == RS_OK:
						player.mail_send( addresseeName, self.__sendType, title, content, money, uids )
				showMessage( mbmsgs[0x0442]%addresseeName, "", MB_OK_CANCEL, query, self.pyTopParent )
				return True
			else:
				player.mail_send( addresseeName, self.__sendType, title, content, money, uids )
		self.__pyNameBox.tabStop = True

	def __onClear( self ):
		self.reset()
		self.__itemTotal = 0
		self.__getMailCost( csdefine.MAIL_TYPE_NORMAL )

	# ------------------------------------------------------
	# public
	# ------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def restoreMail( self, name ):
		self.reset()
		self.__pyNameBox.text = name
		self.__itemTotal = 0
		self.__getMailCost( csdefine.MAIL_TYPE_NORMAL )

	def hide( self ):
		for pySendItem in self.__pySendItems.itervalues():
			if pySendItem.itemInfo is None:continue
			itemInfo = pySendItem.itemInfo
			kitbagID = itemInfo.kitbagID
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, False )

	def show( self ):
		for pySendItem in self.__pySendItems.itervalues():
			if pySendItem.itemInfo is None:continue
			itemInfo = pySendItem.itemInfo
			kitbagID = itemInfo.kitbagID
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, True )
		self.__pyNameBox.tabStop = True

	def reset( self ): # 重置界面"
		self.__moneyInput.money = 0
		self.__pyNameBox.text = ""
		self.__pyTitleBox.text = ""
		self.__pyInputPanel.text = ""
		self.__pyCheckType.checked = False
		self.__pyNameBox.tabStop = True
		for pySendItem in self.__pySendItems.itervalues():
			if pySendItem.itemInfo is None:continue
			itemInfo = pySendItem.itemInfo
			kitbagID = itemInfo.kitbagID
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, False )
			pySendItem.update( None )

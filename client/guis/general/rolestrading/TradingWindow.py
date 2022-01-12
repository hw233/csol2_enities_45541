# -*- coding: gb18030 -*-
#
# $Id: TradingWindow.py,v 1.17 2008-06-27 03:19:27 huangyongwei Exp $

"""
implement tradingwindow( the base class of buying window and selling window )
"""

from guis import *
from guis.common.Window import Window
from TargetPanel import TargetPanel
from MyPanel import MyPanel
from guis.controls.Button import Button
from guis.controls.TextBox import TextBox
from guis.controls.StaticText import StaticText
from event.EventCenter import *
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
from gbref import rds
import GUIFacade
import csdefine
import csconst
import csstatus

TARGET_UNLOCK 	= labelGather.getText( "TradingWindow:main", "miTargetUnlock" )	# ���ڱ�ʾ����Ŀ��δ��������״̬
TARGET_LOCK 	= labelGather.getText( "TradingWindow:main", "miTargetLock" )	# ���ڱ�ʾ����Ŀ������������״̬

class TradingWindow( Window ) :
	def __init__( self ) :
		wnd = GUI.load( "guis/general/rolestrading/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )

		self.__allowHide = False
		self.__triggers = {}
		self.__registerTriggers()
		self.addToMgr( "rolesTradingTradeWindow" )

		self.__trapID = 0	# �Ի�����id
		self.__pyInviteBox = None	# ����ȷ�Ͽ�

		mutexGroups = [ MutexGroup.TRADE1, MutexGroup.TRADE2 ]
		rds.mutexShowMgr.addRootToMutexGroups( self, mutexGroups )				# ��ӵ����������

	def __initialize( self, wnd ) :

		self.__pyLbTargetName = StaticText( wnd.targetName )					# label for showing target name
		self.__pyLbTargetName.text = ""
		self.__pyLbMyName = StaticText( wnd.myName )							# label for showing my name
		self.__pyLbMyName.text = ""

		self.__pyTargetTexts = []
		self.__pyLbTargetGold = StaticText( wnd.targetMoney.lbGold )		# label for showing target money
		self.__pyLbTargetGold.text = "0"
		self.__pyTargetTexts.append( self.__pyLbTargetGold )

		self.__pyTargetSilver = StaticText( wnd.targetMoney.lbSilver )
		self.__pyTargetSilver.text = "0"
		self.__pyTargetTexts.append( self.__pyTargetSilver )

		self.__pyTargetCoin = StaticText( wnd.targetMoney.lbCoin )
		self.__pyTargetCoin.text = "0"
		self.__pyTargetTexts.append( self.__pyTargetCoin )

		self.__pyMyBoxs = []
		self.__pyTBMyGold = TextBox( wnd.myMoney.goldBox, self )		# text box for input my money
		self.__pyTBMyGold.inputMode = InputMode.INTEGER
		self.__pyTBMyGold.filterChars = ['-', '+']
		self.__pyTBMyGold.maxLength = 7
		self.__pyTBMyGold.onTextChanged.bind( self.__moneyChange )
		self.__pyMyBoxs.append( self.__pyTBMyGold )

		self.__pyTBMySilver = TextBox( wnd.myMoney.silverBox, self )
		self.__pyTBMySilver.inputMode = InputMode.INTEGER
		self.__pyTBMySilver.filterChars = ['-', '+']
		self.__pyTBMySilver.maxLength = 2
		self.__pyTBMySilver.onTextChanged.bind( self.__moneyChange )
		self.__pyMyBoxs.append( self.__pyTBMySilver )

		self.__pyTBMyCoin = TextBox( wnd.myMoney.coinBox, self )
		self.__pyTBMyCoin.inputMode = InputMode.INTEGER
		self.__pyTBMyCoin.filterChars = ['-', '+']
		self.__pyTBMyCoin.maxLength = 2
		self.__pyTBMyCoin.onTextChanged.bind( self.__moneyChange )
		self.__pyMyBoxs.append( self.__pyTBMyCoin )

		self.__pyTargetStateText = StaticText( wnd.targetPanel.lockState )
		self.__pyTargetStateText.text = TARGET_UNLOCK
		self.__pyTargetStateText.getGui().colour = ( 255, 0, 0, 255 )

		self.__pyLockBtn = Button( wnd.myPanel.lockBtn, self )
		self.__pyLockBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyLockBtn.onLClick.bind( self.__onLockTrade )

		self.__pyUnlockBtn = Button( wnd.myPanel.unlockBtn, self )
		self.__pyUnlockBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyUnlockBtn.onLClick.bind( self.__onUnlockTrade )

		self.__pyMyTradeBtn = Button( wnd.myPanel.tradeBtn, self )
		self.__pyMyTradeBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyMyTradeBtn.onLClick.bind( self.__onMyTrade )

		self.__pyCloseBtn = Button( wnd.closeBtn, self )
		self.__pyCloseBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyCloseBtn.onLClick.bind( self.__onClose )

		self.__pyMyIPanel = MyPanel( wnd.myPanel.itemsPanel, self )
		self.__pyTargetIPanel = TargetPanel( wnd.targetPanel.itemsPanel, self )

		# ---------------------------------------------
		# ���ñ�ǩ
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyLockBtn, "TradingWindow:main", "lockBtn" )
		labelGather.setPyBgLabel( self.__pyUnlockBtn, "TradingWindow:main", "unlockBtn" )
		labelGather.setPyBgLabel( self.__pyMyTradeBtn, "TradingWindow:main", "tradeBtn" )

	def dispose( self ) :
		"""
		release resource
		"""
		self.__deregisterTriggers()
		Window.dispose( self )

	def __addTrap( self ):
		distance = csconst.COMMUNICATE_DISTANCE
		self.__trapID = BigWorld.player().addTrapExt( distance, self.__onEntitiesTrapThrough )

	def __delTrap( self ):
		if self.__trapID :
			BigWorld.player().delTrap( self.__trapID )				# ɾ����ҵĶԻ�����
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		target = BigWorld.player().si_getTargetEntity()	# ��ý���Ŀ��
		if target and target not in entitiesInTrap:		# �������Ŀ���뿪��ҶԻ�����
			GUIFacade.cancelSwapItem()
			self.__endTrade()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		register event triggers
		"""
		self.__triggers[ "EVT_ON_RSI_INVITE_SWAP_ITEM" ] = self.__onInvite				# be invited
		self.__triggers[ "EVT_ON_RSI_SWAP_ITEM_BEGIN" ] = self.__beginTrade				# begin to trade
		self.__triggers[ "EVT_ON_RSI_SWAP_ITEM_END" ] = self.__endTrade					# end trading

		self.__triggers[ "EVT_ON_RSI_DST_ITEM_CHANGED" ] = self.__onTargetItemChanged		# target object item changed
		self.__triggers[ "EVT_ON_RSI_DST_MONEY_CHANGED" ] = self.__onTargetMoneyChanged	# target money being changed
		self.__triggers[ "EVT_ON_RSI_DST_SWAP_STATE_CHANGED" ] = self.__onTargetStateChange	# target confirmed

		self.__triggers[ "EVT_ON_RSI_SELF_ITEM_CHANGED" ] = self.__onMyItemChanged		# my item changed
		self.__triggers[ "EVT_ON_RSI_SELF_MONEY_CHANGED" ] = self.__onMyMoneyChanged		# my money chnaged
		self.__triggers[ "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED" ] = self.__onMyStateChange	# I confirmed
		self.__triggers["EVT_ONTRADE_STATE_LEAVE"] = self.__onStateLeave
		self.__triggers["EVT_ON_ROLE_DEAD"] = self.__endTrade								#��ɫ���������ش���

		self.__triggers["EVT_ON_TRADE_SWAP_ADD_ITEM"] = self.__onTradeSwapAddItem			# �һ����ӽ�����Ʒ
		self.__triggers["EVT_ON_TRADING_WINDOW_MUTEX"] = self.__endTradeStraight			# ����Ʒ���׽��滥�⣬��Ʒ���׽���ر�
		self.__triggers["EVT_ON_ROLE_MONEY_CHANGED"] = self.__onRoleMoneyChange				# ��ɫ���Ͻ�Ǯ�ı�

		for macroName in self.__triggers.iterkeys():
			GUIFacade.registerEvent( macroName, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for macroName in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( macroName, self )

	# -------------------------------------------------
	def __onTradeConfirmed( self, id ) :
		"""
		show message box for trading confirmation
		"""
		GUIFacade.inviteSwapItemReply( id == RS_YES )

	def __onCancelTradeConfirmed( self, btnID ) :
		"""
		show messagebox for cancel trading confirmation
		"""
		if btnID == RS_YES :
			GUIFacade.cancelSwapItem()

	def __onLockTrade( self ):
		"""
		�������ף����뽻�׵ȴ�״̬
		"""
		GUIFacade.swapAccept()

	def __onUnlockTrade( self ) :
		"""
		ȡ�����������ؽ��׽���״̬
		"""
		player = BigWorld.player()
		player.cell.si_changeStateFC( csdefine.TRADE_SWAP_BEING )

	def __onMyTrade( self ):
		if self.__pyTargetStateText.text == TARGET_UNLOCK or\
		self.__pyLockBtn.visible :
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_HAVE_NOT_LOCKED )
			return
		GUIFacade.swapAccept2()

	def __onMoneyTabOut( self ):
		"""
		��������ͭ�����ʧȥ����ʱ������������Ϣ��֪ͨ�Է�������Ǯ�ı�
		"""
		if self.__pyTBMyGold.tabStop or self.__pyTBMySilver.tabStop or self.__pyTBMyCoin.tabStop:
			return
		goldText = self.__pyTBMyGold.text.strip()
		silverText = self.__pyTBMySilver.text.strip()
		coinText = self.__pyTBMyCoin.text.strip()
		if goldText == "":
			gold = 0
		else:
			gold = int( goldText )
		if silverText == "":
			silver = 0
		else:
			silver = int( silverText )
		if coinText == "":
			coin = 0
		else:
			coin = int( coinText )
		amount = gold*10000 + silver*100 + coin
		GUIFacade.changeSwapMoney( amount )
	# --------------------------------------------
	def onEvent( self, macroName, *args ) :
		"""
		triggering from client base
		"""
		self.__triggers[macroName]( *args )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onInvite( self, targetName ) :
		"""
		receive invite trading message
		"""
		# "%s�������㽻��"
		msg = mbmsgs[0x0782] % targetName
		self.__pyInviteBox = showAutoHideMessage( 30, msg, "", MB_YES_NO, self.__onTradeConfirmed )

	def __beginTrade( self, targetName ) :
		"""
		begin to trade
		"""
		fireEvent("EVT_ONTRADE_STATE_LEAVE", BigWorld.player().tradeState )
		BigWorld.player().tradeState = csdefine.TRADE_SWAP
		self.show()
		self.title = targetName
		self.__pyLbMyName.text = BigWorld.player().playerName
		self.__pyLbTargetName.text = targetName
		self.__clearBoxs()
		self.__clearTexts()
		self.__addTrap()	# ��ӶԻ�����
		#self.__pyTBMyMoney.readOnly = False

	def __endTrade( self ) :
		"""
		end trading
		"""
		self.__allowHide = True
		self.hide()
		self.__allowHide = False
		if BigWorld.player().tradeState == csdefine.TRADE_SWAP:
			BigWorld.player().tradeState = csdefine.TRADE_NONE
		self.__pyTargetIPanel.resumeItems()
		self.__pyMyIPanel.resumeItems()
		self.__pyMyTradeBtn.enable = True
		self.__delTrap()	# ɾ���Ի�����

	def __endTradeStraight( self ) :
		"""
		end trading
		"""
		self.__allowHide = True
		self.hide()
		GUIFacade.cancelSwapItem()		# ֱ��֪ͨ����ˣ����׽���
		self.__allowHide = False
		if BigWorld.player().tradeState == csdefine.TRADE_SWAP:
			BigWorld.player().tradeState = csdefine.TRADE_NONE
		self.__pyTargetIPanel.resumeItems()
		self.__pyMyIPanel.resumeItems()
		self.__pyMyTradeBtn.enable = True
		self.__delTrap()	# ɾ���Ի�����

	def __onRoleMoneyChange( self, oldMoney, newMoney ):
		"""
		��ɫ��Ǯ�ı��ˣ�ֱ�ӹرս��沢ȡ������
		"""
		if BigWorld.player().si_myState != csdefine.TRADE_SWAP_LOCKAGAIN: #�������˫��ȷ��״̬�����ܹر�
			self.__endTradeStraight()

	def onLeaveWorld( self ) :
		"""
		��ɫ�뿪����
		"""
		self.__endTrade()

	# -------------------------------------------------
	def __onTargetItemChanged( self, index, itemInfo ) :
		"""
		when an object item of target is changed, it will be called
		"""
		self.__pyTargetIPanel.updateItem( index, itemInfo )

	def __onTargetMoneyChanged( self, money ) :
		"""
		when target's money is changed, it will be called
		"""
		gold = money/10000
		silver = ( money/100 )%100
		coin = ( money%100 )%100
		self.__pyLbTargetGold.text = arithmetic.toUSValue( gold )
		self.__pyTargetSilver.text = arithmetic.toUSValue( silver )
		self.__pyTargetCoin.text = arithmetic.toUSValue( coin )

	def __onTargetStateChange( self, state ):
		"""
		���׶����״̬�ı�
		"""
		if state == csdefine.TRADE_SWAP_BEING :
			text = TARGET_UNLOCK
			colour = ( 255, 0, 0, 255 )
		else :
			text = TARGET_LOCK
			colour = ( 0, 255, 0, 255 )
		if state == csdefine.TRADE_SWAP_DEFAULT: #�ص�Ĭ��״̬
			if self.__pyInviteBox:
				self.__pyInviteBox.dispose()
		self.__pyTargetStateText.text = text
		self.__pyTargetStateText.getGui().colour = colour

	# -------------------------------------------------
	def __onMyItemChanged( self, index, itemInfo ) :
		"""
		when an object item of mine is changed, it will be called
		"""
		self.__pyMyIPanel.updateItem( index, itemInfo )

	def __onMyMoneyChanged( self, money ) :
		"""
		when my money is changed, it will be called
		"""
		self.__pyTBMyGold.onTextChanged.unbind( self.__moneyChange )
		self.__pyTBMySilver.onTextChanged.unbind( self.__moneyChange )
		self.__pyTBMyCoin.onTextChanged.unbind( self.__moneyChange )
		gold = money/10000
		silver = ( money/100 )%100
		coin = ( money%100 )%100
		self.__pyTBMyGold.text = arithmetic.toUSValue( gold )
		self.__pyTBMySilver.text = arithmetic.toUSValue( silver )
		self.__pyTBMyCoin.text = arithmetic.toUSValue( coin )
		self.__pyTBMyGold.onTextChanged.bind( self.__moneyChange )
		self.__pyTBMySilver.onTextChanged.bind( self.__moneyChange )
		self.__pyTBMyCoin.onTextChanged.bind( self.__moneyChange )

	def __onMyStateChange( self, state ):
		"""
		�Լ��Ľ���״̬�ı�
		"""
		#self.__pyMyOkBtn.enable = ( state == csdefine.TRADE_SWAP_BEING )
		self.__pyLockBtn.visible = ( state == csdefine.TRADE_SWAP_BEING )
		self.__pyUnlockBtn.visible = not self.__pyLockBtn.visible
		self.__pyMyTradeBtn.enable = ( state != csdefine.TRADE_SWAP_SURE )

	def __onStateLeave( self, state ):
		if state == csdefine.TRADE_SWAP:
			GUIFacade.cancelSwapItem()
			BigWorld.player().tradeState = csdefine.TRADE_NONE
			self.__endTrade()

	def __clearBoxs( self ):
		for pyBox in self.__pyMyBoxs:
			pyBox.clear()

	def __clearTexts( self ):
		for pyText in self.__pyTargetTexts:
			pyText.text = ""

	def __onTradeSwapAddItem( self, kitbagID, srcIndex ):
		"""
		�һ�������Ʒ����ӵ����׽���
		"""
		desIndex = self.__pyMyIPanel.getFirstIndex()
		if desIndex < 0:
			BigWorld.player().statusMessage( csstatus.ROLE_TRADE_OPERATER_NOT_ALLOW )
			return
		GUIFacade.changeSwapItem( desIndex, kitbagID, srcIndex )

	def __onClose( self ):
		showMessage( 0x0781, mbmsgs[0x0c22], MB_YES_NO, self.__onCancelTradeConfirmed, self )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onClose_( self ) :
		"""
		when the window is closed, it will be called
		"""
		if not self.visible : return True
		if self.__allowHide : return True
		# "ȡ������"
		GUIFacade.cancelSwapItem()
		return False

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onKeyDown_( self, key, mods ) :
		if key == KEY_RETURN and mods == 0 :
			for pyBox in self.__pyMyBoxs:
				if pyBox.tabStop:
					pyBox.tabStop = False
					return True
				else :
					return False
		return Window.onKeyDown_( self, key, mods )

	# -------------------------------------------------
	def __moneyChange( self ):
		subTradeState = BigWorld.player().si_myState
		if subTradeState == csdefine.TRADE_SWAP_DEFAULT:
			return
		goldText   = self.__pyTBMyGold.text.strip()
		silverText = self.__pyTBMySilver.text.strip()
		coinText   = self.__pyTBMyCoin.text.strip()
		if goldText != "" or silverText != "" or coinText != "":
			goldText   = goldText.replace( ",", "" )
			silverText = silverText.replace( ",", "" )
			coinText   = coinText.replace( ",", "" )
		if goldText == "":
			gold = 0
		else:
			gold = int( goldText )
		if silverText == "":
			silver = 0
		else:
			silver = int( silverText )
		if coinText == "":
			coin = 0
		else:
			coin = int( coinText )
		amount = gold*10000 + silver*100 + coin
		GUIFacade.changeSwapMoney( amount )

	def show( self ):
		Window.show( self )
		rds.helper.courseHelper.openWindow( "shejiao_chuangkou" )	# �������װ���

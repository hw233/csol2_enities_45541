# -*- coding: gb18030 -*-
#
# $Id: PetTrade.py,v 1.4 2008-08-13 08:05:12 fangpengjun Exp $

"""
implement PetTrade Window
"""

from guis import *
from guis.common.Window import Window
from TargetPanel import TargetPanel
from MyPanel import MyPanel
from guis.controls.ButtonEx import HButtonEx
from guis.controls.Button import Button
from guis.controls.TextBox import TextBox
from guis.controls.StaticText import StaticText
from LabelGather import labelGather
from event.EventCenter import *
from config.client.msgboxtexts import Datas as mbmsgs
from gbref import rds
import GUIFacade
import csdefine
import csconst


class PetTrade( Window ):

	def __init__( self ):
		wnd = GUI.load( "guis/general/pettrade/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )

		self.__allowHide = False
		self.__triggers = {}
		self.__registerTriggers()
		self.addToMgr()

		self.__trapID = 0	# 对话陷阱id
		self.__pyInviteBox = None

		mutexGroups = [ MutexGroup.TRADE1, MutexGroup.TRADE2, MutexGroup.PET1 ]
		rds.mutexShowMgr.addRootToMutexGroups( self, mutexGroups )				# 添加到多个互斥组

	def __initialize( self, wnd ):
		self.__pyLbTargetName = StaticText( wnd.targetName )					# label for showing target name
		self.__pyLbTargetName.text = ""
		self.__pyLbMyName = StaticText( wnd.myName )							# label for showing my name
		self.__pyLbMyName.text = ""

		self.__pyTargetTexts = []
		self.__pyLbTargetGold = TextBox( wnd.targetPanel.moneyPanel.goldBox )		# label for showing target money
		self.__pyLbTargetGold.text = "0"
		self.__pyTargetTexts.append( self.__pyLbTargetGold )

		self.__pyTargetSilver =TextBox( wnd.targetPanel.moneyPanel.silverBox )
		self.__pyTargetSilver.text = "0"
		self.__pyTargetTexts.append( self.__pyTargetSilver )

		self.__pyTargetCoin = TextBox( wnd.targetPanel.moneyPanel.coinBox )
		self.__pyTargetCoin.text = "0"
		self.__pyTargetTexts.append( self.__pyTargetCoin )

		self.__pyMyBoxs = []
		self.__pyTBMyGold = TextBox( wnd.myPanel.moneyPanel.goldBox, self )		# text box for input my money
		self.__pyTBMyGold.inputMode = InputMode.INTEGER
		self.__pyTBMyGold.filterChars = ['-', '+']
		self.__pyTBMyGold.maxLength = 7
#		self.__pyTBMyGold.onKeyDown.bind( self.__onEnterKeyDown )	# wsf
		self.__pyTBMyGold.onTextChanged.bind( self.__onMoneyChange )
		self.__pyMyBoxs.append( self.__pyTBMyGold )

		self.__pyTBMySilver = TextBox( wnd.myPanel.moneyPanel.silverBox, self )
		self.__pyTBMySilver.inputMode = InputMode.INTEGER
		self.__pyTBMySilver.filterChars = ['-', '+']
		self.__pyTBMySilver.maxLength = 2
#		self.__pyTBMySilver.onKeyDown.bind( self.__onEnterKeyDown )
		self.__pyTBMySilver.onTextChanged.bind( self.__onMoneyChange )
		self.__pyMyBoxs.append( self.__pyTBMySilver )

		self.__pyTBMyCoin = TextBox( wnd.myPanel.moneyPanel.coinBox, self )
		self.__pyTBMyCoin.inputMode = InputMode.INTEGER
		self.__pyTBMyCoin.filterChars = ['-', '+']
		self.__pyTBMyCoin.maxLength = 2
#		self.__pyTBMyCoin.onKeyDown.bind( self.__onEnterKeyDown )
		self.__pyTBMyCoin.onTextChanged.bind( self.__onMoneyChange )
		self.__pyMyBoxs.append( self.__pyTBMyCoin )

		self.__pyTargetOkBtn = HButtonEx( wnd.targetPanel.okBtn, self )
		self.__pyTargetOkBtn.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyTargetTradeBtn = HButtonEx( wnd.targetPanel.tradeBtn, self )
		self.__pyTargetTradeBtn.setExStatesMapping( UIState.MODE_R4C1 )

		self.__pyMyOkBtn = HButtonEx( wnd.myPanel.okBtn, self )
		self.__pyMyOkBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyMyOkBtn.onLClick.bind( self.__onOKAccept )

		self.__pyMyTradeBtn = HButtonEx( wnd.myPanel.tradeBtn, self )
		self.__pyMyTradeBtn.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyMyTradeBtn.onLClick.bind( self.__onMyTrade )

		self.__pyCloseBtn = Button( wnd.closeBtn, self )
		self.__pyCloseBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyCloseBtn.onLClick.bind( self.__onClose )

		self.__pyTargetpanel = TargetPanel( wnd.targetPanel, self )
		self.__pyMyPanel = MyPanel( wnd.myPanel, self )
		
		self.__pyStConfirm = StaticText(wnd.targetPanel.stConfirm,self)

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setPyBgLabel( self.__pyTargetTradeBtn, "petTrade:main", "TtradeBtn" )
		labelGather.setPyBgLabel( self.__pyTargetOkBtn, "petTrade:main", "TokBtn" )
		labelGather.setPyBgLabel( self.__pyMyTradeBtn, "petTrade:main", "MtradeBtn" )
		labelGather.setPyBgLabel( self.__pyMyOkBtn, "petTrade:main", "MokBtn" )

	def dispose( self ) :
		"""
		release resource
		"""
		self.__deregisterTriggers()
		Window.dispose( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		register event triggers
		"""
		self.__triggers["EVT_ON_RSI_INVITE_SWAP_PET"]	= self.__onInvite				# be invited
		self.__triggers["EVT_ON_RSI_SWAP_PET_BEGIN"] 	= self.__beginTrade				# begin to trade
		self.__triggers["EVT_ON_RSI_SWAP_ITEM_END"] 	= self.__endTrade				# end trading

		self.__triggers["EVT_ON_RSI_DST_PET_CHANGE"]	= self.__onTargetPetChange		# pet change
		self.__triggers["EVT_ON_RSI_DST_PET_REMOVE"]	= self.__onPetRemove			# pet remove
		self.__triggers["EVT_ON_RSI_DST_MONEY_CHANGED"]	= self.__onTargetMoneyChanged	# target money being changed
		self.__triggers["EVT_ON_RSI_DST_SWAP_STATE_CHANGED"] = self.__onTargetStateChange	# target confirmed

		self.__triggers[ "EVT_ON_RSI_SELF_PET_CHANGED" ] = self.__onMyPetChanged		# my pet changed
		self.__triggers[ "EVT_ON_RSI_SELF_MONEY_CHANGED" ] = self.__onMyMoneyChanged		# my money changed
		self.__triggers[ "EVT_ON_RSI_SELF_SWAP_STATE_CHANGED" ] = self.__onMyStateChange	# I confirmed
		self.__triggers["EVT_ONTRADE_STATE_LEAVE"] = self.__onStateLeave
		self.__triggers["EVT_ON_ROLE_DEAD"] = self.__endTrade								#角色死亡后隐藏窗口
		self.__triggers["EVT_ON_PET_TRADE_MUTEX"] = self.__endTrade							# 与宠物交易界面互斥，宠物交易界面关闭

		for macroName in self.__triggers.iterkeys():
			GUIFacade.registerEvent( macroName, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for macroName in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( macroName, self )

	# ----------------------------------------------------
	def __addTrap( self ):
		distance = csconst.COMMUNICATE_DISTANCE
		self.__trapID = BigWorld.player().addTrapExt( distance, self.__onEntitiesTrapThrough )

	def __delTrap( self ):
		if self.__trapID :
			BigWorld.player().delTrap( self.__trapID )				# 删除玩家的对话陷阱
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		target = BigWorld.player().si_getTargetEntity()	# 获得交易目标
		if target and target not in entitiesInTrap:		# 如果交易目标离开玩家对话陷阱
			GUIFacade.cancelSwapItem()
			self.__endTrade()

	def __onTradeConfirmed( self, id ) :
		"""
		show message box for trading confirmation
		"""
		BigWorld.player().si_replySwapPetInvite( id == RS_YES )

	def __onInvite( self, invitorName ):
		"""
		receive invite trading message
		"""
		# "%s请求与你宠物交易"
		msg = mbmsgs[0x0541] % invitorName
		self.__pyInviteBox = showAutoHideMessage( 30, msg, "", MB_YES_NO, callback = self.__onTradeConfirmed, gstStatus = Define.GST_IN_WORLD )

	def __beginTrade( self, invitorName ):
		fireEvent("EVT_ONTRADE_STATE_LEAVE", BigWorld.player().tradeState )
		BigWorld.player().tradeState = csdefine.TRADE_SWAP
		self.show()
		self.__pyLbTargetName.text = invitorName
		self.__pyLbMyName.text = BigWorld.player().playerName
		self.__pyMyPanel.onResumePanels()
		self.__pyTargetpanel.onResumePanels()
		self.__addTrap()
		self.__pyStConfirm.text = '对方未确认'
		self.__pyStConfirm.color = (255,255,0,255)

	def __endTrade( self ):
		self.__allowHide = True
		self.hide()
		self.__allowHide = False
		self.__pyMyPanel.onResumePanels()
		self.__pyTargetpanel.onResumePanels()
		self.__delTrap()	# 删除对话陷阱

	def __onTargetPetChange( self, epitome ):
		self.__pyTargetpanel.onPetChange( epitome )

	def __onPetRemove( self ):
		self.__pyTargetpanel.onResumePanels()

	def __onTargetStateChange( self, state ):
		"""
		交易对象的状态改变
		"""
		self.__pyTargetOkBtn.enable = ( state == csdefine.TRADE_SWAP_PET_BEING )
		self.__pyTargetTradeBtn.enable = ( state != csdefine.TRADE_SWAP_SURE )
		if state == csdefine.TRADE_SWAP_PET_LOCK:
			self.__pyStConfirm.text = '对方已确认'
			self.__pyStConfirm.color = (0,255,0,255)
		if state == csdefine.TRADE_SWAP_PET_BEING:
			self.__pyStConfirm.text = '对方未确认'
			self.__pyStConfirm.color = (255,255,0,255)
		if state == csdefine.TRADE_SWAP_DEFAULT:
			if self.__pyInviteBox:
				self.__pyInviteBox.dispose()
				
	def __onTargetMoneyChanged( self, money ):
		"""
		when target's money is changed, it will be called
		"""
		gold = money/10000
		silver = ( money/100 )%100
		coin = ( money%100 )%100
		self.__pyLbTargetGold.text = arithmetic.toUSValue( gold )
		self.__pyTargetSilver.text = arithmetic.toUSValue( silver )
		self.__pyTargetCoin.text = arithmetic.toUSValue( coin )

	def __onMyPetChanged( self, dbid ):
		self.__pyMyPanel.onPetChange( dbid )

	def __onMyMoneyChanged( self, money ):
		"""
		when my money is changed, it will be called
		"""
		self.__pyTBMyGold.onTextChanged.unbind( self.__onMoneyChange )
		self.__pyTBMySilver.onTextChanged.unbind( self.__onMoneyChange )
		self.__pyTBMyCoin.onTextChanged.unbind( self.__onMoneyChange )
		gold = money/10000
		silver = ( money/100 )%100
		coin = ( money%100 )%100
		self.__pyTBMyGold.text = arithmetic.toUSValue( gold )
		self.__pyTBMySilver.text = arithmetic.toUSValue( silver )
		self.__pyTBMyCoin.text = arithmetic.toUSValue( coin )
		self.__pyTBMyGold.onTextChanged.bind( self.__onMoneyChange )
		self.__pyTBMySilver.onTextChanged.bind( self.__onMoneyChange )
		self.__pyTBMyCoin.onTextChanged.bind( self.__onMoneyChange )

	def __onMyStateChange( self, state ):
		"""
		自己的交易状态改变
		"""
		if state == csdefine.TRADE_SWAP_PET_BEING:
			self.__pyStConfirm.text = '对方未确认'
			self.__pyStConfirm.color = (255,255,0,255)
		self.__pyMyOkBtn.enable = ( state == csdefine.TRADE_SWAP_PET_BEING )
		self.__pyMyTradeBtn.enable = ( state != csdefine.TRADE_SWAP_SURE )
		self.__pyMyPanel.setState( state )

	def __onStateLeave( self, state ):
		if state == csdefine.TRADE_SWAP:
			GUIFacade.cancelSwapItem()
			BigWorld.player().tradeState = csdefine.TRADE_NONE
			self.__endTrade()

	def __onOKAccept( self ):
		BigWorld.player().si_acceptPet()

	def __onMyTrade( self ):
		if self.__pyTargetOkBtn.enable:
			HACK_MSG( "对方还没有锁定。" )
			return
		BigWorld.player().si_secondAcceptPet()

#	def __onEnterKeyDown( self, key, mods ):
#		if key == KEY_RETURN and mods == 0 :
#			goldText = self.__pyTBMyGold.text.strip()
#			silverText = self.__pyTBMySilver.text.strip()
#			coinText = self.__pyTBMyCoin.text.strip()
#			if goldText == "":
#				gold = 0
#			else:
#				gold = int( goldText )
#			if silverText == "":
#				silver = 0
#			else:
#				silver = int( silverText )
#			if coinText == "":
#				coin = 0
#			else:
#				coin = int( coinText )
#			amount = gold*10000 + silver*100 + coin
#			GUIFacade.changeSwapMoney( amount )

	def __onMoneyChange( self ):
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

	def __onClose( self ):
		"""
		"取消交易"
		"""
		showMessage( 0x0542, "", MB_YES_NO, self.__onCancelTradeConfirmed, self )

	def __onCancelTradeConfirmed( self, btnID ) :
		"""
		show messagebox for cancel trading confirmation
		"""
		if btnID == RS_YES :
			GUIFacade.cancelSwapItem()
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onClose_( self ) :
		"""
		when the window is closed, it will be called
		"""
#		if not self.visible : return True
#		if self.__allowHide : return True
#		def query( rs_id ):
#			if rs_id == RS_YES:
#				GUIFacade.cancelSwapItem()
#		showMessage( "取消交易", "", MB_YES_NO, query )
#		return True
		if not self.visible : return True
		if self.__allowHide : return True
		GUIFacade.cancelSwapItem()
		return False
	# ---------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		"""
		triggering from client base
		"""
		self.__triggers[macroName]( *args )

	def onLeaveWorld( self ) :	# wsf add
		"""
		角色离开世界
		"""
		self.__endTrade()

	def show( self ):
		self.__pyMyPanel.initPetsCB()
		Window.show( self )

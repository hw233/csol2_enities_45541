# -*- coding: gb18030 -*-
#
# $Id: SellPanel.py,v 1.3 2008-09-05 08:05:00 fangpengjun Exp $
# rewritten by ganjinxing 2010-01-19

from guis import *
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabButton
from guis.controls.Button import Button
from guis.controls.TabCtrl import TabPanel
from guis.tooluis.CSRichText import CSRichText
from guis.controls.StaticText import StaticText
from guis.tooluis.inputbox.InputBox import InputBox
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
from PetsPanel import VendPetPanel
from GoodsPanel import VendGoodsPanel
from PurchasePanel import VendPurchasePanel
from LabelGather import labelGather
from config.client.msgboxtexts import Datas as mbmsgs
import csdefine
import csconst
import csstatus
import math

STALL_CELL = 0.01


class BaseSellPanel( TabPanel ):
	def __init__( self, tabPanel, pyBinder = None ):
		TabPanel.__init__( self, tabPanel, pyBinder )

		self.isVendSellMode_ = True									# ��¼��ǰ���չ����ǳ���ģʽ
		self.triggers_ = {}
		self.registerTriggers_()
		self.initialize_( tabPanel )

	def initialize_( self, tabPanel ):
		self.pyStartVendBtn_ = Button( tabPanel.startVendBtn ) 		# ��ʼ��̯
		self.pyStartVendBtn_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyStartVendBtn_.onLClick.bind( self.onStartvend_ )

		self.pyPauseVendBtn_ = Button( tabPanel.pauseVendBtn ) 		# ��ͣ��̯
		self.pyPauseVendBtn_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyPauseVendBtn_.onLClick.bind ( self.onPauseVend_ )
		self.pyPauseVendBtn_.visible = False

		self.pyChangePriceBtn_ = Button( tabPanel.changeBtn ) 		# ������Ʒ�۸�
		self.pyChangePriceBtn_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyChangePriceBtn_.onLClick.bind( self.onChangePrice_ )
		self.pyChangePriceBtn_.enable = False

		self.pyStOwnerName_ = StaticText( tabPanel.stOwnerName ) 	# ̯������
		self.pyStOwnerName_.text = ""

		self.pyRtStallTax_ = CSRichText( tabPanel.rtStallTax ) 		# ̯˰
		self.pyRtStallTax_.text = labelGather.getText( "vendwindow:BaseSellPanel", "rtStallTax" ) + "0"
		#self.pyRtStallTax_.foreColor = ( 255, 255, 0, 255 )

		self.pyStCell_ = StaticText( tabPanel.stCess ) 				# ˰��
		self.pyStCell_.text = labelGather.getText( "vendwindow:BaseSellPanel", "stCess" )%( STALL_CELL * 100 )

		#self.pyRtTotalPrice_ = CSRichText( tabPanel.rtTotalPrice ) 	# �ܼ�Ǯ
		#self.pyRtTotalPrice_.text = labelGather.getText( "vendwindow:BaseSellPanel", "rtTotalPrice" ) + "0"
		#self.pyRtTotalPrice_.foreColor = ( 6, 228, 192, 255 )

		self.pyMoneyBar_ = MoneyBar( tabPanel.moneybox_total )
		self.pyMoneyBar_.readOnly = True
		self.pyMoneyBar_.money = 0

		self.initTabCtrl_( tabPanel.subTab )

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.pyStartVendBtn_, "vendwindow:BaseSellPanel", "btnStartVend" )
		labelGather.setPyBgLabel( self.pyPauseVendBtn_, "vendwindow:BaseSellPanel", "btnPauseVend" )
		labelGather.setPyBgLabel( self.pyChangePriceBtn_, "vendwindow:BaseSellPanel", "btnChangePrice" )
		labelGather.setLabel( tabPanel.st_total, "vendwindow:BaseSellPanel", "rtTotalPrice" )


	# ---------------------------------------------------------------------
	# pravite
	# ---------------------------------------------------------------------
	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ):
		pass

	def initTabCtrl_( self, subTab ):
		for index, pyBtn in enumerate( self.pySubCtrl_.pyBtns ) :
			labelGather.setPyBgLabel( pyBtn, "vendwindow:BaseSellPanel", "subTabBtn_%i" % index )

	def onTabSelectChanged_( self ) :
		self.enableChangePriceBtn()

	def onStallTaxChange_( self, tax ):
		self.pyRtStallTax_.text = str( tax )

	def onTaxRatioChange_( self, taxRatio ):
		self.pyStCell_.text = labelGather.getText( "vendwindow:BaseSellPanel", "stCess" )%( taxRatio * 100 )

	def onChangePrice_( self ):
		selTabPage = self.pySubCtrl_.pySelPage
		selTabPanel = selTabPage.pyPanel 										# ��ȡ��ǰѡ���ҳ��
		selTabPanel.changeItemPrice()

	def onCalcuExpense_( self ):
		"""
		�������ۼۺ�̯˰
		"""
		if not self.isVendSellMode_ : return
		cost = 0
		for pyPanel in self.pySubCtrl_.pyPanels :
			cost += pyPanel.getTotalPrice()
		stallTax = int( math.ceil( cost * STALL_CELL ) )
		self.pyMoneyBar_.money = cost
		#costStr = utils.currencyToViewText( cost )
		#self.pyRtTotalPrice_.text = labelGather.getText( "vendwindow:BaseSellPanel", "rtTotalPrice" ) + ( costStr == "" and "0" or costStr )
		costStr = utils.currencyToViewText( stallTax )
		self.pyRtStallTax_.text = labelGather.getText( "vendwindow:BaseSellPanel", "rtStallTax" ) + ( costStr == "" and "0" or costStr )
		labelGather.setLabel( self.gui.st_total, "vendwindow:BaseSellPanel", "rtTotalPrice" )

	def onUpdatePurchaseCost_( self, cost ) :
		"""
		�����չ���Ʒ�۸�
		"""
		if self.isVendSellMode_ : return
		self.pyMoneyBar_.money = cost
		labelGather.setLabel( self.gui.st_total, "vendwindow:BaseSellPanel", "rtPurchaseCost" )
		#costStr = utils.currencyToViewText( cost )
		#self.pyRtTotalPrice_.text = labelGather.getText( "vendwindow:BaseSellPanel", "rtPurchaseCost" ) + ( costStr == "" and "0" or costStr )

	def onSwitchVendMode_( self, isVendSellMode ) :
		"""
		�л�����ģʽ/�չ�ģʽ
		"""
		self.isVendSellMode_ = isVendSellMode
		self.pyStCell_.visible = isVendSellMode
		self.pyRtStallTax_.visible = isVendSellMode


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.triggers_[eventMacro]( *args )

	def enableChangePriceBtn( self ) :
		self.pyChangePriceBtn_.enable = True

	def reset( self ):
		self.pyMoneyBar_.money = 0
		self.pyRtStallTax_.text = labelGather.getText( "vendwindow:BaseSellPanel", "rtStallTax" ) + "0"
		#self.pyRtTotalPrice_.text = labelGather.getText( "vendwindow:BaseSellPanel", "rtTotalPrice" ) + "0"
		for pyPanel in self.pySubCtrl_.pyPanels :
			pyPanel.reset()


class VendSellPanel( BaseSellPanel ) :


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ):
		self.triggers_["EVT_ON_ROLE_STATE_CHANGED"] 		= self.__onRoleStateChange		# ���״̬�ı�
		self.triggers_["EVT_ON_STALL_TAX_CHANGE"] 			= self.onStallTaxChange_ 		# ̯λ˰
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )

	def initialize_( self, tabPanel ) :
		self.__pyEndVendBtn = Button( tabPanel.endVendBtn ) 					# ������̯
		self.__pyEndVendBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyEndVendBtn.onLClick.bind( self.__onEndVend )

		self.__pyChangeNameBtn = Button( tabPanel.changeNameBtn ) 				# ��̯λ����
		self.__pyChangeNameBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyChangeNameBtn.onLClick.bind( self.__onChangeName )
		self.__pyChangeNameBtn.enable = False

		tabPanel.remainTime.visible = False
		tabPanel.cb_stallModel.visible = False

		BaseSellPanel.initialize_( self, tabPanel )

		# -------------------------------------------------
		# ���ñ�ǩ
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pyEndVendBtn, "vendwindow:VendSellPanel", "btnEndVend" )
		labelGather.setPyBgLabel( self.__pyChangeNameBtn, "vendwindow:VendSellPanel", "btnChangeSignboard" )

	def initTabCtrl_( self, subTab ):
		self.pySubCtrl_ = TabCtrl( subTab )
		self.pySubCtrl_.onTabPageSelectedChanged.bind( self.onTabSelectChanged_ )
		self.pyGoodsPanel_ = self.__createTabPage( subTab, VendGoodsPanel, 0 )
		self.pyPetsPanel_ = self.__createTabPage( subTab, VendPetPanel, 1 )
		self.pyPurchasePanel_ = self.__createTabPage( subTab, VendPurchasePanel, 2 )
		BaseSellPanel.initTabCtrl_( self, subTab )

	def onStartvend_( self ):
		player = BigWorld.player()
		if player.getState() == csdefine.ENTITY_STATE_FIGHT:
			player.statusMessage( csstatus.VEND_FORBIDDEN_VEND_ON_FIGHTING )
			return
		if player.getState() == csdefine.ENTITY_STATE_DEAD:
			player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
			return
		if player.isMoving() or player.isJumping():
			player.statusMessage( csstatus.VEND_FORBIDDEN_VEND_ON_MOVING )
			return
		if player.intonating():													# �����в������̯
			player.statusMessage( csstatus.VEND_FORBIDDEN_VEND_ON_INTONATE )
			return

		kitUidList = []
		uidList = []
		itemsPrice = []
		petsList = []
		petsPrice = []
		vendItems = self.pyGoodsPanel_.getSellItems()							# ������Ʒ
		for itemInfo in vendItems :
			if itemInfo.rolePrice > csconst.TRADE_PRICE_UPPER_LIMIT :
				# "��Ʒ(%s)��۳�������!"
				showAutoHideMessage( 3.0, mbmsgs[0x0e01] % itemInfo.name(), mbmsgs[0x0c22], pyOwner = self )
				return
			uidList.append( itemInfo.uid )
			kitUidList.append( itemInfo.kitbagID )
			itemsPrice.append( itemInfo.rolePrice )

		vendPets = self.pyPetsPanel_.getVendPets()								# ���۳���
		for petEpitome in vendPets :
			price = petEpitome.rolePrice
			if price > csconst.TRADE_PRICE_UPPER_LIMIT :
				# "�����۳�������!"
				showAutoHideMessage( 3.0, 0x0e02, mbmsgs[0x0c22], pyOwner = self )
				return
			petsList.append( petEpitome.databaseID )
			petsPrice.append( price )

		if 0 in itemsPrice or 0 in petsPrice : 									# �۸��б��д��ڼ۸�Ϊ0����Ʒ
			# "������Ʒ��δ���!"
			showAutoHideMessage( 3.0, 0x0e03, mbmsgs[0x0c22], pyOwner = self )
			return

		purchaseItems = self.pyPurchasePanel_.getPurchaseItems()				# �չ���Ʒ
		if len( vendItems ) < 1 and len( vendPets ) < 1 and len( purchaseItems ) < 1 :
			# "û�г��ۻ��չ�����Ʒ!"
			showAutoHideMessage( 3.0, 0x0e04, mbmsgs[0x0c22], pyOwner = self )
			return
		if self.pyPurchasePanel_.getPurchaseTotalPrice() > player.money : 		# ����Ǯȥ�չ���Ʒ
			# "��û���㹻�Ľ�Ǯ�չ���Ʒ!"
			showAutoHideMessage( 3.0, 0x0e05, mbmsgs[0x0c22], pyOwner = self )
			return
		player.vend_vend( kitUidList, uidList, itemsPrice, petsList, petsPrice )

	def onPauseVend_( self ):
		player = BigWorld.player()
		player.vend_pauseVend()
		player.tradeState = csdefine.ENTITY_STATE_VEND


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onRoleStateChange( self, state ):
		"""
		���״̬�ı�
		"""
		isVendState = state == csdefine.ENTITY_STATE_VEND
		self.__pyChangeNameBtn.enable = isVendState
		self.pyPauseVendBtn_.visible = isVendState
		self.pyStartVendBtn_.visible = not isVendState
		self.enableChangePriceBtn()
		for pyPanel in self.pySubCtrl_.pyPanels :
			pyPanel.onRoleTradeStateChanged( state )

	def __createTabPage( self, tabCtrl, panelClass, index ) :
		tabBtn = getattr( tabCtrl, "btn_" + str( index ) )
		pyTabBtn = TabButton( tabBtn )
		tabPanel = getattr( tabCtrl, "panel_" + str( index ) )
		pyTabPanel = panelClass( tabPanel, self )
		self.pySubCtrl_.addPage( TabPage( pyTabBtn, pyTabPanel ) )
		return pyTabPanel

	def __onChangeName( self ):
		def operationCB( res, text ) :
			if res == DialogResult.OK :
				text = text.strip()
				if len( text ) > csconst.VEND_SIGNBOARD_MAX_LENGTH :						# wsf,����������ֺϷ��Լ��
					# "���ֳ��Ȳ��ܳ��� 20���ֽڣ�"
					showAutoHideMessage( 3.0, 0x0e06, mbmsgs[0x0c22] )
				elif text == "" :
					# "�������������Ч��"
					showAutoHideMessage( 3.0, 0x0e07, mbmsgs[0x0c22] )
				elif not rds.wordsProfanity.isPureString( text ) :
					# "���Ʋ��Ϸ���"
					showAutoHideMessage( 3.0, 0x0e08, mbmsgs[0x0c22] )
				elif rds.wordsProfanity.searchNameProfanity( text ) is not None :
					# "����������н��ôʻ�!"
					showAutoHideMessage( 3.0, 0x0e09, mbmsgs[0x0c22] )
				else :
					BigWorld.player().vend_setSignboard( text )
		title = labelGather.getText( "vendwindow:VendSellPanel", "ipBoxClew" )
		pyIPBox = InputBox()
		pyIPBox.maxLength = 20
		pyIPBox.show( title, operationCB, self )

	def __onEndVend( self ):
		BigWorld.player().vend_endVend()
		self.pyBinder.hide()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def enableChangePriceBtn( self ) :
		"""
		ʹ���޸ļ۸�ť
		"""
		selTabPage = self.pySubCtrl_.pySelPage
		if selTabPage is None : return
		player = BigWorld.player()
		if not player or not player.isPlayer() : return
		selPanel = selTabPage.pyPanel
		enable = player.state != csdefine.ENTITY_STATE_VEND
		enable &= selPanel.canChangePrice()
		self.pyChangePriceBtn_.enable = enable

	def reset( self ):
		BaseSellPanel.reset( self )
		self.__onRoleStateChange( csdefine.TRADE_NONE )

	def onParentShow( self ) :
		player = BigWorld.player()
		self.__onRoleStateChange( player.state )
		self.pyStOwnerName_.text = labelGather.getText( "vendwindow:VendSellPanel", "stOwnerName" ) + player.getName()
		for pyPanel in self.pySubCtrl_.pyPanels :
			pyPanel.onParentShow()

	def onParentHide( self ) :
		for pyPanel in self.pySubCtrl_.pyPanels :
			pyPanel.onParentHide()

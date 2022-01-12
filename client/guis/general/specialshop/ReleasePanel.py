# -*- coding: gb18030 -*-
#
# $Id: ReleasePanel.py, fangpengjun Exp $

"""
implement ReleasePanel panel class
订单发布面板
"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.TabCtrl import TabPanel
from guis.controls.Button import Button
from guis.controls.TextBox import TextBox
from guis.controls.StaticText import StaticText
from config.client.msgboxtexts import Datas as mbmsgs
import utils

class ReleasePanel( TabPanel ):
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pySellPanel = SellSetting( panel.sellPanel )
		self.__pyBuyPanel = BuySetting( panel.buyPanel )
		self.__pyInfoPanel = InfoPanel( panel.infoPanel )

	# ------------------------------------------------------------
	# private
	# ------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_YBT_SHOW_ACC_MON"]	= self.__onMoneyChange
		self.__triggers["EVT_ON_YBT_SHOW_ACC_YB"]	= self.__onGoldChange
		self.__triggers["EVT_ON_YBT_NEW_BUY_BILL"]	= self.__onEstablishBuyBill
		self.__triggers["EVT_ON_YBT_NEW_SELL_BILL"]	= self.__onEstablishSellBill
		self.__triggers["EVT_ON_YBT_DRAW_YB_SUCCESS"] = self.__onDrawYBSucc
		self.__triggers["EVT_ON_YBT_DRAW_MONEY_SUCCESS"] = self.__onDrawMoneySucc

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )
	# --------------------------------------------------------------
	def __onMoneyChange( self, money ):
		"""
		角色账户金钱
		"""
		self.__pyInfoPanel.onMoneyChange( money )
	
	def __onGoldChange( self, gold ):
		"""
		角色账户元宝
		"""
		self.__pyInfoPanel.onGoldChange( gold )
	
	def __onEstablishBuyBill( self ):
		"""
		创建求购订单回调
		"""
		self.__pyBuyPanel.onEstablishBuyBill()
	
	def __onEstablishSellBill( self ):
		"""
		创建寄售订单单回调
		"""
		self.__pySellPanel.onEstablishSellBill()
	
	def __onDrawYBSucc( self ):
		"""
		成功取出元宝回调
		"""
		self.__pyInfoPanel.onDrawYBSucc()
	
	def __onDrawMoneySucc( self ):
		"""
		成功取出金钱回调
		"""
		self.__pyInfoPanel.onDrawMoneySucc()

	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )
	
	def onSelected( self ):
		player = BigWorld.player()
		player.getBalanceMoney()
		player.getBalanceYB()
	
	def onLeaveWorld( self ):
		self.__pySellPanel.onLeaveWorld()
		self.__pyBuyPanel.onLeaveWorld()
# ---------------------------------------------------------------------
# 账户信息面板
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
class InfoPanel( PyGUI ):
	def __init__( self, panel ):
		PyGUI.__init__( self, panel )
		self.__pyRtMoney = CSRichText( panel.rtMoney )
		self.__pyRtMoney.text = ""
		
		self.__pyRtGold = CSRichText( panel.rtGold )
		self.__pyRtGold.text = ""
		
		self.__pyDrawMoney = Button( panel.drawMoney )
		self.__pyDrawMoney.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyDrawMoney.onLClick.bind( self.__onDrawMoney )
		labelGather.setPyBgLabel( self.__pyDrawMoney, "SpecialShop:ReleasePanel", "btnWithdraw" )

		self.__pyDrawGold = Button( panel.drawGold )
		self.__pyDrawGold.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyDrawGold.onLClick.bind( self.__onDrawGold )
		labelGather.setPyBgLabel( self.__pyDrawGold, "SpecialShop:ReleasePanel", "btnWithdraw" )
		
		labelGather.setLabel( panel.stTitle, "SpecialShop:ReleasePanel", "tradeAccount" )
		labelGather.setLabel( panel.gameMoney, "SpecialShop:ReleasePanel", "accountMoney" )
		labelGather.setLabel( panel.gameGold, "SpecialShop:ReleasePanel", "accountGold" )

	def __onDrawMoney( self ):
		"""
		取出金钱
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().drawMoney()
		showMessage( mbmsgs[0x07eb], "", MB_OK_CANCEL, query, self )
		return True
	
	def __onDrawGold( self ):
		"""
		取出元宝
		"""
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().drawYB()
		showMessage( mbmsgs[0x07ec], "", MB_OK_CANCEL, query, self )
		return True

	def onMoneyChange( self, coin ):
		coinIcon = PL_Image.getSource( "guis_v2/controls/coinicon.gui" )
		coinText = utils.currencyToViewText( coin )
		self.__pyRtMoney.text = PL_Font.getSource( coinText, fc = ( 232, 53, 241 ) )
		self.__pyDrawMoney.enable = coin > 0
	
	def onGoldChange( self, gold ):
		ybIcon = PL_Image.getSource( "guis/general/specialshop/yuanbao.gui" )
		self.__pyRtGold.text = PL_Font.getSource( "%d%s"%( gold, ybIcon ), fc = ( 255, 248, 158 ) )
		self.__pyDrawGold.enable = gold > 0
	
	def onDrawYBSucc( self ):
		ybIcon = PL_Image.getSource( "guis/general/specialshop/yuanbao.gui" )
		self.__pyRtGold.text = PL_Font.getSource( "%d%s"%( 0, ybIcon ), fc = ( 255, 248, 158 ) )
		self.__pyDrawGold.enable = False
	
	def onDrawMoneySucc( self ):
		coinIcon = PL_Image.getSource( "guis_v2/controls/coinicon.gui" )
		self.__pyRtMoney.text = PL_Font.getSource( "%d%s"%( 0, coinIcon ), fc = ( 232, 53, 241 ) )
		self.__pyDrawMoney.enable = False
# -----------------------------------------------------------------
class SettingPanel( PyGUI ):
	def __init__( self, panel,  ):
		PyGUI.__init__( self, panel )
		self.pyNumberBox_ = TextBox( panel.numberBox.box )
		self.pyNumberBox_.text = ""
		self.pyNumberBox_.maxLength = 4
		self.pyNumberBox_.inputMode = InputMode.INTEGER
		self.pyNumberBox_.filterChars = ["-", "+"]
		
		self.pyTotalPanel_ = MoneyPanel( panel.totalPanel )
		self.pyTotalPanel_.setBoxText( 0 )
		
		self.pyFeePanel_ = MoneyPanel( panel.feePanel )
		self.pyFeePanel_.setBoxText( 0 )
		
		self.pyIncomePanel_ = MoneyPanel( panel.incomePanel )
		self.pyIncomePanel_.setBoxText( 0 )
		
		labelGather.setLabel( panel.orderTime, "SpecialShop:ReleasePanel", "tradeTime" )
		labelGather.setLabel( panel.ybUnit, "SpecialShop:ReleasePanel", "rateText" )
		
		self.pyBtnConfirm_ = Button( panel.btnConfirm )
		self.pyBtnConfirm_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyBtnConfirm_.enable = False

	def onLeaveWorld( self ):
		self.onHide()

	def onHide( self ):
		self.pyNumberBox_.text = ""
		self.pyTotalPanel_.setBoxText(0)
		self.pyFeePanel_.setBoxText(0)
		self.pyIncomePanel_.setBoxText(0)
		self.pyBtnConfirm_.enable = False

# --------------------------------------------------------------------
UNIT_LIMIT = 2500000		# 单价上限
UNIT_LOWER_LIMIT = 200000	# 单价下限
GOLD_LIMIT = 1000			# 元宝上限

# 出售设置
class SellSetting( SettingPanel ):
	def __init__( self, panel ):
		SettingPanel.__init__( self, panel )
		self.__pyUnitPanel = UnitPanel( panel.unitPanel, self )
		self.pyNumberBox_.onTextChanged.bind( self.__onSellNumChange )
		self.pyBtnConfirm_.onLClick.bind( self.__onConfirm )
		labelGather.setPyBgLabel( self.pyBtnConfirm_, "SpecialShop:ReleasePanel", "confirmSell" )
		
		labelGather.setLabel( panel.stTitle, "SpecialShop:ReleasePanel", "sellSetting" )
		labelGather.setLabel( panel.unitText, "SpecialShop:ReleasePanel", "sellUnit" )
		labelGather.setLabel( panel.numberText, "SpecialShop:ReleasePanel", "sellNumber" )
		labelGather.setLabel( panel.totalAmount, "SpecialShop:ReleasePanel", "totalText" )
		labelGather.setLabel( panel.feeText, "SpecialShop:ReleasePanel", "feeText" )
		labelGather.setLabel( panel.totalIncome, "SpecialShop:ReleasePanel", "totalIncome" )
	
	def __onSellNumChange( self ):
		unitPrice = self.__pyUnitPanel.getUnitPrice()
		if unitPrice > 0:
			sellNumber = 0
			if self.pyNumberBox_.text != "":
				sellNumber = int( self.pyNumberBox_.text )
			gold = BigWorld.player().gold
			self.pyBtnConfirm_.enable = sellNumber <= GOLD_LIMIT and sellNumber >0
			if sellNumber > GOLD_LIMIT:
				showAutoHideMessage( 3.0, mbmsgs[0x07e7], "", pyOwner = self )
				sellNumber = GOLD_LIMIT
				self.pyNumberBox_.text = str( sellNumber )
			totalPrice = unitPrice*sellNumber
			self.pyTotalPanel_.setBoxText( totalPrice )
			fee = int( unitPrice*0.01 )*sellNumber
			self.pyFeePanel_.setBoxText( fee )
			self.pyIncomePanel_.setBoxText( totalPrice - fee )
	
	def __onConfirm( self ):
		unitPrice = self.__pyUnitPanel.getUnitPrice( )
		if unitPrice <= 0:return
		if self.pyNumberBox_.text == "":return
		yuanbao = int( self.pyNumberBox_.text )
		if unitPrice > UNIT_LIMIT:
			self.__pyUnitPanel.setLtUnit( False )
			showAutoHideMessage( 3.0, mbmsgs[0x07e6], "", pyOwner = self )
			return
		if yuanbao > GOLD_LIMIT:
			showAutoHideMessage( 3.0, mbmsgs[0x07e7], "", pyOwner = self )
			self.pyNumberBox_.pyLText_.text = "%d"%GOLD_LIMIT
			return
		if BigWorld.player().gold < yuanbao*100:
			showAutoHideMessage( 3.0, mbmsgs[0x07e8], "", pyOwner = self )
			return
		BigWorld.player().establishSellBillRequest( yuanbao )
	
	def onUnitPriceChange( self, unitPrice ):
		if self.pyNumberBox_.text != "":
			sellNumber = int( self.pyNumberBox_.text )
			self.pyBtnConfirm_.enable = unitPrice > 0 and \
			sellNumber <= GOLD_LIMIT
			totalPrice = unitPrice*sellNumber
			self.pyTotalPanel_.setBoxText( totalPrice )
			fee = int( unitPrice*0.01 )*sellNumber
			self.pyFeePanel_.setBoxText( fee )
			self.pyIncomePanel_.setBoxText( totalPrice - fee )
	
	def onEstablishSellBill( self ):
		yuanbao = int( self.pyNumberBox_.text )
		unitPrice = self.__pyUnitPanel.getUnitPrice()
		fee = int( unitPrice*0.01 )*yuanbao
		priceStr = ""
		feeStr = ""
		priceGold = unitPrice/10000
		priceSilver = ( unitPrice%10000 )/100
		priceCoin = ( unitPrice%10000 )%100
		feeGold = fee/10000
		feeSilver = ( fee%10000 )/100
		feeCoin = ( fee%10000 )%100
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().establishSellBill( yuanbao, unitPrice )
		if int( priceGold ) > 0:
			priceStr += "%d%s"%( priceGold, PL_Image.getSource( "guis_v2/controls/goldicon.gui" ) )
		if int( priceSilver ) > 0:
			priceStr += "%d%s"%( priceSilver, PL_Image.getSource( "guis_v2/controls/silvericon.gui" ) )
		if priceCoin > 0:
			priceStr += "%d%s"%( priceCoin, PL_Image.getSource( "guis_v2/controls/coinicon.gui" ) )
		if int( feeGold ) > 0:
			feeStr += "%d%s"%( feeGold, PL_Image.getSource( "guis_v2/controls/goldicon.gui" ) )
		if int( feeSilver ) > 0:
			feeStr += "%d%s"%( feeSilver, PL_Image.getSource( "guis_v2/controls/silvericon.gui" ) )
		if feeCoin > 0:
			feeStr += "%d%s"%( feeCoin, PL_Image.getSource( "guis_v2/controls/coinicon.gui" ) )
		showMessage( mbmsgs[0x07e4]%( feeStr, priceStr, yuanbao*100 ), "", MB_OK_CANCEL, query, self )
		return True
	
	def onHide( self ):
		self.__pyUnitPanel.resetBox()
		SettingPanel.onHide( self )

# ---------------------------------------------------------------------
# 购买设置
class BuySetting( SettingPanel ):
	def __init__( self, panel ):
		SettingPanel.__init__( self, panel )
		self.__pyUnitPanel = UnitPanel( panel.unitPanel, self )
		self.pyNumberBox_.onTextChanged.bind( self.__onBuyNumChange )
		self.pyBtnConfirm_.onLClick.bind( self.__onConfirm )
		labelGather.setPyBgLabel( self.pyBtnConfirm_, "SpecialShop:ReleasePanel", "confirmBuy" )
		labelGather.setLabel( panel.stTitle, "SpecialShop:ReleasePanel", "buySetting" )
		labelGather.setLabel( panel.unitText, "SpecialShop:ReleasePanel", "buyUnit" )
		labelGather.setLabel( panel.numberText, "SpecialShop:ReleasePanel", "buyNumber" )
		labelGather.setLabel( panel.totalAmount, "SpecialShop:ReleasePanel", "totalText" )
		labelGather.setLabel( panel.feeText, "SpecialShop:ReleasePanel", "feeText" )
		labelGather.setLabel( panel.totalIncome, "SpecialShop:ReleasePanel", "totalExpend" )
	
	def __onConfirm( self ):
		unitPrice = self.__pyUnitPanel.getUnitPrice()
		if unitPrice <= 0:return
		if self.pyNumberBox_.text == "":return
		yuanbao = int( self.pyNumberBox_.text )
		if unitPrice < UNIT_LOWER_LIMIT:
			showAutoHideMessage( 3.0, mbmsgs[0x07ea], "", pyOwner = self )
			self.__pyUnitPanel.setLtUnit( True )
			return
		if yuanbao > GOLD_LIMIT:
			showAutoHideMessage( 3.0, mbmsgs[0x07e9], "", pyOwner = self )
			self.pyNumberBox_.pyLText_.text = "%d"%GOLD_LIMIT
			return
		BigWorld.player().establishBuyBillRequest( yuanbao, unitPrice )
	
	def __onBuyNumChange( self ):
		unitPrice = self.__pyUnitPanel.getUnitPrice()
		if unitPrice > 0:
			buyNumber = 0
			if self.pyNumberBox_.text != "":
				buyNumber = int( self.pyNumberBox_.text )
			self.pyBtnConfirm_.enable = buyNumber <= GOLD_LIMIT and buyNumber > 0
			if buyNumber > GOLD_LIMIT:
				showAutoHideMessage( 3.0, mbmsgs[0x07e7], "", pyOwner = self )
				buyNumber = GOLD_LIMIT
				self.pyNumberBox_.text = str( buyNumber )
			totalPrice = unitPrice*buyNumber
			self.pyTotalPanel_.setBoxText( totalPrice )
			fee = int( unitPrice*0.11 )*buyNumber
			self.pyFeePanel_.setBoxText( fee )
			self.pyIncomePanel_.setBoxText( totalPrice + fee )
	
	def onUnitPriceChange( self, unitPrice ):
		if self.pyNumberBox_.text != "":
			buyNumber = int( self.pyNumberBox_.text )
			self.pyBtnConfirm_.enable = buyNumber <= GOLD_LIMIT and unitPrice > 0
			totalPrice = unitPrice*buyNumber
			self.pyTotalPanel_.setBoxText( totalPrice )
			fee = int( unitPrice*0.11 )*buyNumber
			self.pyFeePanel_.setBoxText( fee )
			self.pyIncomePanel_.setBoxText( totalPrice + fee )
	
	def onEstablishBuyBill( self ):
		yuanbao = int( self.pyNumberBox_.text )
		unitPrice = self.__pyUnitPanel.getUnitPrice()
		fee = int( unitPrice*0.01 )*yuanbao
		priceStr = ""
		feeStr = ""
		priceGold = unitPrice/10000
		priceSilver = ( unitPrice%10000 )/100
		priceCoin = ( unitPrice%10000 )%100
		feeGold = fee/10000
		feeSilver = ( fee%10000 )/100
		feeCoin = ( fee%10000 )%100
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().establishBuyBill( yuanbao, unitPrice )
		if int( priceGold ) > 0:
			priceStr += "%d%s"%( priceGold, PL_Image.getSource( "guis_v2/controls/goldicon.gui" ) )
		if int( priceSilver ) > 0:
			priceStr += "%d%s"%( priceSilver, PL_Image.getSource( "guis_v2/controls/silvericon.gui" ) )
		if priceCoin > 0:
			priceStr += "%d%s"%( priceCoin, PL_Image.getSource( "guis_v2/controls/coinicon.gui" ) )
		if int( feeGold ) > 0:
			feeStr += "%d%s"%( feeGold, PL_Image.getSource( "guis_v2/controls/goldicon.gui" ) )
		if int( feeSilver ) > 0:
			feeStr += "%d%s"%( feeSilver, PL_Image.getSource( "guis_v2/controls/silvericon.gui" ) )
		if feeCoin > 0:
			feeStr += "%d%s"%( feeCoin, PL_Image.getSource( "guis_v2/controls/coinicon.gui" ) )
		showMessage( mbmsgs[0x07e5]%( feeStr, priceStr, yuanbao*100 ), "", MB_OK_CANCEL, query, self )
		return True

	def onHide( self ):
		self.__pyUnitPanel.resetBox()
		SettingPanel.onHide( self )

# ----------------------------------------------------------------------------------
MONEY_LIMIT = 2500000
MONEY_LOWER_LIMIT = 200000

class UnitPanel( PyGUI ):
	def __init__( self, panel, pyBinder ):
		PyGUI.__init__( self, panel )
		self.__pyGoldBox = TextBox( panel.goldBox.box )
		self.__pyGoldBox.text = ""
		self.__pyGoldBox.maxLength = 3
		self.__pyGoldBox.inputMode = InputMode.INTEGER
		self.__pyGoldBox.filterChars = ["-", "+"]
		self.__pyGoldBox.onTextChanged.bind( self.__onTextChange )
		
		self.__pySilverBox = TextBox( panel.silverBox.box )
		self.__pySilverBox.text = ""
		self.__pySilverBox.maxLength = 2
		self.__pySilverBox.inputMode = InputMode.INTEGER
		self.__pySilverBox.filterChars = ["-", "+"]
		self.__pySilverBox.onTextChanged.bind( self.__onTextChange )

		self.__pyCoinBox = TextBox( panel.coinBox.box )
		self.__pyCoinBox.text = ""
		self.__pyCoinBox.maxLength = 2
		self.__pyCoinBox.inputMode = InputMode.INTEGER
		self.__pyCoinBox.filterChars = ["-", "+"]
		self.__pyCoinBox.onTextChanged.bind( self.__onTextChange )
		self.pyBinder = pyBinder
	
	def __onTextChange( self ):
		money = self.getUnitPrice()
		self.pyBinder.onUnitPriceChange( money )
			
	def getUnitPrice( self ):
		coin = 0
		silver = 0
		gold = 0
		if self.__pyGoldBox.text != "":
			gold = int( self.__pyGoldBox.text )
		if self.__pySilverBox.text != "":
			silver = int( self.__pySilverBox.text )
		if self.__pyCoinBox.text != "":
			coin = int( self.__pyCoinBox.text )
		money = gold*10000 + silver*100 + coin
		return money
	
	def setLtUnit( self, isBuy ):
		"""
		设置购买或出售最低价
		"""
		if isBuy: #购买
			self.__pyGoldBox.pyLText_.text = "%d"%( UNIT_LOWER_LIMIT/10000 )
		else:
			self.__pyGoldBox.pyLText_.text = "%d"%( UNIT_LIMIT/10000 )
		self.__pySilverBox.pyLText_.text = "%d"%0
		self.__pyCoinBox.pyLText_.text = "%d"%0
		
	def resetBox( self ):
		self.__pyGoldBox.text = ""
		self.__pySilverBox.text = ""
		self.__pyCoinBox.text = ""

# ---------------------------------------------------------
class MoneyPanel( PyGUI ):
	def __init__( self, panel ):
		PyGUI.__init__( self, panel )
		self.__pyStGold = StaticText( panel.stGold )
		self.__pyStGold.text = ""
		
		self.__pyStSilver = StaticText( panel.stSilver )
		self.__pyStSilver.text = ""
		
		self.__pyStCoin = StaticText( panel.stCoin )
		self.__pyStCoin.text = ""
	
	def setBoxText( self, money ):
		gold = money/10000
		silver = ( money%10000 )/100
		coin = ( money%10000 )%100
		self.__pyStGold.text = str( gold )
		self.__pyStSilver.text = str( silver )
		self.__pyStCoin.text = str( coin )
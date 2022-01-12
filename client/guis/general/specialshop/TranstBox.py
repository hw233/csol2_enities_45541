# -*- coding: gb18030 -*-
#
# $Id: TranstBox.py, fangpengjun Exp $

"""
implement transt box class

"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.TextBox import TextBox
from guis.controls.Button import Button
from config.client.msgboxtexts import Datas as mbmsgs
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Image import PL_Image

class BaseBox( Window ):
	def __init__( self, box ):
		Window.__init__( self, box )
		self.bill = None
		self.pyNumBox_ = TextBox( box.numberBox.box )
		self.pyNumBox_.text = ""
		self.pyNumBox_.inputMode = InputMode.INTEGER
		self.pyNumBox_.filterChars = ["-","+"]
		
		self.pyRtTotal_ = CSRichText( box.rtTotal )
		self.pyRtTotal_.text = ""
		
		self.pyBtnCancel_ = Button( box.btnCancel )
		self.pyBtnCancel_.setStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyLabel( self.pyBtnCancel_, "SpecialShop:TranstBox", "cancel" )
		self.__initInfoPanel( box.infoPanel )
		labelGather.setLabel( box.infoPanel.orderText, "SpecialShop:TranstBox", "orderNumer" )
		labelGather.setLabel( box.unitText, "SpecialShop:TranstBox", "unit" )
		
	def __initInfoPanel( self, panel ):
		self.pyStOrder_ = StaticText( panel.stOrder )
		self.pyStOrder_.text = ""
		self.pyRtUnitPrice_ = CSRichText( panel.rtUnit )
		self.pyRtUnitPrice_.text = ""
		self.pyRtNumber_ = CSRichText( panel.rtNumber )
		self.pyRtNumber_.text = ""
	
	def show( self, bill, pyOwner ):
		self.bill = bill
		self.pyStOrder_.text = str( bill[1] )
		iconText = PL_Image.getSource( "guis_v2/controls/coinicon.gui" )
		self.pyRtUnitPrice_.text = PL_Font.getSource( "%d%s"%( bill[-1], iconText ), fc = ( 232, 53, 241 ) )
		ybIcon = PL_Image.getSource( "guis/general/specialshop/yuanbao.gui" )
		self.pyRtNumber_.text = PL_Font.getSource( "%d%s"%( bill[3]*100, ybIcon ), fc = ( 255, 255, 255 ) )
		Window.show( self, pyOwner )
	
	def hide( self ):
		self.bill = None
		self.pyNumBox_.text = ""
		self.pyRtTotal_.text = ""
		self.pyStOrder_.text = ""
		self.pyRtUnitPrice_.text = ""
		self.pyRtNumber_.text = ""
		Window.hide( self )

# -------------------------------------------------------
# 元宝购买确认框
class BuyBox( BaseBox ):
	__instance=None
	def __init__( self ):
		assert BuyBox.__instance is None ,"BuyBox instance has been created"
		BuyBox.__instance = self
		box = GUI.load( "guis/general/specialshop/buybox.gui" )
		uiFixer.firstLoadFix( box )
		BaseBox.__init__( self, box )
		self.pyNumBox_.onTextChanged.bind( self.__onBuyNumChange )
		self.__pyBtnBuy = Button( box.btnBuy )
		self.__pyBtnBuy.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnBuy.enable = False
		self.__pyBtnBuy.onLClick.bind( self.__onBuyYB )
		self.pyBtnCancel_.onLClick.bind( self.__onCancelBuy )
		labelGather.setPyLabel( self.pyLbTitle_, "SpecialShop:TranstBox", "buyTitle" )
		labelGather.setLabel( box.infoPanel.unitPrice,"SpecialShop:TranstBox", "sellUnit" )
		labelGather.setLabel( box.infoPanel.sellNumber,"SpecialShop:TranstBox", "sellNumber" )
		labelGather.setLabel( box.inputText, "SpecialShop:TranstBox", "inputBuy" )
		labelGather.setLabel( box.totalText, "SpecialShop:TranstBox", "totalExpend" )
		labelGather.setPyLabel( self.__pyBtnBuy, "SpecialShop:TranstBox", "buyTitle" )
		self.addToMgr( "buyBox" )

	@staticmethod
	def instance():
		if BuyBox.__instance is None:
			BuyBox.__instance = BuyBox()
		return BuyBox.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return BuyBox.__instance
	
	def __onBuyNumChange( self ):
		self.__pyBtnBuy.enable = self.pyNumBox_.text != "" and int( self.pyNumBox_.text ) <= self.bill[3]
		if self.pyNumBox_.text == "":return
		if int( self.pyNumBox_.text ) > self.bill[3]:
			showAutoHideMessage( 3.0, mbmsgs[0x07ee]%( self.bill[3]*100 ),"", MB_OK, pyOwner = self )
			self.pyNumBox_.text = str( self.bill[3] )
			return
		num = int( self.pyNumBox_.text )
		expense = num*self.bill[-1]
		extra = expense*0.1
		total = expense + extra
		expStr = ""
		extraStr = ""
		expGold = total/10000
		expSilver = ( total%10000 )/100
		expCoin = ( total%10000 )%100
		extraGold = extra/10000
		extraSilver = ( extra%10000 )/100
		extraCoin = ( extra%10000 )%100
		if expGold > 0:
			expStr += "%d%s"%( expGold, PL_Image.getSource( "guis_v2/controls/goldicon.gui" ) )
		if expSilver > 0:
			expStr += "%d%s"%( expSilver, PL_Image.getSource( "guis_v2/controls/silvericon.gui" ) )
		if expCoin > 0:
			expStr += "%d%s"%( expCoin, PL_Image.getSource( "guis_v2/controls/coinicon.gui" ) )
			
		if extraGold > 0:
			extraStr += "%d%s"%( extraGold, PL_Image.getSource( "guis_v2/controls/goldicon.gui" ) )
		if extraSilver > 0:
			extraStr += "%d%s"%( extraSilver, PL_Image.getSource( "guis_v2/controls/silvericon.gui" ) )
		if extraCoin > 0:
			extraStr += "%d%s"%( extraCoin, PL_Image.getSource( "guis_v2/controls/coinicon.gui" ) )
			
		self.pyRtTotal_.text = PL_Font.getSource( "%s,其中%s为手续费"%( expStr, extraStr ), fc = ( 232, 53, 241 ) )
	
	def __onBuyYB( self ):
		"""
		购买元宝
		"""
		if self.bill is None:return
		yuanbao = int( self.pyNumBox_.text )
		BigWorld.player().buyYB( self.bill[0], self.bill[1], yuanbao, self.bill[-1] )
	
	def __onCancelBuy( self ):
		"""
		取消购买
		"""
		self.hide()
	
	def show( self, bill, pyOwner = None ):
		BaseBox.show( self, bill, pyOwner )

	def hide( self ):
		self.__pyBtnBuy.enable = False
		if self.bill is None:return
		BigWorld.player().unBuyYB( self.bill[0], self.bill[1] )
		BaseBox.hide( self )
		self.removeFromMgr()
		BuyBox.__instance = None
		
# --------------------------------------------------------
# 元宝出售确认框
class SellBox( BaseBox ):
	__instance = None
	def __init__( self ):
		assert SellBox.__instance is None ,"BuyBox instance has been created"
		SellBox.__instance = self
		box = GUI.load( "guis/general/specialshop/sellbox.gui" )
		uiFixer.firstLoadFix( box )
		BaseBox.__init__( self, box )
		self.bill = None
		self.pyNumBox_.onTextChanged.bind( self.__onSellNumChange )
		self.__pyBtnSell = Button( box.btnSell )
		self.__pyBtnSell.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSell.enable = False
		self.__pyBtnSell.onLClick.bind( self.__onSellYB )
		self.pyBtnCancel_.onLClick.bind( self.__onCancelSell )
		labelGather.setPyLabel( self.pyLbTitle_, "SpecialShop:TranstBox", "sellTitle" )
		labelGather.setLabel( box.infoPanel.unitPrice,"SpecialShop:TranstBox", "buyUnit" )
		labelGather.setLabel( box.infoPanel.buyNumber,"SpecialShop:TranstBox", "buyNumber" )
		labelGather.setLabel( box.inputText, "SpecialShop:TranstBox", "inputSell" )
		labelGather.setLabel( box.totalText, "SpecialShop:TranstBox", "totalIncome" )
		labelGather.setPyLabel( self.__pyBtnSell, "SpecialShop:TranstBox", "sellTitle" )
		self.addToMgr( "sellBox" )

	@staticmethod
	def instance():
		if SellBox.__instance is None:
			SellBox.__instance = SellBox()
		return SellBox.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return SellBox.__instance
	
	def __onSellNumChange( self ):
		self.__pyBtnSell.enable = self.pyNumBox_.text != "" and int( self.pyNumBox_.text ) <= self.bill[3]
		if self.pyNumBox_.text == "":return
		if int( self.pyNumBox_.text ) > self.bill[3]:
			showAutoHideMessage( 3.0, mbmsgs[0x07ef]%( self.bill[3]*100 ),"", MB_OK, pyOwner = self )
			self.pyNumBox_.text = str( self.bill[3] )
			return
		num = int( self.pyNumBox_.text )
		income = self.bill[-1]*num
		fee = income*0.1
		incStr = ""
		feeStr = ""
		incGold = income/10000
		incSilver = ( income%10000 )/100
		incCoin = ( income%10000 )%100
		feeGold = fee/10000
		feeSilver = ( fee%10000 )/100
		feeCoin = ( fee%10000 )%100
		if incGold > 0:
			incStr += "%d%s"%( incGold, PL_Image.getSource( "guis_v2/controls/goldicon.gui" ) )
		if incSilver > 0:
			incStr += "%d%s"%( feeSilver, PL_Image.getSource( "guis_v2/controls/silvericon.gui" ) )
		if incCoin > 0:
			incStr += "%d%s"%( incCoin, PL_Image.getSource( "guis_v2/controls/coinicon.gui" ) )

		if feeGold > 0:
			feeStr += "%d%s"%( feeGold, PL_Image.getSource( "guis_v2/controls/goldicon.gui" ) )
		if feeSilver > 0:
			feeStr += "%d%s"%( feeSilver, PL_Image.getSource( "guis_v2/controls/silvericon.gui" ) )
		if feeCoin > 0:
			feeStr += "%d%s"%( feeCoin, PL_Image.getSource( "guis_v2/controls/coinicon.gui" ) )
			
		self.pyRtTotal_.text = PL_Font.getSource( "%s"%incStr, fc = ( 232, 53, 241 ) )
	
	def __onSellYB( self ):
		"""
		出售元宝
		"""
		if self.bill is None:return
		yuanbao = int( self.pyNumBox_.text )
		BigWorld.player().sellYB( self.bill[0], self.bill[1], yuanbao, self.bill[-1] )
	
	def __onCancelSell( self ):
		"""
		取消元宝出售
		"""
		self.hide()
	
	def show( self, bill, pyOwner = None ):
		BaseBox.show( self, bill, pyOwner )
		
	def hide( self ):
		self.__pyBtnSell.enable = False
		if self.bill is None:return
		BigWorld.player().unSellYB( self.bill[0], self.bill[1] )
		BaseBox.hide( self )
		self.removeFromMgr()
		SellBox.__instance=None
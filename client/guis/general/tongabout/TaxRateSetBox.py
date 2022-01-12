# -*- coding: gb18030 -*-
#
# $Id: TaxRateSetBox.py,v 1.4 2008-08-14 02:20:08 kebiao Exp $

"""
implement TaxRateSetBox window
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.tooluis.CSRichText import CSRichText
from guis.controls.TextBox import TextBox
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import GUIFacade

class TaxRateSetBox( Window ):

	__instance=None
	def __init__( self ):
		assert TaxRateSetBox.__instance is None,"TaxRateSetBox instance has been created"
		box = GUI.load( "guis/general/tongabout/taxset.gui" )
		uiFixer.firstLoadFix( box )
		Window.__init__( self, box )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True

		self.__pyBtnOk = Button( box.btnOk, self )
		self.__pyBtnOk.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onOk )
		labelGather.setPyBgLabel( self.__pyBtnOk, "TongAbout:TaxRateSetBox", "btnOk" )

		self.__pyTaxBox = TextBox( box.setTaxBox.box, self )
		self.__pyTaxBox.onTextChanged.bind( self.__onTextChange )
		self.__pyTaxBox.inputMode = InputMode.INTEGER
		self.__pyTaxBox.text = ""
		self.__pyTaxBox.maxLength = 2
		self.__pyTaxBox.filterChars = ['-', '+']

		self.__pyBtnCancel = Button( box.btnCancel,self)
		self.__pyBtnCancel.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "TongAbout:TaxRateSetBox", "btnCancel" )

		self.__pyRtExplain = CSRichText( box.rtExplain )
		self.__pyRtExplain.text = ""
		self.__pyRtExplain.align = "L"
	
		labelGather.setLabel( box.lbTitle, "TongAbout:TaxRateSetBox", "lbTitle" )
		labelGather.setLabel( box.taxRatio, "TongAbout:TaxRateSetBox", "inputRatio" )

		self.addToMgr( "cityTaxRateBox" )

	# -------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onOk( self ) :
		if self.notify_() :
			BigWorld.player().tong_requestSetCityRevenueRate( int( self.__pyTaxBox.text ) )
			self.hide()

	def __onCancel( self ) :
		self.hide()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self ) :
		player = BigWorld.player()
		text = self.__pyTaxBox.text
		if text == "" : return False
		rateNum = int( text )
		if rateNum < 1 or rateNum > 50:	# 帮会名称合法性检测
			# "税率只能为1%-50%，请输入一个1-50的整数，请重新输入。"
			showAutoHideMessage( 3.0, 0x09c1, "" )
			return False
		return True

	def __onTextChange( self ) :
		self.__pyBtnOk.enable = self.__pyTaxBox.text != ""

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------

	def show( self, rate ) :
		self.__pyRtExplain.text = PL_Font.getSource( labelGather.getText( "TongAbout:TaxRateSetBox", "warnText" ), fc = ( 230, 227, 185 ) )
		self.__pyTaxBox.text = "%s"%rate
		Window.show( self )
		self.__pyTaxBox.tabStop = True

	def hide( self ):
		self.__pyTaxBox.clear()
		Window.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )

	def onLeaveWorld( self ) :
		self.hide()

	@staticmethod
	def instance():
		if TaxRateSetBox.__instance is None:
			TaxRateSetBox.__instance = TaxRateSetBox()
		return TaxRateSetBox.__instance
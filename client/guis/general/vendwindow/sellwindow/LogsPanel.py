# -*- coding: gb18030 -*-
#
# $Id: LogsPanel.py,v 1.3 2008-09-05 08:05:00 fangpengjun Exp $
#

from guis import *
from guis.controls.TabCtrl import TabPanel
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ItemsPanel import ItemsPanel
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
SPACE = PL_Space.getSource
from LabelGather import labelGather


class VendLogsPanel( TabPanel ) :

	def __init__( self, tabPanel, pyBinder = None ) :
		TabPanel.__init__( self, tabPanel, pyBinder )
		self.triggers_ = {}
		self.registerTriggers_()

		#self.__pyTotalIncome = CSRichText( tabPanel.rtTotalInCome ) 				# 合计收益
		#self.__pyTotalIncome.foreColor = ( 6, 228, 192, 255 )
		#self.__pyTotalIncome.text = labelGather.getText( "vendwindow:VendLogsPanel", "totalIncome" ) + SPACE( 24 ) + "0"
		self.__pyIncome = MoneyBar( tabPanel.moneybox_income )
		self.__pyIncome.readOnly = True
		self.__pyIncome.money = 0

		self.__pyLogsPanel = ItemsPanel( tabPanel.ctPanel.clipPanel, tabPanel.ctPanel.sbar )
		self.income_ = 0

		labelGather.setLabel( tabPanel.st_Income, "vendwindow:VendLogsPanel", "totalIncome" )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def addRecord_( self, record ) :
		pyRecord = CSRichText()
		pyRecord.maxWidth = self.__pyLogsPanel.width
		name, sellName, price, time, amount = record
		itemName = PL_Font.getSource( sellName, fc = ( 255, 0, 0, 255 ) )
		priceStr = PL_Font.getSource( utils.currencyToViewText( price ),fc = ( 0, 255, 0, 255 ) )
		timeStr = PL_Font.getSource( time, fc = ( 1, 128, 108, 255 ) )
		buyerName = PL_Font.getSource( name, fc = ( 255, 0, 0, 255 ) )
		itemAmount = PL_Font.getSource( str( amount ), fc = ( 255, 255, 255, 0 ) )
		pyRecord.text = labelGather.getText( "vendwindow:VendLogsPanel", "record" ) % ( timeStr, buyerName, priceStr, itemName, itemAmount )
		self.__pyLogsPanel.addItem( pyRecord )
		self.income_ += price
		self.__pyIncome.money = self.income_
		#incomeStr = labelGather.getText( "vendwindow:VendLogsPanel", "totalIncome" ) + \
		#SPACE( 24 ) + utils.currencyToViewText( self.income_ )
		#self.__pyTotalIncome.text = incomeStr
		
	def addRecord2_( self, record ) :
		pyRecord = CSRichText()
		pyRecord.maxWidth = self.__pyLogsPanel.width
		name, sellName, price, time, amount = record
		itemName = PL_Font.getSource( sellName, fc = ( 255, 0, 0, 255 ) )
		priceStr = PL_Font.getSource( utils.currencyToViewText( price ),fc = ( 0, 255, 0, 255 ) )
		timeStr = PL_Font.getSource( time, fc = ( 1, 128, 108, 255 ) )
		buyerName = PL_Font.getSource( name, fc = ( 255, 0, 0, 255 ) )
		itemAmount = PL_Font.getSource( str( amount ), fc = ( 255, 255, 255, 0 ) )
		pyRecord.text = labelGather.getText( "vendwindow:VendLogsPanel", "record2" ) % ( timeStr, buyerName, priceStr, itemName, itemAmount )
		self.__pyLogsPanel.addItem( pyRecord )
		self.income_ += price
		self.__pyIncome.money = self.income_

	def registerTriggers_( self ) :
		self.triggers_["EVT_ON_VEND_VENDOR_ADD_RECORD"] = self.addRecord_
		self.triggers_["EVT_ON_VEND_VENDOR_ADD_RECORD_BUY"] = self.addRecord2_
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )


	# ----------------------------------------------------------------
	# pravite
	# ----------------------------------------------------------------
	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.triggers_.iterkeys() :
			ECenter.registerEvent( key, self )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.triggers_[eventMacro]( *args )

	def reset( self ) :
		#self.__pyTotalIncome.text = labelGather.getText( "vendwindow:VendLogsPanel", "totalIncome" ) +\
		#SPACE( 24 ) + "0"
		self.__pyIncome.money = 0
		self.__pyLogsPanel.clearItems()

	def onParentShow( self ) :
		pass

	def onParentHide( self ) :
		pass
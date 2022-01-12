# -*- coding: gb18030 -*-
#
# $Id: ChangeRateSetting.py $

"""
implement ChangeRateSetting class
"""
from guis import *
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from LabelGather import labelGather

class ChangeRateSetting( Window ):
	__instance = None
	def __init__( self ):
		assert ChangeRateSetting.__instance is None, " ChangeRateSetting.__instance has been created!"
		ChangeRateSetting.__instance  = self 
		panel = GUI.load( "guis/tooluis/inputbox/money_input_box.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.addToMgr( " changeRateSetting" ) 
	
		self.__initPanel( panel )
		
	def __initPanel( self, panel ):
		self.__moneyInput = MoneyBar( panel.inputBoxs )
		self.__moneyInput.money = 0
		
		self.__pyBtnOk = HButtonEx( panel.OKBtn )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__updateChangeRate )
		labelGather.setPyBgLabel( self.__pyBtnOk, "RelationShip:RelationPanel", "btnOk" )
		
		self.__pyBtnCancel = HButtonEx( panel.cancelBtn )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__cancelUpdateChangeRate )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "RelationShip:RelationPanel", "btnCancel" )
		
		self.__pyStChangeRate = StaticText( panel.notifyText )
		self.__pyStChangeRate.charSpace = -1
		self.__pyStChangeRate.text = labelGather.getText( "RelationShip:TongPanel", "changeRateTips" )
	
	# ----------------------------------------------------------
	# private
	# ----------------------------------------------------------			
	def __updateChangeRate( self ):
		rate = self.__moneyInput.money
		if rate > 0:
			player = BigWorld.player()
			player.tong_setSalaryExchangeRate(  rate )
			
	def __cancelUpdateChangeRate( self ):
		self.hide()
		
	@staticmethod
	def instance():
		"""
		get the exclusive instance of ChangeRateSetting
		"""
		if ChangeRateSetting.__instance is None:
			ChangeRateSetting.__instance = ChangeRateSetting()
		return ChangeRateSetting.__instance
	
	def show( self, pyOwner = None ):
		Window.show( self, pyOwner )
		
	def hide( self ):
		self.__moneyInput.money = 0
		Window.hide( self )
		
		
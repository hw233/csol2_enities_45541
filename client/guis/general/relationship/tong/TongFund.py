# -*- coding: gb18030 -*-
#
# $Id: TongFund.py $

"""
implement TongFund class
"""

import BigWorld
import csdefine
from guis import *
from guis.controls.Control import Control
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.Label import Label
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ItemsPanel import ItemsPanel
from ChangeRateSetting import ChangeRateSetting
import GUIFacade
from guis.common.PyGUI import PyGUI
import utils


class TongFund( Window ):
	def __init__( self ):
		panel = GUI.load( "guis/general/relationwindow/tongpanel/tongFund.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.addToMgr( "tongFund" )	
		self.__triggers = {}
		self.__registerTriggers()
		self.__initpanel( panel )

	def __initpanel( self, panel ):
		labelGather.setLabel( panel.lbTitle, "RelationShip:TongPanel", "tongFund" )
		self.__infoPanel = ItemsPanel( panel.infoPanel.clipPanel, panel.infoPanel.sbar )
		self.__infoPanel.rowSpace = 5
		lastweekPanel = GUI.load("guis/general/relationwindow/tongpanel/lastweekFund.gui" )
		uiFixer.firstLoadFix( lastweekPanel )
		self.__lastWeekInfoPanel = InfoPanel( lastweekPanel )
		thisweekPanel = GUI.load("guis/general/relationwindow/tongpanel/thisweekFund.gui" )
		uiFixer.firstLoadFix( thisweekPanel )
		self.__thisWeekInfoPanel = InfoPanel( thisweekPanel )
		nextweekPanel = GUI.load("guis/general/relationwindow/tongpanel/nextweekFundSet.gui" )
		uiFixer.firstLoadFix( nextweekPanel )
		
		self.__btnChangeRate = HButtonEx( nextweekPanel.changeRate )
		self.__btnChangeRate.setExStatesMapping( UIState.MODE_R4C1 )
		self.__btnChangeRate.onLClick.bind( self.__updateNextWeekChangeRate)
		labelGather.setPyBgLabel( self.__btnChangeRate,"RelationShip:TongPanel", "set" )
		self.__nextWeekChangeRatePanel = InfoPanel( nextweekPanel )
		
		self.__pyBtnShut = HButtonEx( panel.btnShut )
		self.__pyBtnShut.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnShut.onLClick.bind( self.__onQuit )
		labelGather.setPyBgLabel( self.__pyBtnShut, "RelationShip:TongPanel", "close" )	

	# ----------------------------------------------------------
	# private
	# ----------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_INIT_TONG_FUND"] = self.__onInitFund		 #初始化帮会资金情况
		self.__triggers["EVT_ON_TOGGLE_TONG_UPDATE_NEXTWEEKRATE"] = self.__onUpdateNextWeekChangeRate 		#更新下周帮会兑换额
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )
	
	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	#-------------------------------------------------------------
	
	def __onInitFund( self, lastWeekInfo, thisWeekInfo ):
		tongMoney = BigWorld.player().tongMoney
		lastWeekInfos = { "lastweekTotalFund": utils.currencyToViewText( lastWeekInfo[0] ),
						"lastweekChangeRate": labelGather.getText("RelationShip:TongPanel","lastweekChangeRateValue")%( utils.currencyToViewText( lastWeekInfo[1] )),
						"lastweekContribute": labelGather.getText("RelationShip:TongPanel", "lastweekContributeValue" ) % ( lastWeekInfo[2] ),
						"lastweekUsedSarary": utils.currencyToViewText( lastWeekInfo[3] ),
						"lastweekUsedFund": utils.currencyToViewText( lastWeekInfo[4] ),
						"lastweekRemainFund": utils.currencyToViewText( lastWeekInfo[5] )
						}
		thisWeekInfos = { "thisweekTotalFund":utils.currencyToViewText( thisWeekInfo[0] ),
						"thisweekChangeRate" :labelGather.getText("RelationShip:TongPanel","thisweekChangeRateValue")%(utils.currencyToViewText( thisWeekInfo[1] )),
						"thisweekContribute": labelGather.getText("RelationShip:TongPanel", "thisweekContributeValue") % ( thisWeekInfo[2]),
						"thisweekUsedSararySet":utils.currencyToViewText( int ( thisWeekInfo[1] * thisWeekInfo[2]) ),
						"thisweekUsedFund":utils.currencyToViewText( thisWeekInfo[3] ),
						"thisweekRemainFund":utils.currencyToViewText( tongMoney )				
						}
		
		lastWeekItems = self.__lastWeekInfoPanel.pyInfoItems
		for name, pyInfoPanel in lastWeekItems.items():
			infoValue = lastWeekInfos.get( name, None )
			if infoValue is None:continue
			pyInfoPanel.title = labelGather.getText( "RelationShip:TongPanel", name )
			pyInfoPanel.text = str( infoValue )		
		self.__lastWeekInfoPanel.title = labelGather.getText( "RelationShip:TongPanel", "lastweek" )
		self.__infoPanel.addItem( self.__lastWeekInfoPanel )
		self.__lastWeekInfoPanel.top = 10
		thisWeekItems = self.__thisWeekInfoPanel.pyInfoItems
		for name, pyInfoPanel in thisWeekItems.items():
			infoValue = thisWeekInfos.get( name, None )
			if infoValue is None:continue
			pyInfoPanel.title = labelGather.getText( "RelationShip:TongPanel", name )
			pyInfoPanel.text = str( infoValue )	
		self.__thisWeekInfoPanel.title = labelGather.getText( "RelationShip:TongPanel", "thisweek" )		
		self.__infoPanel.addItem( self.__thisWeekInfoPanel )		
		if self.__isTongChife(): # 如果是帮主，则显示更改下周兑换额选项
			nextWeekItems = self.__nextWeekChangeRatePanel.pyInfoItems
			for name, pyInfoPanel in nextWeekItems.items():
				pyInfoPanel.title = labelGather.getText( "RelationShip:TongPanel", name )
				changeRateText = labelGather.getText("RelationShip:TongPanel","changeRate")%utils.currencyToViewText( thisWeekInfo[-1] )
				pyInfoPanel.text = changeRateText
			self.__infoPanel.addItem( self.__nextWeekChangeRatePanel )
							
	def __onUpdateNextWeekChangeRate( self, rate ):
		if rate is not None:
			changeRateText = labelGather.getText("RelationShip:TongPanel","changeRate")%utils.currencyToViewText( rate )
			self.__nextWeekChangeRatePanel.pyInfoItems["nextweekChangeRate"].text = changeRateText
				
	def __isTongChife( self ):
		player =BigWorld.player()
		grade = player.tong_memberInfos[player.databaseID].getGrade()
		return grade == csdefine.TONG_DUTY_CHIEF

	def __updateNextWeekChangeRate( self ):
		ChangeRateSetting.instance().show( self )

	def __onQuit( self ):
		self.hide()

	# -----------------------------------------------------------------
	# public
	# -----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self, pyOwner = None ):
		player = BigWorld.player()
		player.cell.tong_onClientOpenTongMoneyWindow()
		Window.show( self, pyOwner )

	def hide( self ):
		Window.hide( self )
		
class InfoPanel( PyGUI ):
	def __init__( self, panel ):
		PyGUI.__init__( self, panel )
		self.__pyInfoItems = {}
		for name, item in panel.children:
			if name == "divition" or name == "title" or name == "changeRate": continue
			pyItem = InfoItem( item )
			self.__pyInfoItems[name] = pyItem
		haveTitle = getattr( panel, "title", None )
		if haveTitle:
			self.__title = StaticText( panel.title )
			self.__title.text = ""
		
	def _getPyItems( self ):
		return self.__pyInfoItems
		
	def _getText( self ):
		return self.__title.text
		
	def _setText( self, value ):
		self.__title.text = value
		
	pyInfoItems = property( _getPyItems)
	title = property( _getText, _setText )	
		
class InfoItem( Control ):
	def __init__( self, infoItem ):
		Control.__init__( self, infoItem )
		self.crossFocus = True
		self.__pyStTitle = StaticText( infoItem.titleText )
		self.__pyRtValue = CSRichText( infoItem.rtValue )
		self.__pyRtValue.align = "R"
		self.__pyRtValue.text = ""

	def _getText( self ):
		return self.__pyRtValue.text

	def _setText( self, text ):
		self.__pyRtValue.text = text

	def _getTitle( self ):
		return self.__pyStTitle.text

	def _setTitle( self, title ):
		self.__pyStTitle.text = title

	text = property( _getText, _setText )
	title = property( _getTitle, _setTitle )
	
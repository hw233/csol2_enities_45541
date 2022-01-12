# -*- coding: gb18030 -*-
#
# $Id: YuanBaoPanel.py, fangpengjun Exp $

"""
implement ybTrade panel class

"""
from guis import *
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.controls.TabCtrl import TabPanel
from LabelGather import labelGather
from TranstPanel import SellPanel
from TranstPanel import BuyPanel
from ReleasePanel import ReleasePanel
from DetailsPanel import LogsPanel,OperatePanel

class YBTradePanel( TabPanel ):
	
	ybPanels = {0: SellPanel, 
				1: BuyPanel,
				2: ReleasePanel,
				3: LogsPanel,
				4: OperatePanel
				}
				
	def __init__( self, panel, pyBinder = None ):
		TabPanel.__init__( self, panel )
		self.__pyTabCtrl = TabCtrl( panel )
		index = 0
		while True :											#初始化TabCtrl
			tabName = "btn_" + str( index )
			tab = getattr( panel, tabName, None )
			if tab is None : break
			panelName = "panel_" + str( index )
			tabPanel = getattr( panel, panelName, None )
			if tabPanel is None : break
			pyBtn = TabButton( tab )
			labelGather.setPyBgLabel( pyBtn, "SpecialShop:ybPanel", tabName )
			pyPanel = self.ybPanels[index]( tabPanel )
			pyPage = TabPage( pyBtn, pyPanel )
			self.__pyTabCtrl.addPage( pyPage )
			index += 1
		self.__pyTabCtrl.onTabPageSelectedChanged.bind( self.__onPageChange )

	def __onPageChange( self, pyCtrl ):
		pySelPage = pyCtrl.pySelPage
		pyPanel = pySelPage.pyPanel
		pyPanel.onSelected()
	
	def onSelected( self ):
		self.__pyTabCtrl.pySelPage = self.__pyTabCtrl.pyPages[0]
		pyPanel = self.__pyTabCtrl.pySelPage.pyPanel
		pyPanel.onSelected()
	
	def onHide( self ):
		for pyPage in self.__pyTabCtrl.pyPages:
			pyPage.pyPanel.onHide()
	
	def onLeaveWorld( self ):
		for pyPage in self.__pyTabCtrl.pyPages:
			pyPage.pyPanel.onLeaveWorld()

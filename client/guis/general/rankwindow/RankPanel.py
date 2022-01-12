# -*- coding: gb18030 -*-
#
# $Id: LevelCharts.py, fangpengjun Exp $

"""
implement LevelCharts panel class

"""
from guis import *
from guis.controls.TabCtrl import TabPanel
from guis.controls.ListPanel import ListPanel
from RankItem import RankItem
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from guis.tooluis.richtext_plugins.PL_Image import PL_Image

MAX_AMOUNT = 20

class RankPanel( TabPanel ):
	def __init__( self, tabPanel ):
		TabPanel.__init__( self, tabPanel )
		self.__initialize( tabPanel )

	def __initialize( self, panel ):
		"""
		初始化列表
		"""
		self.__barsPath = "guis/general/rankwindow/bars/bar_%d.gui"
		self.__pyRanksPanel = ListPanel( panel.ranksPanel, panel.ranksBar )
		self.__pyRanksPanel.autoSelect = False
		self.__pyRanksPanel.rowSpace = -5.0

	def dispose(self):
		self.__pyRanksPanel.clearItems()	# NPC信息列表
		self.__pyRanksPanel = None
		TabPanel.dispose(self)

	def setRankItemInfo( self, startIndex, rankDatas ):
		"""
		设置从startIndex开始的格子信息
		"""
		player = BigWorld.player()
		rankType = self.pyTabPage.rankType
		playerName = player.getName()
		tongName = player.tongName
		for index, rankData in enumerate( rankDatas ):
			gbIndex = startIndex + index
			item = GUI.load( self.__barsPath%rankType )
			uiFixer.firstLoadFix( item )
			pyRankItem = RankItem( item )
			pyRankItem.index = gbIndex
			pyRankItem.updateRankData( rankType, gbIndex, rankData )
			pyRankItem.selected = False
			pyRankItem.reset()
			self.__pyRanksPanel.addItem( pyRankItem )
	
	def onRecActPoint( self, gbIndex, infoList ):
		item = GUI.load( self.__barsPath%3 )
		uiFixer.firstLoadFix( item )
		pyRankItem = RankItem( item )
		pyRankItem.index = infoList[0]
		pyRankItem.setTongActPoit( gbIndex, infoList )
		pyRankItem.selected = False
		pyRankItem.reset()
		self.__pyRanksPanel.addItem( pyRankItem )

	def clearRanks( self ):
		self.__pyRanksPanel.clearItems()
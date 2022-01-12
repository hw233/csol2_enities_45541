# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from SubPanel import SubPanel
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from guis.controls.ComboBox import ComboBox
from guis.controls.ComboBox import ComboItem


class CopyAoZhanRank( Window ):
	panel_map = { "upperPanel" : 0, "lowerPanel" : 1 }
	def __init__( self ):
		wnd = GUI.load( "guis/general/spacecopyabout/spaceCopyAoZhan/copyAoZhanRank.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_  = True
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"

		self.__round_maps = { 32:0, 16:1, 8:2, 4:3, 2:4, 1:5 }
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.lbTitle, "SpaceCopyAoZhan:AoZhanRank", "lbTitle")
		self.__pyTabCtr = TabCtrl( wnd.tc )

		self.__pyUpperPanel = SubPanel( wnd.tc.panel_0, CopyAoZhanRank.panel_map["upperPanel"] ) # 胜者组
		self.__pyBtnUpper = TabButton( wnd.tc.btn_0 )
		self.__pyBtnUpper.selectedForeColor = ( ( 255,255,255, 255 ) )
		labelGather.setPyBgLabel( self.__pyBtnUpper, "SpaceCopyAoZhan:AoZhanRank", "btn_0")
		self.__pyTabCtr.addPage( TabPage( self.__pyBtnUpper, self.__pyUpperPanel ) )

		self.__pyLowerPanel = SubPanel( wnd.tc.panel_1, CopyAoZhanRank.panel_map["lowerPanel"] ) # 败者组
		self.__pyBtnLower = TabButton( wnd.tc.btn_1 )
		self.__pyBtnLower.selectedForeColor = ( ( 255,255,255, 255 ) )
		labelGather.setPyBgLabel( self.__pyBtnLower, "SpaceCopyAoZhan:AoZhanRank", "btn_1")
		self.__pyTabCtr.addPage( TabPage( self.__pyBtnLower, self.__pyLowerPanel ) )

		self.__pyTabCtr.onTabPageSelectedChanged.bind( self.__onPageSelected )

		self.__pyBtnRefresh = HButtonEx( wnd.btnRefresh )	# 刷新
		self.__pyBtnRefresh.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnRefresh.onLClick.bind( self.__aoZhanRefresh )
		labelGather.setPyBgLabel( self.__pyBtnRefresh, "SpaceCopyAoZhan:AoZhanRank", "btnRefresh" )

		self.__pyBtnGather = HButtonEx( wnd.btnGather )		# 集合
		self.__pyBtnGather.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnGather.onLClick.bind( self.__aoZhanGather )
		labelGather.setPyBgLabel( self.__pyBtnGather, "SpaceCopyAoZhan:AoZhanRank", "btnGather" )

		self.__pyOptionCB = ComboBox( wnd.optionBox )	# 轮次选项
		self.__pyOptionCB.text = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "options" )
		self.__pyOptionCB.foreColor = ( 0, 255, 186, 255 )
		self.__pyOptionCB.autoSelect = False
		self.__pyOptionCB.onItemSelectChanged.bind( self.__onOptionChange )

		pyRound1 = ComboItem( labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "round1" ) )
		pyRound2 = ComboItem( labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "round2" ) )
		pyRound3 = ComboItem( labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "round3" ) )
		pyRound4 = ComboItem( labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "round4" ) )
		pyRound5 = ComboItem( labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "round5" ) )
		pyRound6 = ComboItem( labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "round6" ) )

		self.__pyOptionCB.addItems( [pyRound1, pyRound2, pyRound3, pyRound4, pyRound5, pyRound6] )
		for pySelItem in self.__pyOptionCB.pyItems:
			pySelItem.h_anchor = "CENTER"

		self.__pyTabCtr.pySelPage = self.__pyTabCtr.pyPages[0]

	# -------------------------------------------------------------------
	# private
	#--------------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_AOZHAN_RANK_INFO"] = self.__receiveAoZhanInfo
		self.__triggers["EVT_ON_HIDE_AOZHAN_RANK"] = self.__onHide
		for eventMacro in self.__triggers.iterkeys():
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ):
		for eventMacro in self.__triggers.iterkeys():
			ECenter.registerEvent( eventMacro, self )

	# -------------------------------------------------------
	def __onPageSelected( self, tabCtrl ):
		tabCtrl.pySelPage.pyPanel.showPanel( self.__pyOptionCB.selIndex )

	def __aoZhanRefresh( self ):
		BigWorld.player().aoZhan_flushBattlefield()

	def __aoZhanGather( self ):
		BigWorld.player().aoZhan_gotoEnterNPC()
		self.hide()

	def __onOptionChange( self, pyItem ):
		self.__pyTabCtr.pySelPage.pyPanel.showPanel( self.__pyOptionCB.selIndex )

	def __receiveAoZhanInfo( self, warInfos, doingMatch ):
		self.clearItems()
		roundList = []
		selIndex = self.__pyOptionCB.selIndex
		for matchType, info in warInfos.infos.iteritems():
			if not matchType: continue
			round = self.__round_maps[matchType]
			roundList.append( round )
		roundList.sort()
		for index, pyItem in enumerate( self.__pyOptionCB.pyItems ):
			if index in roundList:
				pyItem.enable = True
			else:
				pyItem.enable = False
		if roundList:
			if selIndex <= roundList[0]:
				 selIndex = roundList[0]
			self.__pyOptionCB.selIndex = selIndex
		else:
			self.__pyOptionCB.selIndex = -1
		for pyPanel in self.__pyTabCtr.pyPanels:
			pyPanel.addRankInfo( warInfos, doingMatch )
		self.__pyTabCtr.pySelPage.pyPanel.showPanel( self.__pyOptionCB.selIndex )
		Window.show( self )

	def __onHide( self ):
		self.hide()

	# -------------------------------------------------------------------
	# public
	#--------------------------------------------------------------------
	def onEvent( self, macroName, *args ):
		self.__triggers[macroName]( *args )

	def clearItems( self ):
		for pyPanel in self.__pyTabCtr.pyPanels:
			pyPanel.clearItems()

	def hide( self ):
		ECenter.fireEvent( "EVT_ON_HIDE_AOZHAN_RESULT" )
		Window.hide( self )

	def onLeaveWorld( self ):
		self.clearItems()
		self.hide()
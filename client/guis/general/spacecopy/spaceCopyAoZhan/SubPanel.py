# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from guis import *
from LabelGather import labelGather
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.TabCtrl import TabPanel
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ODListPanel import ODListPanel

class SubPanel( TabPanel ):
	def __init__( self, panel, groupID ):
		TabPanel.__init__( self, panel )
		self.__groupID = groupID

		self.__winnerInfos = {}
		self.__failureInfos = {}
		self.__round_maps = { 1:32, 2:16, 3:8, 4:4, 5:2, 6:1 }
		self.__initPanel( panel )

	def __initPanel( self, panel ):
		self.__pyBtnRank = HButtonEx( panel.subPanel.btn_0 )
		self.__pyBtnRank.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnRank, "SpaceCopyAoZhan:AoZhanRank", "btnRank" )

		self.__pyBtnPlayerName = HButtonEx( panel.subPanel.btn_1 )
		self.__pyBtnPlayerName.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnPlayerName, "SpaceCopyAoZhan:AoZhanRank", "btnPlayerName" )

		self.__pyBtnFightTime = HButtonEx( panel.subPanel.btn_2 )
		self.__pyBtnFightTime.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnFightTime, "SpaceCopyAoZhan:AoZhanRank", "btnFightTime" )

		self.__pyBtnResult = HButtonEx( panel.subPanel.btn_3 )
		self.__pyBtnResult.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnResult, "SpaceCopyAoZhan:AoZhanRank", "btnResult" )

		self.__pyListPanel = ODListPanel( panel.subPanel.clipPanel, panel.subPanel.sbar )
		self.__pyListPanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pyListPanel.onDrawItem.bind( self.__drawListItem )
		self.__pyListPanel.ownerDraw = True
		self.__pyListPanel.itemHeight = 23
		self.__pyListPanel.autoSelect = False

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initListItem( self, pyViewItem ):
		pyRankItem = RankItem()
		pyViewItem.addPyChild( pyRankItem )
		pyViewItem.pyItem = pyRankItem
		pyRankItem.left = 0
		pyRankItem.top = 0

	def __drawListItem( self, pyViewItem ):
		pyRankItem = pyViewItem.pyItem
		pyRankItem.resetText( pyViewItem.listItem )
		if pyViewItem.selected:			# 选中状态
			pyRankItem.resetColor( ( 60, 255, 0, 255 ) )
		else:
			pyRankItem.resetColor( ( 255, 255, 255, 255 ) )

	def __getWinnerInfoByRound( self, warInfos, round, doingMatch ):
		winnerInfos = []
		index = self.__round_maps[round]
		if not index in warInfos.infos.keys(): return winnerInfos
		resultInfos = self.__getResultInfos( warInfos, doingMatch )
		roundInfos = self.__getRoundInfos( warInfos, doingMatch )
		if not index in roundInfos.keys(): return winnerInfos
		# 胜者组排序
		rankInfo = {}
		timeInfo = {}
		actInfo = {} #胜利
		absInfo = {} #失败
		for dbid in warInfos.infos[index].joinList:
			if dbid in roundInfos[index].keys():
				room = warInfos.infos[index].getEnterRoom( dbid )
				useTime = int( room.useTime )
				if roundInfos[index][dbid]["vicOrDef"] == labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "vicText" ):	# 胜利
					actInfo[dbid] = useTime
				else:
					absInfo[dbid] = useTime
			else:
				absInfo[dbid] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "nullText" )
		rankList = sorted( actInfo.items(), key=lambda e:e[1], reverse=False )
		rankList.extend( absInfo.items() )
		for dex, rank in enumerate( rankList ):
			id = rank[0]
			rankInfo[id] = dex + 1
			timeInfo[id] = rank[1]
		for dbid in warInfos.infos[index].joinList:
			winnerInfo = {}
			winnerInfo["rank"] = rankInfo[dbid]
			winnerInfo["playerName"] = warInfos.joinDatas[dbid].playerName
			if doingMatch == index:
				winnerInfo["useTime"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "nullText" )
			else:
				winnerInfo["useTime"] = timeInfo[dbid]
			winnerInfo["result"] = resultInfos[dbid]
			winnerInfos.append( winnerInfo )
		return winnerInfos

	def __getFailureInfoByRound( self, warInfos, round, doingMatch ):
		failureInfos = []
		index = self.__round_maps[round]
		if not index in warInfos.infos.keys():
			return failureInfos
		resultInfos = self.__getResultInfos( warInfos, doingMatch )
		# 败者组排序
		rankInfo = {}
		numInfo = {}
		for dbid in warInfos.infos[index].failureList:
			winNum = warInfos.getFailPlayerWinNum( dbid )
			numInfo[dbid] = winNum
		rankList = sorted( numInfo.items(),key=lambda e:e[1], reverse=True )
		for dex, rank in enumerate( rankList ):
			id = rank[0]
			rankInfo[id] = dex + 1
		for dbid in warInfos.infos[index].failureList:
			failureInfo = {}
			failureInfo["rank"] = rankInfo[dbid]
			failureInfo["playerName"] = warInfos.joinDatas[dbid].playerName
			room = warInfos.infos[index].getEnterRoom( dbid )
			if room is None:
				failureInfo["useTime"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "nullText" )
			else:
				failureInfo["useTime"] = int( room.useTime )
			if doingMatch == index:
				failureInfo["useTime"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "nullText" )
			failureInfo["result"] = resultInfos[dbid]
			failureInfos.append( failureInfo )
		return failureInfos

	def __getResultInfos( self, warInfos, doingMatch ):
		resultInfos = {}
		for dbid in warInfos.joinDatas.keys():
			resultList = []
			for i in xrange( 1, 7 ):
				resultInfo = self.__getResultInfoByRound( dbid, warInfos, i, doingMatch )
				if resultInfo == {}: continue
				resultList.append( resultInfo )
			resultInfos[dbid] = resultList
		return resultInfos

	def __getRoundInfos( self, warInfos, doingMatch ):
		roundInfos = {}
		for matchType, info in warInfos.infos.iteritems():
			roundInfo = {}
			for room in info.getRoundRooms():
				if info.getType() == csdefine.AO_ZHAN_ROOM_TYPE_NO_FAILURE:#没有失败组
					if room.aPlayer:
						playerInfo = {}
						playerInfo["group"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "groupVic" )
						if room.winner == room.aPlayer:
							playerInfo["score"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "scoreText", room.score )
							playerInfo["vicOrDef"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "vicText" )
							if room.bPlayer:
								playerInfo["groupInfo"] = [ warInfos.joinDatas[room.aPlayer].playerName, warInfos.joinDatas[room.bPlayer].playerName ]
							else:
								playerInfo["groupInfo"] = [ warInfos.joinDatas[room.aPlayer].playerName, "" ]
						else:
							playerInfo["score"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "nullText" )
							playerInfo["vicOrDef"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "defText" )
							if room.bPlayer:
								playerInfo["groupInfo"] = [ warInfos.joinDatas[room.bPlayer].playerName, warInfos.joinDatas[room.aPlayer].playerName ]
							else:
								playerInfo["groupInfo"] = [ "", warInfos.joinDatas[room.aPlayer].playerName ]
						roundInfo[room.aPlayer] = playerInfo
					if room.bPlayer:
						playerInfo = {}
						playerInfo["group"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "groupVic" )
						if room.winner == room.bPlayer:
							playerInfo["score"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "scoreText", room.score )
							playerInfo["vicOrDef"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "vicText" )
							if room.aPlayer:
								playerInfo["groupInfo"] = [ warInfos.joinDatas[room.bPlayer].playerName, warInfos.joinDatas[room.aPlayer].playerName ]
							else:
								playerInfo["groupInfo"] = [ warInfos.joinDatas[room.bPlayer].playerName, "" ]
						else:
							playerInfo["score"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "nullText" )
							playerInfo["vicOrDef"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "defText" )
							if room.aPlayer:
								playerInfo["groupInfo"] = [ warInfos.joinDatas[room.aPlayer].playerName, warInfos.joinDatas[room.bPlayer].playerName ]
							else:
								playerInfo["groupInfo"] = [ "", warInfos.joinDatas[room.bPlayer].playerName ]
						roundInfo[room.bPlayer] = playerInfo
				else:
					if room.aPlayer:
						playerInfo = {}
						playerInfo["group"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "groupVic" )
						rivalInfo = []
						if len( room.failureList ):
							for f in room.failureList:
								rivalInfo.append( warInfos.joinDatas[f].playerName )
						if rivalInfo == []: rivalInfo = ""
						if room.winner == room.aPlayer:
							playerInfo["score"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "scoreText", room.score )
							playerInfo["vicOrDef"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "vicText" )
							playerInfo["groupInfo"] = [ warInfos.joinDatas[room.aPlayer].playerName, rivalInfo ]
						else:
							playerInfo["score"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "nullText" )
							playerInfo["vicOrDef"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "defText" )
							playerInfo["groupInfo"] = [ rivalInfo, warInfos.joinDatas[room.aPlayer].playerName ]
						roundInfo[room.aPlayer] = playerInfo
					if len( room.failureList ):
						teammate = []
						for f in room.failureList:
							teammate.append( warInfos.joinDatas[f].playerName )
						for fdbid in room.failureList:
							playerInfo = {}
							playerInfo["group"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "groupDef" )
							if room.winner != room.aPlayer:
								playerInfo["score"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "scoreText", room.score )
								playerInfo["vicOrDef"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "vicText" )
								if room.aPlayer:
									playerInfo["groupInfo"] = [ teammate, warInfos.joinDatas[room.aPlayer].playerName ]
								else:
									playerInfo["groupInfo"] = [ teammate, "" ]
							else:
								playerInfo["score"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "nullText" )
								playerInfo["vicOrDef"] = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "defText" )
								if room.aPlayer:
									playerInfo["groupInfo"] = [ warInfos.joinDatas[room.aPlayer].playerName, teammate ]
								else:
									playerInfo["groupInfo"] = [ "", teammate ]
							roundInfo[fdbid] = playerInfo
			# 当前轮正在进行不显示战绩
			if doingMatch == matchType: roundInfo = {}
			roundInfos[matchType]= roundInfo
		return roundInfos

	def __getResultInfoByRound( self, dbid, warInfos, round, doingMatch ):
		resultInfo = {}
		index = self.__round_maps[round]
		if not index in warInfos.infos.keys(): return resultInfo
		roundInfos = self.__getRoundInfos( warInfos, doingMatch )
		if not index in roundInfos.keys(): return resultInfo
		if dbid in roundInfos[index].keys():
			resultInfo["round"] = round
			resultInfo["group"] = roundInfos[index][dbid]["group"]
			resultInfo["score"] = roundInfos[index][dbid]["score"]
			resultInfo["vicOrDef"] = roundInfos[index][dbid]["vicOrDef"]
			resultInfo["groupInfo"] = roundInfos[index][dbid]["groupInfo"]
		return resultInfo

	def __showPanelByIndex( self, index ):
		if not index in self.__winnerInfos.keys(): return
		if not index in self.__failureInfos.keys(): return
		self.clearItems()
		if self.__groupID == 0:		# 胜者组
			self.__pyListPanel.addItems( self.__winnerInfos[index] )
			self.__pyListPanel.sort( key = lambda item: item["rank"], reverse = False )
		elif self.__groupID == 1:	# 败者组
			self.__pyListPanel.addItems( self.__failureInfos[index] )
			self.__pyListPanel.sort( key = lambda item: item["rank"], reverse = False )

	#------------------------------------------------------------------------
	#public
	#------------------------------------------------------------------------
	def showPanel( self, index ):
		self.__showPanelByIndex( index + 1 )
		TabPanel.onShow( self )

	def addRankInfo( self, warInfos, doingMatch ):
		self.__winnerInfos = {}		# 胜者组
		self.__failureInfos = {}	# 败者组
		for i in xrange( 1, 7 ):
			self.__winnerInfos[i] = self.__getWinnerInfoByRound( warInfos, i, doingMatch )
		for j in xrange( 1, 7 ):
			self.__failureInfos[j] = self.__getFailureInfoByRound( warInfos, j, doingMatch )

	def clearItems( self ):
		self.__pyListPanel.clearItems()

# ----------------------------------------------------------------
class RankItem( GUIBaseObject ):
	def __init__( self, pyBinder = None ):
		item = GUI.load( "guis/general/spacecopyabout/spaceCopyAoZhan/rankItem.gui" )
		uiFixer.firstLoadFix( item )
		GUIBaseObject.__init__( self, item )
		self.__elements = item.elements
		self.focus = False
		self.crossFocus = False
		self.__result = []
		self.__initialize( item, pyBinder )

	def __initialize( self, item, pyBinder ) :
		self.__pyRtRank = CSRichText( item.rtRank )
		self.__pyRtRank.text = ""
		self.__pyRtRank.align = "C"

		self.__pyRtPlayerName = CSRichText( item.rtPlayerName )
		self.__pyRtPlayerName.text = ""

		self.__pyRtFightTime = CSRichText( item.rtFightTime )
		self.__pyRtFightTime.text = ""
		self.__pyRtFightTime.align = "C"

		self.__pyBtnView = HButtonEx( item.btnView )
		self.__pyBtnView.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnView, "SpaceCopyAoZhan:AoZhanRank", "btnView" )
		self.__pyBtnView.onLClick.bind( self.__onShowAoZhanResult )
		self.__pyBtnView.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyBtnView.onMouseLeave.bind( self.__onMouseLeave )

	def __onMouseEnter( self, pyBtn ):
		if pyBtn is None: return
		dsp = labelGather.getText( "SpaceCopyAoZhan:AoZhanRank", "resultTips" )
		toolbox.infoTip.showToolTips( self, dsp )

	def __onMouseLeave( self ):
		toolbox.infoTip.hide()

	def __onShowAoZhanResult( self ):
		ECenter.fireEvent( "EVT_ON_SHOW_AOZHAN_RESULT", self.__result )

	def resetText( self, info ):
		"""
		更新列表项文本
		"""
		self.__pyRtRank.text			= str( info["rank"] )
		self.__pyRtPlayerName.text		= str( info["playerName"] )
		self.__pyRtFightTime.text		= str( info["useTime"] )
		self.__result 					= info["result"]

	def resetColor( self, color ):
		"""
		更新列表项字体颜色
		"""
		self.__pyRtRank.foreColor = color
		self.__pyRtPlayerName.foreColor = color
		self.__pyRtFightTime.foreColor = color

# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ODListPanel import ODListPanel
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import Timer
import random

class SpaceCopyLiuWangMuRank( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/spacecopyabout/spaceCopyLiuWangMu/liuWangMuRank.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )		
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.__seconds = 0 	#多少秒后关闭
		self.__timeControlID = 0
		
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()
				
	def __initialize( self, wnd ):
		self.__pyStPlayersRank = StaticText( wnd.stPlayersRank )
		self.__pyStPlayersRank.text = ""
		
		self.__pyStTongsRank = StaticText( wnd.stTongsRank )
		self.__pyStTongsRank.text = ""
		
		self.__pyRtTips = CSRichText( wnd.csTips )
		self.__pyRtTips.text = ""
		
		self.__pyBtnPlayersRank = HButtonEx( wnd.playersRankPanel.btn_0 )
		self.__pyBtnPlayersRank.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnPlayersRank.onLClick.bind( self.__onSorByPlayersRank )
		labelGather.setPyBgLabel( self.__pyBtnPlayersRank, "SpaceCopyLiuWangMuRank:main", "btn_0" )
		
		self.__pyBtnPlayersName = HButtonEx( wnd.playersRankPanel.btn_1 )
		self.__pyBtnPlayersName.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnPlayersName.onLClick.bind( self.__onSorByPlayersName )
		labelGather.setPyBgLabel( self.__pyBtnPlayersName, "SpaceCopyLiuWangMuRank:main", "btn_1" )
		
		self.__pyBtnPlayersTongName = HButtonEx( wnd.playersRankPanel.btn_2 )
		self.__pyBtnPlayersTongName.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnPlayersTongName.onLClick.bind( self.__onSorByPlayersTongName )
		labelGather.setPyBgLabel( self.__pyBtnPlayersTongName, "SpaceCopyLiuWangMuRank:main", "btn_2" )
		
		self.__pyBtnPlayersDamage = HButtonEx( wnd.playersRankPanel.btn_3 )
		self.__pyBtnPlayersDamage.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnPlayersDamage.onLClick.bind( self.__onSorByPlayersDamage)
		labelGather.setPyBgLabel( self.__pyBtnPlayersDamage, "SpaceCopyLiuWangMuRank:main", "btn_3" )
		
		self.__pyBtnTongsRank = HButtonEx( wnd.tongsRankPanel.btn_0 )
		self.__pyBtnTongsRank.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnTongsRank.onLClick.bind( self.__onSorByTongsRank )
		labelGather.setPyBgLabel( self.__pyBtnTongsRank, "SpaceCopyLiuWangMuRank:main", "btn_0" )
		
		self.__pyBtnTongsName = HButtonEx( wnd.tongsRankPanel.btn_1 )
		self.__pyBtnTongsName.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnTongsName.onLClick.bind( self.__onSorByTongsName )
		labelGather.setPyBgLabel( self.__pyBtnTongsName, "SpaceCopyLiuWangMuRank:main", "btn_2" )
		
		self.__pyBtnTongsDamage = HButtonEx( wnd.tongsRankPanel.btn_2 )
		self.__pyBtnTongsDamage.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnTongsDamage.onLClick.bind( self.__onSorByTongsDamage )
		labelGather.setPyBgLabel( self.__pyBtnTongsDamage, "SpaceCopyLiuWangMuRank:main", "btn_3" )
		
		self.__pyBtnOk = HButtonEx( wnd.btnOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnOk.onLClick.bind( self.__onLeaveSpace )
		labelGather.setPyBgLabel( self.__pyBtnOk, "SpaceCopyLiuWangMuRank:main", "btnOk" )
		
		
		self.__pyPlayersRankListPanel = ODListPanel( wnd.playersRankPanel.clipPanel, wnd.playersRankPanel.sbar )
		self.__pyPlayersRankListPanel.onViewItemInitialized.bind( self.__initPlayerListItem )
		self.__pyPlayersRankListPanel.onDrawItem.bind( self.__drawListItem )
		self.__pyPlayersRankListPanel.ownerDraw = True
		self.__pyPlayersRankListPanel.itemHeight = 23.0
		
		self.__pyTongsLankListPanel = ODListPanel( wnd.tongsRankPanel.clipPanel, wnd.tongsRankPanel.sbar )
		self.__pyTongsLankListPanel.onViewItemInitialized.bind( self.__initTongListItem )
		self.__pyTongsLankListPanel.onDrawItem.bind( self.__drawListItem )
		self.__pyTongsLankListPanel.ownerDraw = True
		self.__pyTongsLankListPanel.itemHeight = 23.0
		
		labelGather.setPyLabel( self.pyLbTitle_, "SpaceCopyLiuWangMuRank:main", "lbTitle" )
		labelGather.setPyLabel( self.__pyStPlayersRank, "SpaceCopyLiuWangMuRank:main", "stPlayersRank" )
		labelGather.setPyLabel( self.__pyStTongsRank, "SpaceCopyLiuWangMuRank:main", "stTongsRank" )
		
	def __initPlayerListItem( self, pyViewItem ):
		pyPlayer = PlayerInfoItem()
		pyViewItem.addPyChild( pyPlayer )
		pyPlayer.left = 0
		pyPlayer.top = 0
		pyViewItem.crossFocus = False
		pyViewItem.pyItem = pyPlayer
		
	def __initTongListItem( self, pyViewItem ):
		pyTong = TongInfoItem()
		pyViewItem.addPyChild( pyTong )
		pyTong.left = 0
		pyTong.top = 0
		pyViewItem.crossFocus = False
		pyViewItem.pyItem = pyTong
		
	def __drawListItem( self, pyViewItem ):
		pyItem = pyViewItem.pyItem
		pyItem.setInfo( pyViewItem )
		
	def __registerTriggers( self ):	
		self.__triggers["EVT_ON_LIU_WANG_MU_SHOW_RANKLIST"] = self.__receiveRankInfo			
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )
			
	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )
			
	def __onSorByPlayersRank( self ):
		pass
		
	def __onSorByPlayersName( self ):
		pass
	
	def __onSorByPlayersTongName( self ):
		pass
		
	def __onSorByPlayersDamage( self ):
		pass
		
	def __onSorByTongsRank( self ):
		pass
		
	def __onSorByTongsName( self ):
		pass
	
	def __onSorByTongsDamage( self ):
		pass
		
	def __onLeaveSpace( self ):
		area = random.random() * 10 * 2 - 10
		BigWorld.player().teleportPlayer("zly_bi_shi_jian", Math.Vector3(-457.0 + area, 60.0, -841.0 + area), Math.Vector3(0, 0, 0))
		self.hide()

		
	def __setTips( self ):
		if self.__seconds <= 0:
			Timer.cancel( self.__timeControlID )
			self.__timeControlID = 0
			self.hide()
		else:
			self.__seconds -= 1
			timeStr = PL_Font.getSource("%s"% self.__seconds,fc = "c3")
			self.__pyRtTips.text = labelGather.getText( "SpaceCopyLiuWangMuRank:main", "rtTips")%timeStr
			
	def __receiveRankInfo( self, msg ):
		playersDamage = msg[0]
		tongsDamage = msg[1]
		player_tongDict = msg[2]
		newPlayersDamage = []
		#在个人伤害列表加上名次和帮会名字
		for rank, playerDamage in enumerate( playersDamage ):
			playerDamage = list( playerDamage )
			tongName = player_tongDict.get( playerDamage[0])
			playerDamage.insert( 0, rank +1 )
			playerDamage.insert( 2, tongName )
			newPlayersDamage.append( playerDamage )
		#在帮会伤害列表加上名次
		newTongsDamage = []
		for rank, tongDamage in enumerate( tongsDamage ):
			tongDamage = list( tongDamage )
			tongDamage.insert( 0, rank + 1 )
			newTongsDamage.append( tongDamage )
		for playerDamage in newPlayersDamage:
			self.__pyPlayersRankListPanel.addItem( playerDamage )
		self.__pyPlayersRankListPanel.sort( key = lambda item: item[0])	
		for tongDamage in newTongsDamage:
			self.__pyTongsLankListPanel.addItem( tongDamage )
		self.__pyTongsLankListPanel.sort( key = lambda item:item[0] )
		Window.show( self )
		self.__seconds = 30
		self.__timeControlID = Timer.addTimer( 0, 1, self.__setTips )
		
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
	def hide( self ):
		self.__pyPlayersRankListPanel.clearItems()
		self.__pyTongsLankListPanel.clearItems()
		Window.hide( self )
		
	def onLeaveWorld( self ) :
		self.hide()
		
from guis.controls.ListItem import MultiColListItem		
class PlayerInfoItem( MultiColListItem ):

	_ITEM = None

	def __init__( self ):
		if PlayerInfoItem._ITEM is None :
			PlayerInfoItem._ITEM = GUI.load( "guis/general/spacecopyabout/spaceCopyLiuWangMu/playersRankItem.gui" )
		item = util.copyGuiTree( PlayerInfoItem._ITEM )
		uiFixer.firstLoadFix( item )
		MultiColListItem.__init__( self, item )
		self.commonBackColor = ( 255, 255, 255, 255 )
		self.selectedBackColor = ( 255, 255, 255, 255 )
		self.highlightBackColor = ( 255, 255, 255, 255 )
		self.focus = False

	def setInfo( self, pyViewItem ):
		"""
		更新玩家排行信息
		"""
		playerInfo = pyViewItem.listItem
		rank = playerInfo[0]
		playerName = playerInfo[1]
		tongName = playerInfo[2]
		if tongName == None:tongName = ""
		damage = playerInfo[3]
		self.setTextes( rank, playerName, tongName, damage )
		
		
class TongInfoItem( MultiColListItem ):

	_ITEM = None

	def __init__( self ):
		if TongInfoItem._ITEM is None :
			TongInfoItem._ITEM = GUI.load( "guis/general/spacecopyabout/spaceCopyLiuWangMu/tongsRankItem.gui" )
		item = util.copyGuiTree( TongInfoItem._ITEM )
		uiFixer.firstLoadFix( item )
		MultiColListItem.__init__( self, item )
		self.commonBackColor = ( 255, 255, 255, 255 )
		self.selectedBackColor = ( 255, 255, 255, 255 )
		self.highlightBackColor = ( 255, 255, 255, 255 )
		self.focus = False

	def setInfo( self, pyViewItem ):
		"""
		更新帮会排行信息
		"""
		tongInfo = pyViewItem.listItem
		rank = tongInfo[0]
		tongName = tongInfo[1]
		if tongName == None:tongName = ""
		damage = tongInfo[2]
		self.setTextes( rank, tongName, damage )
				
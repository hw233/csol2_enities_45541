# -*- coding: gb18030 -*-

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ODListPanel import ODListPanel

class CopyJueDiFanJiRank( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/spacecopyabout/spaceCopyJueDiFanJi/copyJueDiFanJiRank.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )		
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"

		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ):
		self.__pyBtnPlayersRank = HButtonEx( wnd.tc.btnRank )
		self.__pyBtnPlayersRank.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnPlayersRank.onLClick.bind( self.__onSorByPlayersRank )
		labelGather.setPyBgLabel( self.__pyBtnPlayersRank, "SpaceCopyJueDiFanJi:JueDiRank", "btnRank" )

		self.__pyBtnPlayersName = HButtonEx( wnd.tc.btnPlayerName )
		self.__pyBtnPlayersName.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnPlayersName.onLClick.bind( self.__onSorByPlayersName )
		labelGather.setPyBgLabel( self.__pyBtnPlayersName, "SpaceCopyJueDiFanJi:JueDiRank", "btnPlayerName" )

		self.__pyBtnPlayersIntegral = HButtonEx( wnd.tc.btnIntegral )
		self.__pyBtnPlayersIntegral.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnPlayersIntegral.onLClick.bind( self.__onSorByPlayersIntegral )
		labelGather.setPyBgLabel( self.__pyBtnPlayersIntegral, "SpaceCopyJueDiFanJi:JueDiRank", "btnIntegral" )

		self.__pyPlayersRankListPanel = ODListPanel( wnd.tc.clipPanel, wnd.tc.sbar )
		self.__pyPlayersRankListPanel.onViewItemInitialized.bind( self.__initRankListItem )
		self.__pyPlayersRankListPanel.onDrawItem.bind( self.__drawListItem )
		self.__pyPlayersRankListPanel.ownerDraw = True
		self.__pyPlayersRankListPanel.itemHeight = 23.0

		labelGather.setLabel( wnd.lbTitle, "SpaceCopyJueDiFanJi:JueDiRank", "lbTitle" )

	def __initRankListItem( self, pyViewItem ):
		pyItem = RankItem()
		pyViewItem.addPyChild( pyItem )
		pyItem.left = 0
		pyItem.top = 0
		pyViewItem.crossFocus = False
		pyViewItem.pyItem = pyItem

	def __drawListItem( self, pyViewItem ):
		pyItem = pyViewItem.pyItem
		pyItem.setInfo( pyViewItem )

	# ----------------------------------------------------------
	# pravite
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_JUEDI_RANK"] = self.__receiveBulletin
		self.__triggers["EVT_ON_SHOW_JUEDI_RANK_LIST"] = self.__onShow
		self.__triggers["EVT_ON_HIDE_JUEDI_RANK_LIST"] = self.__onHide
		for key in self.__triggers:
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ):
		for key in self.__triggers:
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __onSorByPlayersRank( self ):
		pass

	def __onSorByPlayersName( self ):
		pass

	def __onSorByPlayersIntegral( self ):
		pass

	def __onShow( self ):
		self.show()

	def __onHide( self ):
		self.hide()

	def __receiveBulletin( self, scoreList ):
		sorceItems = []
		self.__pyPlayersRankListPanel.clearItems()
		for index, sorceInfo in enumerate( scoreList ):
			info = [index + 1, sorceInfo[0], sorceInfo[1]]
			sorceItems.append( info )
		for sorceItem in sorceItems:
			self.__pyPlayersRankListPanel.addItem( sorceItem )
		self.__pyPlayersRankListPanel.sort( key = lambda item:item[0] )
		Window.show( self )

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onLeaveWorld( self ):
		self.__pyPlayersRankListPanel.clearItems()
		self.hide()


from guis.controls.ListItem import MultiColListItem

class RankItem( MultiColListItem ):

	_ITEM = None

	def __init__( self ):
		if RankItem._ITEM is None :
			RankItem._ITEM = GUI.load( "guis/general/spacecopyabout/spaceCopyJueDiFanJi/rankItem.gui" )
		item = util.copyGuiTree( RankItem._ITEM )
		uiFixer.firstLoadFix( item )
		MultiColListItem.__init__( self, item )
		self.commonBackColor = ( 255, 255, 255, 255 )
		self.selectedBackColor = ( 255, 255, 255, 255 )
		self.highlightBackColor = ( 255, 255, 255, 255 )
		self.focus = False

	def setInfo( self, pyViewItem ):
		"""
		"""
		rankInfo = pyViewItem.listItem
		rank = rankInfo[0]
		playerName = rankInfo[1]
		if playerName == None: playerName = ""
		integral = rankInfo[2]
		self.setTextes( rank, playerName, integral )

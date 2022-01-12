# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import ShareTexts
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ODListPanel import ODListPanel
from guis.controls.ListItem import MultiColListItem

g_chs_class = { csdefine.CLASS_FIGHTER	: ShareTexts.PROFESSION_FIGHTER,
				csdefine.CLASS_SWORDMAN	: ShareTexts.PROFESSION_SWORD,
				csdefine.CLASS_ARCHER	: ShareTexts.PROFESSION_ARCHER,
				csdefine.CLASS_MAGE		: ShareTexts.PROFESSION_MAGIC,
			}

class CopyAoZhanSignUp( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/spacecopyabout/spaceCopyAoZhan/copyAoZhanSignUp.gui" )
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
		self.__pyBtnSignUp = HButtonEx( wnd.btnSignUp, self )	# 报名
		self.__pyBtnSignUp.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSignUp.onLClick.bind( self.__aoZhanSignUp )
		labelGather.setPyBgLabel( self.__pyBtnSignUp, "SpaceCopyAoZhan:AoZhanSignUp", "btnSignUp" )

		self.__pyLbText = CSRichText( wnd.lbText )
		self.__pyLbText.align = "L"
		self.__pyLbText.text = ""

		self.__pyBtnNumber = HButtonEx( wnd.tc.btnNumber )
		self.__pyBtnNumber.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnNumber.onLClick.bind( self.__onSorByNumber )
		labelGather.setPyBgLabel( self.__pyBtnNumber, "SpaceCopyAoZhan:AoZhanSignUp", "btnNumber" )

		self.__pyBtnPlayersName = HButtonEx( wnd.tc.btnPlayerName )
		self.__pyBtnPlayersName.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnPlayersName.onLClick.bind( self.__onSorByPlayersName )
		labelGather.setPyBgLabel( self.__pyBtnPlayersName, "SpaceCopyAoZhan:AoZhanSignUp", "btnPlayerName" )

		self.__pyBtnLevel = HButtonEx( wnd.tc.btnLevel )
		self.__pyBtnLevel.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnLevel.onLClick.bind( self.__onSorByLevel )
		labelGather.setPyBgLabel( self.__pyBtnLevel, "SpaceCopyAoZhan:AoZhanSignUp", "btnLevel" )

		self.__pyBtnClass = HButtonEx( wnd.tc.btnClass )
		self.__pyBtnClass.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnClass.onLClick.bind( self.__onSorByClass )
		labelGather.setPyBgLabel( self.__pyBtnClass, "SpaceCopyAoZhan:AoZhanSignUp", "btnClass" )

		self.__pySignUpListPanel = ODListPanel( wnd.tc.clipPanel, wnd.tc.sbar )
		self.__pySignUpListPanel.onViewItemInitialized.bind( self.__initSignUpListItem )
		self.__pySignUpListPanel.onDrawItem.bind( self.__drawListItem )
		self.__pySignUpListPanel.ownerDraw = True
		self.__pySignUpListPanel.itemHeight = 23.0

		labelGather.setLabel( wnd.lbTitle, "SpaceCopyAoZhan:AoZhanSignUp", "lbTitle" )

	def __initSignUpListItem( self, pyViewItem ):
		pyItem = SignUpItem()
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
		self.__triggers["EVT_ON_SHOW_AOZHAN_SIGNUP_WINDOW"] = self.__showAoZhanSignUpWindow
		self.__triggers["EVT_ON_AOZHAN_SIGNUP"] = self.__onAoZhanSignUp
		self.__triggers["EVT_ON_AOZHAN_IS_JOIN"] = self.__isJoinAoZhan
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ):
		for key in self.__triggers.iterkeys():
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __onSorByNumber( self ):
		pass

	def __onSorByPlayersName( self ):
		pass

	def __onSorByLevel( self ):
		pass

	def __onSorByClass( self ):
		pass

	def __aoZhanSignUp( self ):
		BigWorld.player().aoZhan_signUp()

	def __onAoZhanSignUp( self ):
		if self.visible:
			BigWorld.player().aoZhan_getSignUpList()

	def __isJoinAoZhan( self, isJoin ):
		pass

	def __showAoZhanSignUpWindow( self, signUpList ):
		self.__pySignUpListPanel.clearItems()
		dbidList = []
		for info in signUpList:
			dbidList.append( info.databaseID )
		dbidList.sort()
		index = 1
		signUpItems = []
		for dbid in dbidList:
			for info in signUpList:
				if dbid == info.databaseID:
					item = [index, info.playerName, info.playerLevel, info.playerClass]
			signUpItems.append( item )
			index += 1
		for signUpItem in signUpItems:
			self.__pySignUpListPanel.addItem( signUpItem )
		self.__pySignUpListPanel.sort( key = lambda item:item[0] )
		self.__pyLbText.text = labelGather.getText( "SpaceCopyAoZhan:AoZhanSignUp", "signUpText", len( signUpItems ) )
		Window.show( self )

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, macroName, *args ):
		self.__triggers[macroName]( *args )

	def onLeaveWorld( self ):
		self.__pySignUpListPanel.clearItems()
		self.hide()


# ---------------------------------------------------------
class SignUpItem( MultiColListItem ):
	def __init__( self ):
		item = GUI.load( "guis/general/spacecopyabout/spaceCopyAoZhan/signUpItem.gui" )
		uiFixer.firstLoadFix( item )
		MultiColListItem.__init__( self, item )
		self.commonBackColor = ( 255, 255, 255, 255 )
		self.selectedBackColor = ( 255, 255, 255, 255 )
		self.highlightBackColor = ( 255, 255, 255, 255 )
		self.focus = False

	def setInfo( self, pyViewItem ):
		"""
		"""
		signUpInfo = pyViewItem.listItem
		number = signUpInfo[0]
		playerName = signUpInfo[1]
		if playerName is None: playerName = ""
		level = signUpInfo[2]
		pyClass = signUpInfo[3]
		gClass = g_chs_class.get( pyClass, "" )
		self.setTextes( number, playerName, level, gClass )

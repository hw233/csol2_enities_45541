# -*- coding: gb18030 -*-
#


import weakref
from guis import *
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.controls.RichText import RichText
from guis.tooluis.CSMLRichTextBox import CSMLRichTextBox
from AbstractTemplates import Singleton
from LabelGather import labelGather

class TeamVoteWnd( Singleton, Window ):

	__instance = None
	__triggers = {}

	def __init__( self ):
		assert TeamVoteWnd.__instance is None,"TeamVoteWnd instance has been created"
		TeamVoteWnd.__instance = self
		wnd = GUI.load( "guis/general/teammateinfo/votewnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )
		self.addToMgr( "teamVoteWnd" )
		self.__suffererID = 0
		self.__initiatorID = 0

	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "teammateinfo:tmbox_MU", "kickingVote" )
		self.__pyRtWarning = RichText( wnd.rtWarning )
		self.__pyRtWarning.aglin = "L"
		self.__pyRtWarning.text = ""

		self.__pyBtnOk = HButtonEx( wnd.btnOK )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnOk, "teammateinfo:tmbox_MU", "kickOk" )
		self.__pyBtnOk.onLClick.bind( self.__onOK )
	
		self.__pyBtnCancel = HButtonEx( wnd.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "teammateinfo:tmbox_MU", "kickCancel" )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		
		self.__pyTextBox = CSMLRichTextBox( wnd.textBox.panel, wnd.textBox.sbar )
		self.__pyTextBox.maxLength = 220.0
		self.__pyTextBox.onTextChanged.bind( self.__onTextChange )
		self.__pyTextBox.text = ""
	
	def __onTextChange( self ):
		self.__pyBtnOk.enable = self.__pyTextBox.text != ""
	
	def __onOK( self, pyBtn ):
		if pyBtn is None:return
		reason = self.__pyTextBox.text
		playerID = BigWorld.player().id
		if not self.__initiatorID:
			BigWorld.player().initiateVoteForKickingTeammate( self.__suffererID, reason )
		else :
			BigWorld.player().voteToKickTeammate( True )
		self.hide()
		
	def __onCancel( self, pyBtn ):
		if pyBtn is None:return
		playerID = BigWorld.player().id
		if not self.__initiatorID:
			self.hide()
		else :
			BigWorld.player().voteToKickTeammate( False )
			self.hide()

	@staticmethod
	def instance():
		"""
		get the exclusive instance of AutoFightWindow
		"""
		if TeamVoteWnd.__instance is None:
			TeamVoteWnd.__instance = TeamVoteWnd()
		return TeamVoteWnd.__instance

	@staticmethod
	def getInstance():
		"""
		"""
		return TeamVoteWnd.__instance

	def show( self, pyOwner ):
		self.__pyTextBox.text = ""
		self.__pyTextBox.readOnly = False
		self.__suffererID = pyOwner.teammateID
		self.__pyRtWarning.text = labelGather.getText("teammateinfo:tmbox_MU", "kickReason" )
		Window.show( self )


	def hide( self ):
		TeamVoteWnd.__instance=None
		Window.hide( self )
		
	@classmethod
	def __onWndShow( SELF,initiatorID, suffererID, reason ):
		print "__onWndShow",initiatorID, suffererID, reason
		#pass
		self = SELF.inst
		self.__pyTextBox.text = reason
		self.__pyTextBox.readOnly = True
		self.__suffererID = suffererID
		self.__initiatorID = initiatorID
		self.__pyRtWarning.text = labelGather.getText("teammateinfo:tmbox_MU", "kickReason" )
		Window.show( self )

	@classmethod
	def onEvent( SELF, evtMacro, *args) :
		SELF.__triggers[ evtMacro ]( *args )

	@classmethod
	def registerEvents( SELF ) :
		SELF.__triggers[ "EVT_ON_KICKVOTE_WND_SHOW" ] = SELF.__onWndShow
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

TeamVoteWnd.registerEvents()
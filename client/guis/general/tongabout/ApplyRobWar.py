# -*- coding: gb18030 -*-
#
# $Id: FoundTong.py,v 1.4 2008-08-14 02:20:08 kebiao Exp $

"""
implement FoundTong window
"""
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.TextBox import TextBox
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
import GUIFacade

class ApplyRobWar( Window ):
	def __init__( self ):
		panel = GUI.load( "guis/general/tongabout/tongwar/tongwar.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 	= True
		self.__triggers = {}
		self.__registerTriggers()

		self.__pyBtnOk = Button( panel.btnOk, self )
		self.__pyBtnOk.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onOk )
		labelGather.setPyBgLabel( self.__pyBtnOk, "TongAbout:ApplyRobWar", "btnOk" )

		self.__pyTextBox = TextBox( panel.nameBox.box, self )
		self.__pyTextBox.onTextChanged.bind( self.__onTextChange )
		self.__pyTextBox.inputMode = InputMode.COMMON
		self.__pyTextBox.text = ""
		self.maxLength = 14

		self.__pyBtnCancel = Button( panel.btnCancel,self)
		self.__pyBtnCancel.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "TongAbout:ApplyRobWar", "btnCancel" )
		labelGather.setLabel( panel.lbTitle, "TongAbout:ApplyRobWar", "lbTitle" )
		labelGather.setLabel( panel.tongName, "TongAbout:ApplyRobWar", "tongName" )

	# -------------------------------------------------
	def __registerTriggers( self ) :
		"""
		"""
		self.__triggers["EVT_ON_TOGGLE_TONG_REQUEST_ROB_WAR"] = self.show
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	def onEvent( self, eventMacro, *args ) :
		"""
		"""
		self.__triggers[eventMacro]( *args )
	# -------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onOk( self ) :
		if self.notify_() :
			BigWorld.player().tong_requestRobWar( self.__pyTextBox.text.strip() )
			self.__pyTextBox.text = ""
			self.hide()

	def __onCancel( self ) :
		self.hide()

	def __isHasDigit( self, text ):
		for letter in text:
			if letter.isdigit():
				return True
			else:
				continue
		return False
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def notify_( self ) :
		text = self.__pyTextBox.text.strip()
		if text == "" :
			showAutoHideMessage( 3.0, 0x0962, mbmsgs[0x0c22] )
			return False
		return True

	def __onTextChange( self ) :
		self.__pyBtnOk.enable = self.__pyTextBox.text != ""

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------

	def show( self ) :
		Window.show( self )
		self.__pyTextBox.tabStop = True

	def hide( self ):
		self.__pyTextBox.clear()
		Window.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )

	def onLeaveWorld( self ) :
		self.hide()
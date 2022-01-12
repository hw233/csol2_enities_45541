# -*- coding: gb18030 -*-
#
# $Id: MailWindow.py,v 1.5 2008-08-26 02:15:22 huangyongwei Exp $

from guis import *
from LabelGather import labelGather
from guis.common.TrapWindow import UnfixedTrapWindow
from guis.controls.TabCtrl import TabCtrl
from guis.controls.StaticText import StaticText
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from SendPanel import SendPanel
from MailBox import MailBox
import event.EventCenter as ECenter
import GUIFacade
import csconst

class MailWindow( UnfixedTrapWindow ):

	_cc_defIndex = 1
	_cc_row		= 7

	def __init__( self ):
		wnd = GUI.load( "guis/general/mailwindow/window.gui" )
		uiFixer.firstLoadFix( wnd )
		UnfixedTrapWindow.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = True
		self.nowPanel = 0 #区别目前显示的是那个面板 0收信 1发信 by姜毅

		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyTabCtrl = TabCtrl( wnd.tc )

		self.__pyMailBox = MailBox( wnd.tc.panel_0, self )
		self.__pyReceiveBtn = TabButton( wnd.tc.btn_0 )
		self.__pyReceiveBtn.commonMapping = util.getStateMapping( self.__pyReceiveBtn.size, UIState.MODE_R3C1, UIState.ST_R1C1 )
		self.__pyReceiveBtn.selectedMapping = util.getStateMapping(self.__pyReceiveBtn.size, UIState.MODE_R3C1, UIState.ST_R2C1 )
		self.__pyReceiveBtn.selectedForeColor = ( 142, 216, 217, 255 )
		labelGather.setPyBgLabel( self.__pyReceiveBtn, "MailWindow:main", "btn_0" )
		self.__pyReceiveBtn.onLClick.bind( self.__onShowMailBox )
		self.__pyMailBoxPage = TabPage( self.__pyReceiveBtn, self.__pyMailBox )
		self.__pyTabCtrl.addPage( self.__pyMailBoxPage )

		self.__pySendPanel = SendPanel( wnd.tc.panel_1, self )
		self.__pySendBtn = TabButton( wnd.tc.btn_1 )
		self.__pySendBtn.commonMapping = util.getStateMapping( self.__pySendBtn.size, UIState.MODE_R3C1, UIState.ST_R1C1 )
		self.__pySendBtn.selectedMapping = util.getStateMapping(self.__pySendBtn.size, UIState.MODE_R3C1, UIState.ST_R2C1 )
		self.__pySendBtn.selectedForeColor = ( 142, 216, 217, 255 )
		labelGather.setPyBgLabel( self.__pySendBtn, "MailWindow:main", "btn_1" )
		self.__pySendBtn.onLClick.bind( self.__onShowSend )
		self.__pySendPage = TabPage( self.__pySendBtn, self.__pySendPanel )
		self.__pyTabCtrl.addPage( self.__pySendPage )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTrapTriggered_( self, entitiesInTrap ) :
		"""
		陷阱触发
		@param	entitiesInTrap		: 陷阱里的ENTITY
		@type	entitiesInTrap		: LIST
		"""
		if self.trappedEntity not in entitiesInTrap :
			BigWorld.player().mailOverWithNPC()
			self.hide()

	# --------------------------------------------------------------------------------
	# private
	# --------------------------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_MAIL_BOX"] = self.__toggleMailWindow # 与邮件NPC对话触发游戏界面
		self.__triggers["EVT_ON_RESTORE_MAIL"] = self.__onRestoreMail
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	# -----------------------------------------------------------------
	def __toggleMailWindow( self, npc ): # 触发邮箱界面
		self.setTrappedEntID( npc.id )
		self.show()

	# -----------------------------------------------------------------
	def __onShowMailBox( self ):
		self.nowPanel = 0
		labelGather.setPyLabel( self.pyLbTitle_, "MailWindow:panel_0", "lbTitle" )
#		self.__pyTabCtrl.pySelPage = self.__pyMailBox

	def __onShowSend( self ):
		if self.nowPanel == 1:
			return
		self.nowPanel = 1
		labelGather.setPyLabel( self.pyLbTitle_, "MailWindow:panel_1", "lbTitle" )
#		self.__pyTabCtrl.pySelPage =  self.__pySendPanel
		self.__pySendPanel.reset()

	def __onRestoreMail( self, name ):
		labelGather.setPyLabel( self.pyLbTitle_, "MailWindow:panel_1", "lbTitle" )
		self.__pyTabCtrl.pySelPage =  self.__pySendPage
		self.__pySendPanel.restoreMail( name )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def show( self ):# 触发显示
		self.__pySendPanel.show()
		labelGather.setPyLabel( self.pyLbTitle_, "MailWindow:panel_0", "lbTitle" )
		self.__pyTabCtrl.pySelPage = self.__pyMailBoxPage
		UnfixedTrapWindow.show( self )

	def hide( self ):
		self.__pySendPanel.hide()
		self.__pyMailBox.pySelletter = None
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		UnfixedTrapWindow.hide( self )

	def onLeaveWorld( self ) :
		self.__pySendPanel.reset()
		self.__pyMailBox.reset()
		self.hide()

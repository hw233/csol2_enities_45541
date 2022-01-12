# -*- coding: gb18030 -*-
#
# $Id: Notifier.py,v 1.10 2008-08-29 02:39:28 huangyongwei Exp $

"""
活动提示按钮
"""

import event.EventCenter as ECenter
import time
from guis import *
from guis.common.RootGUI import RootGUI

class Notifier( RootGUI ) :
	def __init__( self ) :
		ui = GUI.load( "guis/general/activitycalendar/notifier.gui" )
		RootGUI.__init__( self, ui )
		self.activable_ = False
		self.moveFocus = False
		self.posZSegment = ZSegs.L5
		self.focus = True
		self.crossFocus = True
		self.movable_ = False
		self.escHide_ = False
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "BOTTOM"
		self.addToMgr( "activityNotifier" )

		self.__flashCBID = 0
		self.__flashEndTime = 0

		self.__triggers = {}
		self.__registerTriggers()

		self.visible = False


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_LOCATED_NOTIFIER_POSITION"] = self.__located

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __located( self, bottom ) :
		self.bottom = bottom

	def __flashAlpha( self, dec ) :
		if self.alpha >= 255 :
			dec = -abs( dec )
		elif self.alpha <= 50 :
			dec = abs( dec )
		alpha = self.alpha + dec
		self.alpha = max( alpha, 50 )
		self.alpha = min( alpha, 255 )
		if time.time() < self.__flashEndTime :
			self.__flashCBID = BigWorld.callback( 0.04, Functor( self.__flashAlpha, dec ) )
		else :
			self.hide()

	def __startFlash( self ) :
		self.__flashAlpha( 10 )

	def __stopFlash( self ) :
		BigWorld.cancelCallback( self.__flashCBID )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLMouseDown_( self, mods ) :
		return True

	def onLClick_( self, mods ) :
		ECenter.fireEvent( "EVT_ON_TOGGLE_ACTIVITY_WINDOW" )
		self.hide()

	def onMouseEnter_( self ) :
		rds.ccursor.set( "hand" )
		return True

	def onMouseLeave_( self ) :
		rds.ccursor.normal()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		self.__stopFlash()
		self.visible = False

	def show( self ) :
		self.__flashEndTime = time.time() + 300
		if not self.visible :
			self.__startFlash()
		RootGUI.show( self )

	def hide( self ) :
		self.__stopFlash()
		rds.ccursor.normal()
		RootGUI.hide( self )

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )
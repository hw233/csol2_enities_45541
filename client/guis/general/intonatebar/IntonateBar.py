# -*- coding: gb18030 -*-
#
# $Id: IntonateBar.py,v 1.13 2008-08-26 02:14:12 huangyongwei Exp $

"""
implement intonate bar class

2006/12/18: writen by huangyongwei
2008/04/28: rewriten by huangyongwei
"""

import GUIFacade
from guis import *
from guis.common.RootGUI import RootGUI
from guis.controls.ProgressBar import HFProgressBar


class IntonateBar( RootGUI ) :
	def __init__( self ) :
		bar = GUI.load( "guis/general/intonatebar/bar.gui" )
		uiFixer.firstLoadFix( bar )
		RootGUI.__init__( self, bar )
		self.focus = False
		self.moveFocus = False
		self.activable_ = False
		self.posZSegment = ZSegs.L1
		self.escHide_ = False
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "BOTTOM"

		self.__fader = bar.fader							# 渐显/渐隐 shader
		self.__fader.speed = 0.6
		self.__fader.value = 0
		self.__pyBar = HFProgressBar( bar.pb )				# 进度条
		self.__pyBar.speed = 0.1

		self.__startTime = 0								# 临时变量，记录开始吟唱的时间
		self.__endTime = 0									# 临时变量，记录结束吟唱的时间

		self.__intonateCBID = 0								# 吟唱倒计时的 callbackID
		self.__fadeCBID = 0									# 渐隐的 callbackID

		self.__triggers = {}
		self.__registerTriggers()


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_INTONATE"] = self.__onIntornate
		self.__triggers["EVT_ON_ROLE_INTONATE_DISTURBED"] = self.__cancelIntonate
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	# -------------------------------------------------
	def __countDown( self ) :
		"""
		吟唱倒计时
		"""
		now = BigWorld.time()
		lastTime = self.__endTime - self.__startTime
		remainTime = max( 0, self.__endTime - now )
		self.__pyBar.value = 1.0 - remainTime / lastTime
		if remainTime > 0 :
			self.__intonateCBID = BigWorld.callback( 0.01, self.__countDown )
		else :
			self.__cancelIntonate()

	# -------------------------------------------------
	def __onIntornate( self, lastTime ) :
		"""
		开始吟唱
		"""
		self.show()
		self.__fader.value = 1
		self.__fader.reset()
		BigWorld.cancelCallback( self.__fadeCBID )

		self.__pyBar.reset( 0.0 )
		self.__startTime = BigWorld.time()
		self.__endTime = self.__startTime + lastTime
		BigWorld.cancelCallback( self.__intonateCBID )
		self.__countDown()

	def __cancelIntonate( self ) :
		"""
		打断吟唱
		"""
		self.__fader.value = 0
		BigWorld.cancelCallback( self.__intonateCBID )
		BigWorld.cancelCallback( self.__fadeCBID )
		self.__fadeCBID = BigWorld.callback( 1.0, self.hide )


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onLeaveWorld( self ) :
		self.hide()

# -*- coding: gb18030 -*-
#
# $Id: CenterMessage.py,v 1.4 2008-08-26 02:21:16 huangyongwei Exp $

"""
"""

import BigWorld
import GUI
import reimpl_statusText
from event import EventCenter as ECenter
from guis import *
from guis.common.PyGUI import PyGUI


# --------------------------------------------------------------------
# --------------------------------------------------------------------
# 自动动作提示消息
# --------------------------------------------------------------------
class StatusText( PyGUI ):
	"""
	自动动作提示信息
	"""
	def __init__( self, guiFilePath ):
		word = GUI.load( guiFilePath )
		GUI.addRoot( word )
		PyGUI.__init__( self, word )
		self.visible = False


# --------------------------------------------------------------------
# 自动动作提示消息管理器
# --------------------------------------------------------------------
class StatusTextController:
	"""
	自动动作提示管理器,这里的动作提示同时只能显示一个，因此必须保证其它的动作被取消
	"""
	def __init__( self ):
#		self.__pyAutoFightText = StatusText( self.__getStatusTextGui( "autoFight" ) )
		self.__pyAutoRunText = StatusText( self.__getStatusTextGui( "autoRun" ) )
		self.__triggers = {}
#		self.__triggers["EVT_ON_START_AUTOFIGHT"] = self.__startAutofight
#		self.__triggers["EVT_ON_STOP_AUTOFIGHT"] = self.__stopAutofight
		self.__triggers["EVT_ON_START_AUTORUN"] = self.__startAutorun
		self.__triggers["EVT_ON_STOP_AUTORUN"] = self.__stopAutorun
		for key in self.__triggers :
			ECenter.registerEvent( key, self )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __startAutofight( self ) :
		self.__pyAutoFightText.visible = True

	def __stopAutofight( self ) :
		self.__pyAutoFightText.visible = False

	def __startAutorun( self, dpos ) :
		self.__pyAutoRunText.visible = True

	def __stopAutorun( self, success ) :
		self.__pyAutoRunText.visible = False
	
	@reimpl_statusText.deco_guiStatusText
	def __getStatusTextGui( self, status ):
		"""
		获取自动战斗或者自动寻路文字
		"""
		if status == "autoFight":
			return "guis/general/autofightwindow/autoFightState.gui"
		elif status == "autoRun":
			return "guis/tooluis/navigateWord/navigateWord.gui"

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

# -*- coding: gb18030 -*-
#
import csdefine
import Const
import event.EventCenter as ECenter
from guis import *
from TargetInfo import TargetInfo
from LolTargetInfo import LolTargetInfo


class TargetMgr( object ):
	def __init__( self ) :
		self.__pyTargetUI = None
		self.__triggers = {}
		self.__registerTriggers()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TARGET_BINDED"] = self.__onShowTargetInfo
		self.__triggers["EVT_ON_TARGET_UNBINDED"] = self.__onHideTrargetInfo

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
		self.__triggers = {}

	def __onShowTargetInfo( self, target ):
		if target.__class__.__name__ == "YXLMBoss":
			self.__pyTargetUI = LolTargetInfo()
		else :
			self.__pyTargetUI = TargetInfo()
		self.__pyTargetUI.onShowTargetInfo( target )

	def __onHideTrargetInfo( self, target ):
		if self.__pyTargetUI:
			self.__pyTargetUI.onHideTrargetInfo( target )
			self.__pyTargetUI = None

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def _getTargetUI( self ):
		"""
		目标头像UI
		"""
		return self.__pyTargetUI

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	targetUI = property( _getTargetUI,  )
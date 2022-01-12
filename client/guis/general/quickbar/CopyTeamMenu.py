# -*- coding: gb18030 -*-

# 寄售菜单 consignment sale menu

from guis import *
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from MenuItem import EnterCopyMItem, QuitCopyMItem, SuppleMItem, CopyTeamMItem
from LabelGather import labelGather
from MenuItem import *
import event.EventCenter as ECenter
import csdefine


class CopyTeamMenu( object ) :

	__instance = None

	def __init__( self ) :
		assert CopyTeamMenu.__instance is None, "CopyTeamMenu instance has been created!"
		CopyTeamMenu.__instance = self
		object.__init__( self )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyMenuItems = {}
		self.__pyMenu = None
		self.__initialize()

	def __del__( self ) :
		if Debug.output_del_ContextMenu :
			INFO_MSG( "CopyTeamMenu has been destroyed!" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self ) :
		self.__pyMenu = ContextMenu()
		self.__pyMenu.onBeforePopup.bind( self.__onBeforMUPopup )
		self.__pyMenu.onItemClick.bind( self.__onMenuItemClick )
#		self.__pyMenu.onAfterClose.bind( self.hide )
		self.__pyMenuItems[0] = EnterCopyMItem()
		self.__pyMenuItems[1] = QuitCopyMItem()
		self.__pyMenuItems[2] = SuppleMItem()
		self.__pyMenuItems[3] = CopyTeamMItem()

	def __registerTriggers( self ) :
		"""
		"""
		for key in self.__triggers :
			ECenter.registerEvent( key, self )
	# -------------------------------------------------
	def __onMenuItemClick( self, pyItem ) :
		"""
		点击了某个菜单项
		"""
		if pyItem is None:return
		player = BigWorld.player()
		pyItem.do( player )
		return True

	def __onBeforMUPopup( self ) :
		"""
		弹出副本组队菜单
		"""
		self.__pyMenu.pyItems.clear()
		player = BigWorld.player()
		for menuItem in self.__pyMenuItems.itervalues():
			if menuItem.check( player ):
				self.__pyMenu.pyItems.add( menuItem )
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@staticmethod
	def instance() :
		if CopyTeamMenu.__instance is None :
			CopyTeamMenu.__instance = CopyTeamMenu()
		return CopyTeamMenu.__instance

	@staticmethod
	def isInstantial() :
		"""
		是否已被实例化
		"""
		return CopyTeamMenu.__instance is not None

	def show( self ) :
		sysBar = rds.ruisMgr.systemBar
		self.__pyMenu.show()
		self.__pyMenu.top = sysBar.top + 25.0
		self.__pyMenu.right = sysBar.left + 20

	def hide( self ) :
		self.__pyMenu.hide()
		self.__triggers = {}
		self.__pyMenuItems = {}

	def onEvent( self, evtMacro, *agrs ) :
		self.__triggers[evtMacro]( *agrs )
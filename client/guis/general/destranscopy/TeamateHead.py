# -*- coding: gb18030 -*-
#
# $Id: TeamateHead.py

import csdefine
import csconst
from guis import *
from guis.controls.Control import Control
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText
from guis.controls.ContextMenu import ContextMenu
from MenuItem import QuitTeamMItem, KickMateMItem, DisbTeamMItem

class TeamateHead( Control ):
	"""
	队伍成员头像
	"""
	def __init__( self, head, dbid ):
		Control.__init__( self, head )
		self.focus = True
		self.__pyMenuItems = [QuitTeamMItem(), KickMateMItem(), DisbTeamMItem() ]
		self.__initialize( head )
		self.__dbid = dbid
		self.entityID = 0
		self.setHeadInfo( dbid )
	
	def __initialize( self, head ):
		self.__pyHeader = PyGUI( head.head )
		self.__pyHeader.texture = ""
		
		self.__pyStLevel = StaticText( head.stLevel )
		self.__pyStLevel.text = ""
		
		self.__pyStName = StaticText( head.stName )
		self.__pyStName.text = ""

		self.__pyCMenu = ContextMenu()
		self.__pyCMenu.addBinder( self )
		self.__pyCMenu.onItemClick.bind( self.__onMenuItemClick )
		self.__pyCMenu.onBeforePopup.bind( self.__onMenuPopUp )

		self.__pyHearts = {}
		for name, item in head.children:
			if not name.startswith( "heart_" ):continue
			index = int( name.split("_")[-1] )
			pyHeart = PyGUI( item )
			self.__pyHearts[index] = pyHeart

	def __onMenuPopUp( self ) :
		"""
		弹出组队菜单
		"""
		self.__pyCMenu.pyItems.clear()
		player = BigWorld.player()
		for menuItem in self.__pyMenuItems:
			if menuItem.check( self.__dbid, player ):
				self.__pyCMenu.pyItems.add( menuItem )
		return True

	def __onMenuItemClick( self, pyItem ) :
		"""
		点击了某个菜单项
		"""
		if pyItem is None:return
		player = BigWorld.player()
		pyItem.do( self.__dbid, player )
		return True
	
	def setHeadInfo( self, dbid ):
		"""
		设置头像信息
		"""
		player = BigWorld.player()
		name = ""
		level = 0
		headTexture = ""
		if dbid == player.databaseID:
			name = player.getName()
			level = player.getLevel()
			headTexture = player.getHeadTexture()
		else:
			teamMember = None
			for member in player.teamMember.values():
				if member.DBID == dbid:
					teamMember = member
					break
			if teamMember:
				name = teamMember.name
				level = teamMember.level
				headTexture = teamMember.header
		self.__pyStLevel.text = "%d"%level
		self.__pyStName.text = name
		self.__pyHeader.texture = headTexture
		self.entityID = self.__getEntityByDbid( dbid )
	
	def __getTeamMember( self, dbid ):
		"""
		获取队友信息
		"""
		player = BigWorld.player()
		for member in player.teamMember.values():
			if member.DBID == dbid:
				return member
	
	def setLivePoint( self, livePoint ):
		"""
		设置生命数
		"""
		idxs = 3 - livePoint
		for idx in range( idxs ):
			pyHeart = self.__pyHearts.get( idx, None )
			if pyHeart is None:continue
			pyHeart.visible = False

	def __getEntityByDbid( self, dbid ):
		"""
		通过dbid获取entityid
		"""
		player = BigWorld.player()
		for entityid, member in player.teamMember.items():
			if member.DBID == dbid:
				return entityid
		return 0
	
	def _setDbid( self, dbid ):
		self.__dbid = dbid
	
	def _getDbid( self ):
		return self.__dbid

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	dbid = property( _getDbid, _setDbid )
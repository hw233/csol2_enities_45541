# -*- coding: gb18030 -*-
#
# $Id: T_TransportWindow.py,v 1.1 2008-08-01 02:54:50 huangyongwei Exp $

"""
implement transport window class
"""

import ResMgr
import Language
import Define
import gbref
import ShortcutMgr
from guis import *
from guis.common.Window import *
from guis.controls.ListPanel import ListPanel
from guis.controls.ListItem import SingleColListItem
from ShortcutMgr import shortcutMgr

class TransportWindow( Window ) :
	__cc_view_rows   = 15

	def __init__( self ) :
		wnd = GUI.load( "guis/clienttools/transportwindow/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.addToMgr()
		rds.ruisMgr.transportWindow = self

		self.__pyPanel = ListPanel( wnd.clipPanel, wnd.scrollBar )
		self.__pyPanel.onItemLClick.bind( self.__onItemClick )
		self.__pyPanel.viewCount = TransportWindow.__cc_view_rows
		self.__pyPanel.selectable = False
		self.__initItems()

		sect = ResMgr.openSection( "entities/client/tools/resources/TransportWindowShortcut.xml" )
		scInfo = ShortcutMgr.SCInfo( sect )
		shortcutMgr._ShortcutMgr__shortcuts["TOGGLE_TRANSPORTWINDOW"] = scInfo
		shortcutMgr._ShortcutMgr__statusTags[Define.GST_IN_WORLD].append( "TOGGLE_TRANSPORTWINDOW" )
		shortcutMgr.setHandler( "TOGGLE_TRANSPORTWINDOW", self.__toggleVisible )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __createPyItem( self, spaceInfo ) :
		pyItem = SingleColListItem()
		pyItem.text = spaceInfo["name"]
		pyItem.onMouseEnter.bind( self.__onShowSpaceName )
		pyItem.onLMouseDown.bind( self.__onHideSpaceName )
		pyItem.onMouseLeave.bind( self.__onHideSpaceName )
		pyItem.spaceInfo = spaceInfo
		return pyItem

	def __initItems( self ) :
		sect = Language.openConfigSection( "config/client/map.xml" )
		for transport in sect.values() :
			name = transport.readString( "name" )
			position = transport.readVector3( "position" )
			space = transport.readString( "space" )
			spaceInfo = { 'name' : name, 'position' : position, 'space' : space }
			pyItem = TransportWindow.__createPyItem( self, spaceInfo )
			self.__pyPanel.addItem( pyItem )
			pyItem.focus = True
		Language.purgeConfig( sect )

	def __onItemClick( self, pyItem ) :
		spaceInfo = pyItem.spaceInfo
		player = BigWorld.player()
		if not rds.statusMgr.isInWorld() : return
		space = spaceInfo["space"]
		position = spaceInfo["position"]
		player.teleportPlayer( space, position, ( 0, 0, 0 ) )
		self.hide()

	def __toggleVisible( self ) :
		self.visible = not self.visible
		return True

	def __onShowSpaceName( self, pyItem ):
		"""
		浮动显示地图名
		"""
		if pyItem is None:return
		spaceInfo = pyItem.spaceInfo
		msg = "地图space名:%s"%spaceInfo["space"]
		toolbox.infoTip.showToolTips( pyItem, msg )
	
	def __onHideSpaceName( self ):
		"""
		隐藏浮动信息
		"""
		toolbox.infoTip.hide()
	# ----------------------------------------------------------------
	# callback
	# ----------------------------------------------------------------
	def onLeaveWorld( self ) :
		self.hide()

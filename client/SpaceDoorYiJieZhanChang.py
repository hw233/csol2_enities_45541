# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
from SpaceDoor import SpaceDoor
from config.client.msgboxtexts import Datas as mbmsgs
import MessageBox as MB
import Define

g_messagebox = None

class SpaceDoorYiJieZhanChang( SpaceDoor ):
	def __init__( self ):
		SpaceDoor.__init__( self )
	
	def onTransport( self, entitiesInTrap ):
		player = BigWorld.player()
		#DEBUG_MSG( entitiesInTrap )
		if not self.inDoor and player in entitiesInTrap:
			#INFO_MSG( "%i --> in trap, tell to cell." % self.id )
			if player.vehicle:
				player.vehicle.disMountEntity( player )
				BigWorld.callback( 2.0, self.onLeaveDartWhenEnterDoor )
				return
			player.beforeEnterDoor()
			#player.stopMove()
			self.__onEnterYiJieDoor()
			self.inDoor = True
		
		if self.inDoor and not player in entitiesInTrap:
			self.inDoor = False
			self.__onLeaveYiJieDoor()
	
	def __onEnterYiJieDoor( self ) :
		"""
		进入异界传送门时弹出确认框
		"""
		global g_messagebox
		def query( rs_id ) :
			if rs_id == MB.RS_OK :
				self.cell.enterDoor()
			global g_messagebox
			g_messagebox = None
		g_messagebox = MB.showMessage( mbmsgs[0x1100], "", MB.MB_OK_CANCEL, query, gstStatus = Define.GST_IN_WORLD )
	
	def __onLeaveYiJieDoor( self ) :
		"""
		离开异界传送门时关闭确认框
		"""
		global g_messagebox
		if g_messagebox is not None :
			g_messagebox.hide()
			g_messagebox = None
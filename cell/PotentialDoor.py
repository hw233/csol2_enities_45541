# -*- coding: gb18030 -*-
import BigWorld

from SpaceDoor import SpaceDoor
from ObjectScripts.GameObjectFactory import g_objFactory

import csstatus

QUEST_GET_SPACE_DICT = {}

class PotentialDoor( SpaceDoor ):
	"""
	潜能副本专用传送门
	"""
	def __init__( self ):
		SpaceDoor.__init__( self )
	
	def enterDoor(self, id):
		"""
		Exposed method.
		进入切换点
		@param source:	玩家ID
		@type source:	integer
		"""
		object = BigWorld.entities.get(id, None)
		
		if not object:
			return
			
		if not self.checkEnter( object ):
			return
			
		desSpace = self.getDestSpace( object )
		if not desSpace:
			return
		
		desSpaceScript = g_objFactory.getObject( desSpace )
		if not desSpaceScript:
			return
			
		desSpace, destPosition, destDirection = desSpaceScript.getSpaceBirth()
		object.beforeEnterSpaceDoor( destPosition, destDirection )
		object.gotoSpace( desSpace, destPosition, destDirection )
	
	def checkEnter( self, entity ):
		if not entity.teamMailbox:
			entity.client.onStatusMessage( csstatus.POTENTIAL_QUEST_DOOR_NOT_TEAM, "" )
			return False
		
		if self.ownerVisibleInfos != ( 0, 0 ):
			pID = self.ownerVisibleInfos[ 0 ]
			tID = self.ownerVisibleInfos[ 1 ]
			if pID != entity.id and tID != entity.teamMailbox.id:
				return False

		return SpaceDoor.enterDoorCheck( self, entity.id )
	
	def getDestSpace( self, entity ):
		"""
		获取传送的目标地图
		"""
		return "fu_ben_maps_xue_shan_0_1"
	
	def getDestPosition( self, entity ):
		return ( -9.008, 91.878, -77.756 )
	
	def getDestDirection( self, entity ):
		return ( -0.244, 74.997, 0.346 )
	
	def requestDestination( self, srcEntityID ):
		"""
		Exposed method.
		请求目的地信息
		"""
		entity = BigWorld.entities.get( srcEntityID, None )
		if entity:
			entity.clientEntity( self.id ).receiverDestination( self.getDestSpace( entity ), self.getDestPosition( entity ) )
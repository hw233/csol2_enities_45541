# -*- coding: gb18030 -*-

# cell
import BigWorld
from SpaceCopy import SpaceCopy
from GameObjectFactory import g_objFactory

SKILL_ID = 780045001			# CSOL-68 此技能为玩家加一个判断自身任务状态的buff

class SpaceCopySingle( SpaceCopy ) :
	"""
	单人地图
	"""
	def __init__( self ) :
		SpaceCopy.__init__( self )
	
	def load( self, section ):
		"""
		加载类数据
		@type	section:	PyDataSection
		@param	section:	数据段
		"""
		SpaceCopy.load( self, section )
		self._spaceConfigInfo[ "FLSDoormap" ] = self._spaceConfigInfo[ "Doormap" ]
		self._spaceConfigInfo[ "Doormap" ] = {}
	
	def onEnterCommon( self, selfEntity, baseMailbox, params ):
		"""
		"""
		SpaceCopy.onEnterCommon( self, selfEntity, baseMailbox, params )
		if selfEntity.className == "xin_fei_lai_shi_001_25_dao":
			player = BigWorld.entities.get( baseMailbox.id )
			if player:
				player.systemCastSpell( SKILL_ID )
		
	def spawnTransportDoor( self,selfEntity ):
		"""
		刷传送门
		"""
		configInfo = self.getSpaceConfig()
		for name, otherDict in configInfo[ "FLSDoormap" ].iteritems():
			BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, otherDict["position"], (0, 0, 1.644427), otherDict )

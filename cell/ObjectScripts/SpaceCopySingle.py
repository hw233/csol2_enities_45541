# -*- coding: gb18030 -*-

# cell
import BigWorld
from SpaceCopy import SpaceCopy
from GameObjectFactory import g_objFactory

SKILL_ID = 780045001			# CSOL-68 �˼���Ϊ��Ҽ�һ���ж���������״̬��buff

class SpaceCopySingle( SpaceCopy ) :
	"""
	���˵�ͼ
	"""
	def __init__( self ) :
		SpaceCopy.__init__( self )
	
	def load( self, section ):
		"""
		����������
		@type	section:	PyDataSection
		@param	section:	���ݶ�
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
		ˢ������
		"""
		configInfo = self.getSpaceConfig()
		for name, otherDict in configInfo[ "FLSDoormap" ].iteritems():
			BigWorld.createEntity( "SpaceDoor", selfEntity.spaceID, otherDict["position"], (0, 0, 1.644427), otherDict )

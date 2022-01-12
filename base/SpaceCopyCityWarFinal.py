# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *
from SpaceCopy import SpaceCopy

class SpaceCopyCityWarFinal( SpaceCopy ):
	"""
	�����ս����
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.spawnPointList = {}
		BigWorld.globalData["TongManager"].registerCityWarFinalSpaceBase( self )

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		��������һ��entity��֪ͨ
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	entity			: baseEntityʵ��
		"""
		if entityType  == "SpawnPointCityWarFinal":
			monsterType =  getattr( baseEntity, "monsterType", 0 )
			if self.spawnPointList.has_key( monsterType ):
				self.spawnPointList[ monsterType ].append( baseEntity )
			else:
				self.spawnPointList[ monsterType ] = [ baseEntity ]
		SpaceCopy.onLoadedEntity( self, entityType, baseEntity )

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		һ��������spawnPoint ������ϡ�
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		self.spawnMonster( {} )

	def spawnMonster( self, params ):
		"""
		define method
		��ʼˢ��
		"""
		# ˢ��ָ�����;ݵ�
		if params.has_key( "monsterType"):
			if not self.spawnPointList.has_key( params["monsterType"] ):
				return
			for spawnMB in self.spawnPointList[ params["monsterType"] ]:
				spawnMB.cell.createEntity( { "belong": params[ "belong" ] } )
			return
		
		for type, spawnList in self.spawnPointList.iteritems():
			if type in [ csdefine.CITY_WAR_FINAL_BASE_FLAG_GUARD ]:
				continue
			for spawnMB in spawnList:
				spawnMB.cell.createEntity( params )

	def closeSpace( self, deleteFromDB = True ):
		"""
		define method
		"""
		BigWorld.globalData["TongManager"].unRegisterCityWarFianlSpaceBase( self )
		SpaceCopy.closeSpace( self, deleteFromDB )
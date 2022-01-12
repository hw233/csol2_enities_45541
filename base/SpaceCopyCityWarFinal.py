# -*- coding: gb18030 -*-

import csdefine
from bwdebug import *
from SpaceCopy import SpaceCopy

class SpaceCopyCityWarFinal( SpaceCopy ):
	"""
	帮会夺城战决赛
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.spawnPointList = {}
		BigWorld.globalData["TongManager"].registerCityWarFinalSpaceBase( self )

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		创建好了一个entity的通知
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	entity			: baseEntity实体
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
		一个副本的spawnPoint 加载完毕。
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		self.spawnMonster( {} )

	def spawnMonster( self, params ):
		"""
		define method
		开始刷怪
		"""
		# 刷新指定类型据点
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
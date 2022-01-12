# -*- coding: gb18030 -*-

import BigWorld
from SpawnPointNormal import SpawnPointNormal

SPAWN_PLANES_ENTITY_TIMERCB = 1003

class Planes( object ):
	"""
	一个位面虚拟空间对象
	"""
	def __init__( self, spaceEntity, planesID, playerMailbox, params ):
		object.__init__( self )
		self.planesPlayers = []
		self.initPlanes( spaceEntity, planesID, playerMailbox, params )
	
	def initPlanes( self, spaceEntity, planesID, playerMailbox, params ):
		"""
		这里的一个planes并不是一个真实的space entity
		"""
		self.planesPlayers.append( playerMailbox )
		self.planesID = planesID
		self.spawnEntities( spaceEntity )
	
	def spawnEntities( self, spaceEntity ):
		"""
		刷出位面entity
		"""
		spaceEntity.spawnPlanesEntities( self.planesID )
	
	def teleportEntity( self, spaceEntity, position, direction, baseMailbox, pickData ):
		"""
		传送玩家进位面
		"""
		spaceEntity.getScript().onPlanesTeleportEntity( spaceEntity, position, direction, baseMailbox, pickData, self.planesID )
	
	def getParams( self, spaceEntity ):
		"""
		取刷新点参数
		"""
		newParams = {}
		newParams[ "planesID" ] = self.planesID
		return newParams

	def destroy( self, spaceEntity ):
		"""
		销毁位面
		"""
		spaceEntity.destoryPlanesEntity( self.planesID )

class ImpPlanesSpace( object ):
	#位面的space接口
	def __init__( self ):
		super( ImpPlanesSpace, self ).__init__()
		self._lastPlanesID = 0
		self._planesItems = {}
		self._planesSpawnEntity = {}
		self._spawnInfos = []
		self.waiteLoaderSpawnPointPlanes = []
		self.waiteLoaderSpawnPointPlanesTimerID = 0
		
	def _teleportEntityToPlanes( self, position, direction, baseMailbox, pickData ):
		"""
		define method.
		传送一个entity到指定的space位面中
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX,
		@param params: 一些关于该entity进入space的额外参数；
		@type params : PY_DICT = None
		"""
		planes = self.getEnterPlanes( baseMailbox, pickData )
		planes.teleportEntity( self, position, direction, baseMailbox, pickData )
	
	def getEnterPlanes( self, playerMailbox, params ):
		"""
		获取进入planesID
		"""	
		planesID = params.get( "planesID", 0 )
		if self._planesItems.has_key( planesID ):
			return self._planesItems[ planesID ]
			
		return self.createPlanes( playerMailbox, params )
	
	def createPlanes( self, playerMailbox, params ):
		"""
		创建一个新的位面
		这里指的并不是一个新的Space，只是一个虚拟的位面空间
		"""
		newPlanesID  = self.getNewSpacePlanesID()
		self._planesItems[ newPlanesID ] = Planes( self, newPlanesID, playerMailbox, params )
		return self._planesItems[ newPlanesID ]
	
	def destroyPlanes( self, planesID ):
		"""
		销毁一个虚拟的位面
		"""
		if self._planesItems.has_key( planesID ):
			self._planesItems[ planesID ].destroy( self )
		
		self._planesItems.pop( planesID )
	
	def getNewSpacePlanesID( self ):
		"""
		获取新的planesID
		"""
		state = 1
		pid = self._lastPlanesID
		while state > 0:
			pid = ( pid + 1 ) % 0x7FFFFFFF
			if not pid in self._planesItems:
				state = 0

		self._lastPlanesID = pid
		return pid
	
	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		加载完一个新刷点
		"""
		if isinstance( baseEntity, SpawnPointNormal ):
			self._spawnInfos.append( baseEntity )
	
	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		self.onCheckPlanesSpawnEntity()
		
	def spawnPlanesEntities( self, planesID ):
		"""
		刷出位面空间怪物
		"""
		if self.isSpawnPointLoaderOver == False:
			self.waiteLoaderSpawnPointPlanes.append( planesID )
			return
			
		if planesID != 1: #位面ID = 1则表示是第一个进入的玩家，系统的SpawnLoader已经默认刷出第一批怪物
			for sp in self._spawnInfos:
				sp.cell.createEntity( { "planesID" : planesID } )
			
			#对于直接创建的怪物重刷一新
			for entityType, spawnList in self._spawnInfoRecords.iteritems():
				if self.loadEntityUseFunc.has_key( entityType ):
					func = self.loadEntityUseFunc.get( entityType )
					for eConfig in spawnList:
						sec, matrix = eConfig
						sec[ "properties" ].writeInt( "planesID", planesID )
						e = func( entityType, sec, matrix )
						self.addPlanesSpawnEntity( planesID, e )
					
		self.onLoadPlanesEntitiesOver( planesID )
	
	def onLoadPlanesEntitiesOver( self, planesID ):
		"""
		virtual method.
		成功加载完一个位面的怪物
		"""
		pass

	def destoryPlanesEntity( self, planesID ):
 		"""
		销毁指定位面的entity
		"""
		for sp in self._spawnInfos:
			sp.cell.destroyEntity( { "planesID" : planesID } )
		
		for e in self._planesSpawnEntity.get( planesID, [] ):
			e.cell.destroy()
		
		self.cell.destoryPlanesEntity( planesID )
	
	def addPlanesSpawnEntity( self, planesID, newEntity ):
		if not self._planesSpawnEntity.has_key( planesID ):
			self._planesSpawnEntity[ planesID ] = []
		
		self._planesSpawnEntity[ planesID ].append( newEntity )
	
	def onCheckPlanesSpawnEntity( self, delay = 0.5 ):
		"""
		位面是否刷出怪物检查
		"""
		if not self.waiteLoaderSpawnPointPlanesTimerID:
			self.waiteLoaderSpawnPointPlanesTimerID = self.addTimer( delay, 0.1, SPAWN_PLANES_ENTITY_TIMERCB )
	
	def onTimerPlanesSpawnEntity( self, timerID ):
		"""
		延迟刷出检查
		"""
		if self.isSpawnPointLoaderOver:
			planesID = self.waiteLoaderSpawnPointPlanes.pop( 0 )
			self.spawnPlanesEntities( planesID )
			if len( self.waiteLoaderSpawnPointPlanes ) == 0:
				self.delTimer( timerID )
				self.waiteLoaderSpawnPointPlanesTimerID = 0

	def onTimer( self, id, userArg ):
		"""
		"""
		if userArg == SPAWN_PLANES_ENTITY_TIMERCB:
			self.onTimerPlanesSpawnEntity( id )

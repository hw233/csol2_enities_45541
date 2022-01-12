# -*- coding: gb18030 -*-

import BigWorld
from SpawnPointNormal import SpawnPointNormal

SPAWN_PLANES_ENTITY_TIMERCB = 1003

class Planes( object ):
	"""
	һ��λ������ռ����
	"""
	def __init__( self, spaceEntity, planesID, playerMailbox, params ):
		object.__init__( self )
		self.planesPlayers = []
		self.initPlanes( spaceEntity, planesID, playerMailbox, params )
	
	def initPlanes( self, spaceEntity, planesID, playerMailbox, params ):
		"""
		�����һ��planes������һ����ʵ��space entity
		"""
		self.planesPlayers.append( playerMailbox )
		self.planesID = planesID
		self.spawnEntities( spaceEntity )
	
	def spawnEntities( self, spaceEntity ):
		"""
		ˢ��λ��entity
		"""
		spaceEntity.spawnPlanesEntities( self.planesID )
	
	def teleportEntity( self, spaceEntity, position, direction, baseMailbox, pickData ):
		"""
		������ҽ�λ��
		"""
		spaceEntity.getScript().onPlanesTeleportEntity( spaceEntity, position, direction, baseMailbox, pickData, self.planesID )
	
	def getParams( self, spaceEntity ):
		"""
		ȡˢ�µ����
		"""
		newParams = {}
		newParams[ "planesID" ] = self.planesID
		return newParams

	def destroy( self, spaceEntity ):
		"""
		����λ��
		"""
		spaceEntity.destoryPlanesEntity( self.planesID )

class ImpPlanesSpace( object ):
	#λ���space�ӿ�
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
		����һ��entity��ָ����spaceλ����
		@type position : VECTOR3,
		@type direction : VECTOR3,
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX,
		@param params: һЩ���ڸ�entity����space�Ķ��������
		@type params : PY_DICT = None
		"""
		planes = self.getEnterPlanes( baseMailbox, pickData )
		planes.teleportEntity( self, position, direction, baseMailbox, pickData )
	
	def getEnterPlanes( self, playerMailbox, params ):
		"""
		��ȡ����planesID
		"""	
		planesID = params.get( "planesID", 0 )
		if self._planesItems.has_key( planesID ):
			return self._planesItems[ planesID ]
			
		return self.createPlanes( playerMailbox, params )
	
	def createPlanes( self, playerMailbox, params ):
		"""
		����һ���µ�λ��
		����ָ�Ĳ�����һ���µ�Space��ֻ��һ�������λ��ռ�
		"""
		newPlanesID  = self.getNewSpacePlanesID()
		self._planesItems[ newPlanesID ] = Planes( self, newPlanesID, playerMailbox, params )
		return self._planesItems[ newPlanesID ]
	
	def destroyPlanes( self, planesID ):
		"""
		����һ�������λ��
		"""
		if self._planesItems.has_key( planesID ):
			self._planesItems[ planesID ].destroy( self )
		
		self._planesItems.pop( planesID )
	
	def getNewSpacePlanesID( self ):
		"""
		��ȡ�µ�planesID
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
		������һ����ˢ��
		"""
		if isinstance( baseEntity, SpawnPointNormal ):
			self._spawnInfos.append( baseEntity )
	
	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		һ��������spawnPoint ������ϡ�
		"""
		self.onCheckPlanesSpawnEntity()
		
	def spawnPlanesEntities( self, planesID ):
		"""
		ˢ��λ��ռ����
		"""
		if self.isSpawnPointLoaderOver == False:
			self.waiteLoaderSpawnPointPlanes.append( planesID )
			return
			
		if planesID != 1: #λ��ID = 1���ʾ�ǵ�һ���������ң�ϵͳ��SpawnLoader�Ѿ�Ĭ��ˢ����һ������
			for sp in self._spawnInfos:
				sp.cell.createEntity( { "planesID" : planesID } )
			
			#����ֱ�Ӵ����Ĺ�����ˢһ��
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
		�ɹ�������һ��λ��Ĺ���
		"""
		pass

	def destoryPlanesEntity( self, planesID ):
 		"""
		����ָ��λ���entity
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
		λ���Ƿ�ˢ��������
		"""
		if not self.waiteLoaderSpawnPointPlanesTimerID:
			self.waiteLoaderSpawnPointPlanesTimerID = self.addTimer( delay, 0.1, SPAWN_PLANES_ENTITY_TIMERCB )
	
	def onTimerPlanesSpawnEntity( self, timerID ):
		"""
		�ӳ�ˢ�����
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

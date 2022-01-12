# -*- coding: gb18030 -*-

from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface

class SpaceCopyPig( SpaceCopy, SpaceCopyYeWaiInterface ):
	"""
	嘟嘟猪
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		self.spawnPointCopyDict = {}
		self.createFinish = 0
		self.currParams = None			# 临时变量：记录当前要出生的怪物参数

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		创建好了一个entity的通知
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	entity			: baseEntity实体
		"""
		if entityType == "SpawnPointCopyYeWai":
			self.addSpawnPointCopy( baseEntity, baseEntity.getName() )

	def checkNeedSpawn( self, sec ):
		# virtual method.
		# 判断是否需要创建此刷新点
		return SpaceCopyYeWaiInterface.checkNeedSpawn( self, sec ) and SpaceCopy.checkNeedSpawn( self, sec )

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		SpaceCopyYeWaiInterface.onSpawnPointLoadedOver( self, retCode )
		self.createFinish = 1	# spawnPoint加载完毕标记

	def addSpawnPointCopy( self, baseMailBox, entityName ):
		"""
		把出生点存入space.spawnPointCopyDict中
		"""
		if self.spawnPointCopyDict.has_key( entityName ):
			self.spawnPointCopyDict[entityName].append( baseMailBox )
		else:
			self.spawnPointCopyDict[entityName] = [baseMailBox]

	def spawnMonsters( self, params ):
		"""
		define method
		"""
		self.currParams = params					# 记录出生点创建怪物的参数

		if self.createFinish == 1:					# 如果出生点加载完毕
			self.createSpawnEntity()
		else:
			self.addTimer( 1.0, 0.0, 100001 )		# 等待出生点加载完毕

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopy.onTimer( self, id, userArg )
		if userArg == 100001:						# 等待出生点加载完毕后
			self.spawnMonsters( self.currParams )
	
	def createSpawnEntity( self ):
		"""
		开始刷怪
		"""
		if self.currParams.has_key( "bossIDs" ):
			bossIDs = self.currParams.pop( "bossIDs" )
			for id in bossIDs:
				for spawnMB in self.spawnPointCopyDict[ id ]:
					spawnMB.cell.createEntity( self.currParams )
		else:
			for className, spawnList in self.spawnPointCopyDict.iteritems():
				if className in self.bossIDs:
					continue
			
				for e in spawnList:
					e.cell.createEntity( self.currParams )
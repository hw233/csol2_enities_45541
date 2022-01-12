# -*- coding: gb18030 -*-

from bwdebug import *
from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface

class SpaceCopyDestinyTrans( SpaceCopy, SpaceCopyYeWaiInterface ):
	"""
	天命轮回副本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		self.createFinish = 0
		self.spawnMonstersList = {}
		self.currParams = None						# 临时变量：记录当前要出生的怪物参数

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

	def getDifficulty( self ):
		"""
		覆盖SpaceCopyYeWaiInterface的方法
		"""
		return 0

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		SpaceCopyYeWaiInterface.onSpawnPointLoadedOver( self, retCode )
		self.createFinish = 1	# spawnPoint加载完毕标记

	def addSpawnPointCopy( self, mailbox, entityName ):
		"""
		define method
		"""
		if self.spawnMonstersList.has_key( entityName ):
			self.spawnMonstersList[entityName].append( mailbox )
		else:
			self.spawnMonstersList[entityName] = [mailbox]

	def createSpawnEntities( self, params ):
		"""
		define method
		通知刷怪
		"""
		if not self.currParams:
			self.currParams = params				# 记录出生点创建怪物的参数

		if self.createFinish == 1:					# 如果出生点加载完毕
			self.createSpawnEntityCopy()
		else:
			self.addTimer( 1.0, 0.0, 100001 )		# 等待出生点加载完毕

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopy.onTimer( self, id, userArg )
		if userArg == 100001:						# 等待出生点加载完毕后
			self.createSpawnEntities( self.currParams )

	def onBeforeDestroyCellEntity( self ):
		"""
		删除cell entity 前，做一些事情
		"""
		self.spawnMonstersList = None

	def createSpawnEntityCopy( self ):
		"""
		开始刷怪
		"""
		for className, spawnList in self.spawnMonstersList.iteritems():
			for spawn in spawnList:
				if spawn.getSpawnType() == "SpawnPointCopyYeWai":
					spawn.cell.createEntity( self.currParams )
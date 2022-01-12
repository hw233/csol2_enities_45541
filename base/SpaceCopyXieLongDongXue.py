# -*- coding: gb18030 -*-
import BigWorld

from bwdebug import *
import Love3

from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface

from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objFactory = GameObjectFactory.instance()

class SpaceCopyXieLongDongXue( SpaceCopy, SpaceCopyYeWaiInterface, SpaceCopyRaidRecordInterface ):
	"""
	邪龙洞穴副本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.spawnMonstersList = {}

	def addSpawnPointCopy( self, mailbox, entityName ):
		"""
		define method
		"""
		if self.spawnMonstersList.has_key( entityName ):
			self.spawnMonstersList[entityName].append( mailbox )
		else:
			self.spawnMonstersList[entityName] = [mailbox]

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
		"""
		virtual method.
		判断是否需要创建此刷新点
		"""
		return SpaceCopyYeWaiInterface.checkNeedSpawn( self, sec ) and SpaceCopy.checkNeedSpawn( self, sec )

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		SpaceCopyYeWaiInterface.onSpawnPointLoadedOver( self, retCode )

	def spawnMonsters( self, params ):
		"""
		define method
		"""
		if params.has_key( "bossID" ):
			bossID = params.pop( "bossID" )
			for e in self.spawnMonstersList[ bossID ]:
				e.cell.createEntity( params )
		else:
			for className, spList in self.spawnMonstersList.iteritems():
				if className in self.bossIDs:
					continue

				for e in spList:
					try:
						e.cell.createEntity( params )
					except:
						pass

	def onEnter( self, baseMailbox, params ):
		"""
		define method.
		玩家进入了空间，需要根据副本boss的击杀情况给予玩家
		相应的提示，并让玩家选择是继续副本还是离开副本。
		@param baseMailbox: 玩家mailbox
		@type baseMailbox: mailbox
		@param params: 玩家onEnter时的一些额外参数
		@type params: py_dict
		"""
		SpaceCopy.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )

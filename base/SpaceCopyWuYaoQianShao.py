# -*- coding: gb18030 -*-
import random
import BigWorld

from SpaceCopyMaps import SpaceCopyMaps
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
from ObjectScripts.GameObjectFactory import GameObjectFactory
g_objFactory = GameObjectFactory.instance()
from bwdebug import *

import Love3

class SpaceCopyWuYaoQianShao( SpaceCopyMaps, SpaceCopyRaidRecordInterface ):
	"""
	巫妖前哨副本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopyMaps.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.__currSpawnID	= 0						# 临时变量	:	用于场景初始化时记录当前加载的spawnPoint索引
		self.cellData['teamLevel'] = self.params['teamLevel']
		self.cellData['teamMaxLevel'] = self.params['teamMaxLevel']
		self.spawnPointCopyDict = {}				# 记录副本中所有怪物出生点 such as:{ "className" : [ spawnPointCopy.base, ... ], ... }
		self.createFinish = 0						# 标记spawnPoint是否加载完毕
		#self.spawnEntityParamsDict = {}				# 记录出生点创建怪物时参数 such as:{ "className": params }
		#self.spawnEntityIDDict = {}					# 记录副本中某种类型entity的id，such as { entityName : [ id1,id2,... ],... }
		#self.spawnPointDoorDict = {}				# 记录副本中SpawnPointDoor出生点 such as:{ "className" : [ SpawnPointDoor.base, ... ], ... }
		self.currParams = None						# 临时变量：记录当前要出生的怪物参数

	def onGetCell(self):
		"""
		cell实体创建完成通知，回调callbackMailbox.onSpaceComplete，通知创建完成。
		"""
		# create spawn point into this space on other thread.
		if len( self.getScript().getSpaceSpawnFile( self ) ) == 0:
			WARNING_MSG( "space %s no spawn file specified." % self.className )
		else:
			Love3.g_spawnLoader.registerSpace( self )		# 加到队列中

		# space cell 创建完成通报
		self.domainMB.onSpaceGetCell( self.spaceNumber )

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		创建好了一个entity的通知
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	entity			: baseEntity实体
		"""
		if entityType == "SpawnPointCopyYeWai" or entityType == "SpawnPointCopyWuYaoQianShao":
			self.addSpawnPointCopy( baseEntity, baseEntity.getName() )

	def getDifficulty( self ):
		return self.getScript().difficulty

	def checkNeedSpawn( self, sec ):
		# virtual method.
		# 判断是否需要创建此刷新点
		return SpaceCopyMaps.checkNeedSpawn( self, sec )

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		SpaceCopyMaps.onSpawnPointLoadedOver( self, retCode )
		self.createFinish = 1	# spawnPoint加载完毕标记
		

	def addSpawnPointCopy( self, baseMailBox, entityName ):
		"""
		把出生点存入space.spawnPointCopyDict中
		"""
		if self.spawnPointCopyDict.has_key( entityName ):
			self.spawnPointCopyDict[entityName].append( baseMailBox )
		else:
			self.spawnPointCopyDict[entityName] = [baseMailBox]

	def createSpawnEntities( self, params ):
		"""
		通知spawnPoingCopy怪物出生
		"""
		if not self.createFinish:
			self.addTimer( 1.0, 0.0, 10001 )	# 等待出生点加载完毕
			if not self.currParams:
				self.currParams = params
			return

		if params.has_key( "bossID" ):
			for spawnPointCopy in self.spawnPointCopyDict[ params[ "bossID" ] ]:
				spawnPointCopy.cell.createEntity( params )	# spawnPointCopy刷出巫妖王
		else:
			for className, spList in self.spawnPointCopyDict.iteritems():
				if className in self.getScript().bossID:
					continue

				for e in spList:
					e.cell.createEntity( params )

		self.currParams = None

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopyMaps.onTimer( self, id, userArg )

		if userArg == 10001:	# 等待出生点加载完毕后，再次怪物出生
			self.createSpawnEntities( self.currParams )

	def onBeforeDestroyCellEntity( self ):
		"""
		删除cell entity 前，做一些事情
		"""
		self.spawnPointCopyDict = None

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
		SpaceCopyMaps.onEnter( self, baseMailbox, params )
		SpaceCopyRaidRecordInterface.onEnter( self, baseMailbox, params )

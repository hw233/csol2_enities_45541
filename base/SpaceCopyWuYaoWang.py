# -*- coding: gb18030 -*-
import random
import BigWorld

from bwdebug import *
from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
from ObjectScripts.GameObjectFactory import GameObjectFactory

import Love3

g_objFactory = GameObjectFactory.instance()

BAO_ZANG_WEI_BING				= [ "20732008", "20722043" ]		# 巫妖王宝藏卫兵的className
WU_YAO_WANG						= [ "20742059", "20742060", "20742061" ]		# 巫妖王的className

class SpaceCopyWuYaoWang( SpaceCopy, SpaceCopyYeWaiInterface, SpaceCopyRaidRecordInterface ):
	"""
	巫妖王宝藏副本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.__currSpawnID	= 0						# 临时变量	:	用于场景初始化时记录当前加载的spawnPoint索引
		self.spawnPointCopyDict = {}				# 记录副本中所有怪物出生点 such as:{ "className" : [ spawnPointCopy.base, ... ], ... }
		self.spawnEntityParamsDict = {}				# 记录出生点创建怪物时参数 such as:{ "className": params }

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
		self.addTimer( 1.0, 0.0, 100001 )
		for cid in BAO_ZANG_WEI_BING:
			self.spawnEntityParamsDict[ cid ] = { "level": self.params[ "teamLevel" ] }

		for cid in WU_YAO_WANG:
			self.spawnEntityParamsDict[ cid ] = { "level": self.params[ "teamLevel" ] }

	def addSpawnPointCopy( self, baseMailBox, entityName ):
		"""
		把出生点存入space.spawnPointCopyDict中
		"""
		if self.spawnPointCopyDict.has_key( entityName ):
			self.spawnPointCopyDict[entityName].append( baseMailBox )
		else:
			self.spawnPointCopyDict[entityName] = [baseMailBox]

	def createSpawnEntities( self ):
		"""
		刷新点加载完毕，开始刷出怪物
		"""
		for entityName in self.spawnPointCopyDict.keys():
			self.createSpawnEntityCopy( entityName, self.spawnEntityParamsDict[entityName] )

	def createSpawnEntityCopy( self, entityName, params ):
		"""
		通知spawnPoingCopy怪物出生
		"""
		for spawnPointCopy in self.spawnPointCopyDict[entityName]:
			spawnPointCopy.cell.createEntity( params )	# spawnPointCopy刷出怪物

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopy.onTimer( self, id, userArg )

		if userArg == 100001:
			self.createSpawnEntities()

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
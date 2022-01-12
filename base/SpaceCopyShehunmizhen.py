# -*- coding: gb18030 -*-
import Love3
from bwdebug import *
from SpaceCopyMaps import SpaceCopyMaps
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface

class SpaceCopyShehunmizhen( SpaceCopyMaps, SpaceCopyRaidRecordInterface ):
	"""
	摄魂迷阵
	"""
	def __init__(self):
		SpaceCopyMaps.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.__currSpawnID	= 0						# 临时变量	:	用于场景初始化时记录当前加载的spawnPoint索引
		self.cellData['teamLevel'] = self.params['teamLevel']
		self.cellData['teamMaxLevel'] = self.params['teamMaxLevel']
		self.spawnList = {}
		self.createFinish = False						# 标记spawnPoint是否加载完毕
		self.currParams = None							# 临时变量：记录当前要出生的怪物参数

	def onGetCell(self):
		"""
		cell实体创建完成通知，回调callbackMailbox.onSpaceComplete，通知创建完成。
		"""
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
		if entityType == "SpawnPointCopyYeWai":
			self.addSpawnPointCopy( baseEntity, baseEntity.getName() )

	def getDifficulty( self ):
		return self.getScript().difficulty

	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		SpaceCopyMaps.onSpawnPointLoadedOver( self, retCode )
		self.createFinish = True	# spawnPoint加载完毕标记

	def addSpawnPointCopy( self, baseMailBox, entityName ):
		"""
		把出生点存入space.spawnPointCopyDict中
		"""
		if self.spawnList.has_key( entityName ):
			self.spawnList[entityName].append( baseMailBox )
		else:
			self.spawnList[entityName] = [baseMailBox]

	def spawnMonsters( self, params ):
		"""
		define method
		"""
		if not self.createFinish:
			self.addTimer( 1.0, 0.0, 10001 )	# 等待出生点加载完毕
			if not self.currParams:
				self.currParams = params
			return
		
		for className, spList in self.spawnList.iteritems():
			for e in spList:
				e.cell.createEntity( params )

	def onTimer( self, id, userArg ):
		"""
		"""
		SpaceCopyMaps.onTimer( self, id, userArg )

		if userArg == 10001:	# 等待出生点加载完毕后，再次怪物出生
			self.spawnMonsters( self.currParams )

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

	def onBeforeDestroyCellEntity( self ):
		"""
		删除cell entity 前，做一些事情
		"""
		self.spawnList = None
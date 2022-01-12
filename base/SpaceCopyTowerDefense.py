# -*- coding: gb18030 -*-
from SpaceCopy import SpaceCopy
from interface.SpaceCopyYeWaiInterface import SpaceCopyYeWaiInterface
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
from bwdebug import *
import BigWorld
import Love3

class SpaceCopyTowerDefense( SpaceCopy, SpaceCopyYeWaiInterface, SpaceCopyRaidRecordInterface ):
	"""
	塔防副本
	"""
	def __init__( self ):
		"""
		初始化
		"""
		SpaceCopy.__init__( self )
		SpaceCopyYeWaiInterface.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )

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
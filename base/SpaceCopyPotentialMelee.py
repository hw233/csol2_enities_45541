# -*- coding: gb18030 -*-
#

from SpaceCopy import SpaceCopy
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
import Love3
import BigWorld
from bwdebug import *

MONSTER_CALC_TYPE = [ "SpawnPointPotentialMelee", ]
FLAG_CLASS_NAME = [ "20254004" ]

TIMER_ARG_SPAWN_FLAG = 10000

class SpaceCopyPotentialMelee( SpaceCopy, SpaceCopyRaidRecordInterface ):
	"""
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		BigWorld.globalData["PotentialMeleeMgr"].onRegisterSpace( self )
		self.spawnPoints = []
		self.spawnFlag = None #旗子刷新点
		self.spawnFlagParams = {}

	def closeSpace( self, deleteFromDB = True ):
		"""
		define method.
		destroy space的唯一入口，所有的space删除都应该走此接口；
		space生命周期结束，删除space
		"""
		BigWorld.globalData["PotentialMeleeMgr"].onUnRegisterSpace( self.id )
		SpaceCopy.closeSpace( self, deleteFromDB )

	def onLoseCell( self ):
		"""
		CELL死亡
		"""
		BigWorld.globalData["PotentialMeleeMgr"].onUnRegisterSpace( self.id )
		SpaceCopy.onLoseCell( self )
	
	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		创建好了一个entity的通知
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	entity			: baseEntity实体
		"""
		if baseEntity.getName() in FLAG_CLASS_NAME:
			self.spawnFlag = baseEntity
			
		if entityType in MONSTER_CALC_TYPE:
			self.spawnPoints.append( baseEntity )

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
	
	def spawnFlagEntity( self, params ):
		"""
		define method.
		刷出圣魂旗
		"""
		if self.spawnFlag and self.spawnFlagParams:
			self.spawnFlag.cell.createEntity( params )
		else:
			self.spawnFlagParams = params
			self.addTimer( 2, 0, TIMER_ARG_SPAWN_FLAG )
		
	def spawnMonster( self, batch, params ):
		"""
		define method.
		刷出怪物
		"""
		params[ "batch" ] = batch
		for sp in self.spawnPoints:
			sp.cell.createEntity( params )
	
	def onTimer( self, id, userArg ):
		if TIMER_ARG_SPAWN_FLAG == userArg:
			self.spawnFlagEntity( self.spawnFlagParams )
			return
		
		SpaceCopy.onTimer( self, id, userArg )
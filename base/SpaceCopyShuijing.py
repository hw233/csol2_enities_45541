# -*- coding: gb18030 -*-
#


from SpaceCopy import SpaceCopy
from interface.SpaceCopyRaidRecordInterface import SpaceCopyRaidRecordInterface
from bwdebug import *
import BigWorld
import Love3

REGISTER_ID = 1
CLOSE_ID = 2

TIMER_REGISTER = 10
TIMER_CLOSE = 30

class SpaceCopyShuijing( SpaceCopy, SpaceCopyRaidRecordInterface ):
	"""
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		SpaceCopyRaidRecordInterface.__init__( self )
		self.cellData['shuijing_level'] = self.params['shuijing_level']
		self.cellData['shuijing_maxlevel'] = self.params['shuijing_maxlevel']
		self.__currSpawnID	= 0
		self.monsterTotalCount = 0
		self.addTimer( TIMER_REGISTER, 0, REGISTER_ID )


	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
		self.cell.calculateMonsterCount()

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

	def onTimer( self, id, userArg ):
		if userArg == REGISTER_ID:
			self.registerToMgr()
		elif userArg == CLOSE_ID:
			self.closeSpace()
		
		SpaceCopy.onTimer( self, id, userArg )
			
	def registerToMgr( self ):
		BigWorld.globalData[ "ShuijingManager" ].registerShuijingMB( self.params[ "shuijingKey" ], self )
		
	def mgrDestorySelf( self ):
		self.addTimer( TIMER_CLOSE, 0, CLOSE_ID )
	
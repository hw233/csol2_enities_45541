# -*- coding: gb18030 -*-

"""
副本中怪物出生点类型，服务器启动后不需要直接创建怪物，怪物死亡后不需要复活，间隔intervalTime时间后，出生一个怪物，直到数量为：spawnNum
"""

import BigWorld
from bwdebug import *
import csdefine
import csconst
import random
from SpawnPoint import SpawnPoint

class SpawnPointCopyInterval( SpawnPoint ):
	"""
	副本中怪物出生点类型
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )
		
	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		pass	# 怪物死亡后不需要复活

	def onBaseGotCell( self, selfEntity ):
		"""
		由base回调回来，通知spawn point，base已经获得了cell的通知
		"""
		# 当base获得了onGetCell()回调后再开始怪物的增产生，以求能解决怪物出生时出生点不正确的问题
		# 当前该问题很可能是底层的bug
		pass	# 副本怪物出生点，不需要创建出生点的怪物

	def getEntityArgs( self, selfEntiy, params = {} ):
		args = SpawnPoint.getEntityArgs( self, selfEntiy, params )
		
		entityNameList = []
		entityOddsList = []
		for e in self.entityName.split( ";" ):
			entityNameList.append( str( e.split( ":" )[0] ) )
			entityOddsList.append( int( e.split( ":" )[1] ) )
			
		args[ "className" ] = getRandomElement( entityNameList, entityOddsList )
		return args
	
	def createEntity( self,selfEntity, params = {} ):
		"""
		初始化怪物
		"""
		SpawnPoint.createEntity( self, selfEntity, params )
		# 出生点出生一个怪物，self.spawnNum减1
		spawnNum = selfEntity.queryTemp( "spawnNum", 0 )
		spawnNum -= 1
		selfEntity.setTemp( "spawnNum", spawnNum )
		if spawnNum > 0:
			intervalTime = selfEntity.queryTemp( "intervalTime", 0 )
			assert intervalTime > 0
			self.addTimer( intervalTime, 0, Const.SPAWN_ON_SERVER_START )	# 间隔intervalTime后，出生一个怪物
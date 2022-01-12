# -*- coding: gb18030 -*-
from bwdebug import *
import csdefine
from SpawnPoint import SpawnPoint
import random

class RandomSpawnPoint( SpawnPoint ):
	"""
	随机点刷新怪物，实现随机的方式取得策划已经配置好的多个位置中的一个刷出怪物。只能用于普通地图。
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取要创建的entity参数
		"""
		args = SpawnPoint.getEntityArgs( self, selfEntity, params )
		positions = selfEntity.getEntityData( "positions" )
		if positions:
			args[ "position" ] = positions[ random.randint( 0, len( positions ) -1 ) ]			# 随机刷新点
		return args
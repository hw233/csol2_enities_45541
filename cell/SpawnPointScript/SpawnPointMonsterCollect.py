# -*- coding: gb18030 -*-
# 有特殊配置怪物的刷新点 by 姜毅 10:43 2011-1-14

from bwdebug import *
from SpawnPointSpecial import SpawnPointSpecial

class SpawnPointMonsterCollect( SpawnPointSpecial ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointSpecial.initEntity( self, selfEntity  )
	
	def createEntity( self, selfEntity, params = {} ):
		"""
		define method
		指定怪物类型、掉落物品刷怪
		"""
		self.rediviousEntity( selfEntity, params )
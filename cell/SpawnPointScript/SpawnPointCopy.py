# -*- coding: gb18030 -*-

"""
副本中怪物出生点类型，服务器启动后不需要直接创建怪物，怪物死亡后不需要复活
"""

import BigWorld
from bwdebug import *
import csdefine
import csconst
import random
from SpawnPoint import SpawnPoint

class SpawnPointCopy( SpawnPoint ):
	"""
	副本中怪物出生点类型
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )

	def onBaseGotCell( self, selfEntity ):
		"""
		由base回调回来，通知spawn point，base已经获得了cell的通知
		"""
		# 当base获得了onGetCell()回调后再开始怪物的增产生，以求能解决怪物出生时出生点不正确的问题
		# 当前该问题很可能是底层的bug
		pass	# 副本怪物出生点，不需要创建出生点的怪物
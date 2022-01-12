# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpawnPoint import SpawnPoint

class SpawnPointDanceSeat( SpawnPoint ):
	# 舞厅中20到39个坐位模型刷新点
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
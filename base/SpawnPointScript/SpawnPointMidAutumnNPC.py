# -*- coding: gb18030 -*-
"""
副本中怪物出生点
"""
import BigWorld
from bwdebug import *

from SpawnPointCopy import SpawnPointCopy

class SpawnPointMidAutumnNPC( SpawnPointCopy ):
	"""
	副本中怪物出生点类型
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
		

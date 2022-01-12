# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
import csdefine
import csconst
import random
from SpawnPointCopy import SpawnPointCopy

class SpawnPointBelongTeam( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
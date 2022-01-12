# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
import csdefine
import csconst
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory
import random

class SpawnPointTrap( SpawnPoint ):
	"""
	根据与策划的沟通,怪物死亡时一次性复活,即第一个怪物死亡后开始计时,计时结束时后面有怪物死亡时一次性复活.
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity )
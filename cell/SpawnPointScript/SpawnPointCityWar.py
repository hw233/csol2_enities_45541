# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
import csdefine
import csconst
import Const
import random
from SpawnPoint import SpawnPoint

class SpawnPointCityWar( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		selfEntity.currentRedivious = 0
		selfEntity.setTemp( "isWarOver", False )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		if selfEntity.getCurrentSpaceBase() == None:
			return
		selfEntity.currentRedivious += 1
		
	def onCityWarOver( self ):
		# define method
		# ��ս�������Ѵ�����entity����
		selfEntity.setTemp( "isWarOver", True )
	
	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if userData == Const.SPAWN_ON_SERVER_START:
			if selfEntity.queryTemp( "isWarOver", False ):
				return
				
			self.createEntity( selfEntity )
# -*- coding: gb18030 -*-
import copy
import random
from SpaceCopy import SpaceCopy

TIMER_USER_ARG_SPAWN_TRAP = 1

class SpaceCopyYeZhanFengQi( SpaceCopy ):
	# 夜战凤栖镇
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.cellData[ "spaceLevel" ] = self.params[ "spaceLevel" ]
		self.cellData[ "actStartTime" ] = self.params[ "actStartTime" ]
		self.spawnCopyList =  []
		self.spawnCopyTrap = []
	
	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		创建好了一个entity的通知
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	entity			: baseEntity实体
		"""
		if entityType == "SpawnPointCopy":
			self.spawnCopyList.append( baseEntity )
		
		if entityType == "SpawnPointSkillTrap":
			self.spawnCopyTrap.append( baseEntity )
	
	def trapRevive( self ):
		spawnList = []
		allTempSpawn = copy.deepcopy( self.spawnCopyTrap )
		for i in xrange( self.getScript().trapReviveNum ):
			if len(allTempSpawn):
				sp = random.choice( allTempSpawn )
				sp.cell.createEntityNormal()
				allTempSpawn.remove( sp )
		
		self.addTimer( self.getScript().trapReviveTime, 0, TIMER_USER_ARG_SPAWN_TRAP )

	def createSpawnEntities( self, params ):
		"""
		define method
		通知spawnPoingCopy怪物出生
		"""
		for sp in self.spawnCopyList:
			sp.cell.createEntity( params )
		
		self.trapRevive()
	
	def onTimer( self, tid, arg ):
		# addTimer control
		if arg  == TIMER_USER_ARG_SPAWN_TRAP:
			self.trapRevive()
		else:
			SpaceCopy.onTimer( self, tid, arg )
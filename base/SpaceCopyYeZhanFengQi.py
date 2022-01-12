# -*- coding: gb18030 -*-
import copy
import random
from SpaceCopy import SpaceCopy

TIMER_USER_ARG_SPAWN_TRAP = 1

class SpaceCopyYeZhanFengQi( SpaceCopy ):
	# ҹս������
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.cellData[ "spaceLevel" ] = self.params[ "spaceLevel" ]
		self.cellData[ "actStartTime" ] = self.params[ "actStartTime" ]
		self.spawnCopyList =  []
		self.spawnCopyTrap = []
	
	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		��������һ��entity��֪ͨ
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	entity			: baseEntityʵ��
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
		֪ͨspawnPoingCopy�������
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
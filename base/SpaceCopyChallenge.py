# -*- coding: gb18030 -*-

import BigWorld
from SpaceCopy import SpaceCopy
from bwdebug import *
import Const

CHALLENGE_CHECK_TYPE = [ "SpawnPointChallenge", "SpawnPointChallengeTrap", "NPCSpawnPoint" ]
TIMER_MGR_CLOSE_SELF = 30
TIMER_REGISTER_SELF = 10

TIMER_AGR_REGHIST	= 1
TIMER_AGR_CLOSE		= 2

class SpaceCopyChallenge( SpaceCopy ):
	"""
	挑战副本
	"""
	def __init__(self):
		SpaceCopy.__init__( self )
		self.__currSpawnID	= 0	
		self.spawnTrapPointMonsters = {}
		self.timerMgrDestroySelfID = 0
		self.addTimer( TIMER_REGISTER_SELF, 0, TIMER_AGR_REGHIST )
	
	def registerToMgr( self ):
		BigWorld.globalData[ "SpaceChallengeMgr" ].registerSpaceIns( self.params[ "spaceChallengeKey" ], self )
	
	def mgrDestroySelf( self ):
		# define method.
		self.addTimer( TIMER_MGR_CLOSE_SELF, 0, TIMER_AGR_CLOSE )
	
	def registerPlayer( self, baseMailbox ):
		SpaceCopy.registerPlayer( self, baseMailbox )
	
	def onTimer( self, id, userArg ):
		if userArg == TIMER_AGR_CLOSE:
			self.closeSpace()
		
		if userArg == TIMER_AGR_REGHIST:
			self.registerToMgr()
			
		SpaceCopy.onTimer( self, id, userArg )
		
	def registerTrapSpawnPoint( self, spawnEntity, trapID ):
		# 注册trap配置的怪物
		if trapID not in self.spawnTrapPointMonsters:
			self.spawnTrapPointMonsters[ trapID ]  = []
			
		self.spawnTrapPointMonsters[ trapID ].append( spawnEntity )
	
	def startTrapSpawnEntity( self, trapID):
		# 刷出trap配置的怪物
		if trapID in self.spawnTrapPointMonsters:
			for spm in self.spawnTrapPointMonsters[ trapID ]:
				spm.cell.startSpawnEntity()
	
	def checkNeedSpawn( self, sec ):
		if sec.readString( "type" ) in CHALLENGE_CHECK_TYPE:
			challengeTMembers = sec.readInt( "properties/challengeTMembers" )
			if self.params[ "spaceChallengeEnterNums" ] < challengeTMembers:
				return False
		
		return SpaceCopy.checkNeedSpawn( self, sec )

	def onBeforeDestroyCellEntity( self ):
		"""
		删除cell entity 前，做一些事情
		"""
		self.spawnTrapPointMonsters = None
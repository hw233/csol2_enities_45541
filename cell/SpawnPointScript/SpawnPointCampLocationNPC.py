# -*- coding: gb18030 -*-

# CSOL-1774 add by cwl

import BigWorld
import Const
import csconst
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory
from bwdebug import *

TIMER_ARG_SPAWN_TIMER = 10001

class SpawnPointCampLocationNPC( SpawnPoint ):
	"""
	��Ӫ�ݵ�NPCˢ�µ�: �ݵ㱻ռ����Ҫת���ɶԷ���Ӫ��NPC
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		if selfEntity.isCount:
			BigWorld.globalData["CampMgr"].addLocationSpawnPoint( selfEntity.camp, selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), selfEntity.entityName, selfEntity.base, selfEntity.getCurrentSpaceBase(), selfEntity.rediviousTotal )
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		��ȡˢ��entity�Ĳ���
		"""	
		args = SpawnPoint.getEntityArgs( self, selfEntity, params )
		
		levelRange = [ int( i ) for i in selfEntity.level.split(";") ]
		if len( levelRange ) >= 2:
			args["level"] = random.randint( levelRange[0], levelRange[1] )
		elif len( levelRange ) == 1:
			args["level"] = levelRange[0]
		
		args[ "camp" ] = selfEntity.camp
		args[ "className" ] = self.getSpawnClassName( selfEntity )
		return args
		
	def createEntity( self, selfEntity, params = {} ):
		"""
		ˢNPC
		"""
		if not self.checkActivity( selfEntity ):
			return
		
		entityName = self.getSpawnClassName( selfEntity )
		if not entityName:
			return
			
		SpawnPoint.createEntity( self, selfEntity, params )
		if selfEntity.spawnTime  > 0:
			selfEntity.spawnTimer = selfEntity.addTimer( 1.0, selfEntity.spawnTime , TIMER_ARG_SPAWN_TIMER )				# �����ú���ˢ�֡� ע��Ҫô�����Զ�����ʱ�䣬Ҫô���ü��ˢ��ʱ��
	
	def rediviousEntity( self, selfEntity ):
		oldSpawnLen = len( selfEntity.spawnList )
		self.createEntity( selfEntity )
		newSpawnLen = len( selfEntity.spawnList )
		newSpawnNum = newSpawnLen - oldSpawnLen
		if not self.isOccued and self.isCount and newSpawnNum:
			BigWorld.globalData["CampMgr"].onLocationMonsterRedivious( self.camp, selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), selfEntity.entityName, newSpawnNum )
	
	def getSpawnClassName( self, selfEntity ):
		if selfEntity.isOccued:
			return self.enemyCampClassName
		else:
			return selfEntity.entityName
			
	def onLocationOccuped( self, selfEntity ):
		"""
		define method
		�ݵ㱻��ռ
		"""
		self.isOccued = True
		self.destroyMonster()
		self.rediviousMonster( selfEntity )
		self.recoverTimer = selfEntity.addTimer( 1 * 60 * 60, 0, 0 )			# �ݵ�ָ�timer
	
	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		if not self.isOccued and self.isCount:
			BigWorld.globalData["CampMgr"].onLocationMonsterDie( self.camp, selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), selfEntity.entityName )
		
		if selfEntity.rediviousTime < 0:
			return
		
		if selfEntity.rediviousTime > 0 or selfEntity.spawnTime  > 0:
			selfEntity.currentRedivious += 1
		
		if not selfEntity.rediviousTimer:
			selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )
	
	def recoverLocation( self, selfEntity ):
		"""
		define method
		�ݵ�ָ�
		"""
		if self.recoverTimer > 0:
			selfEntity.cancel( self.recoverTimer )
			self.recoverTimer = 0
			
		self.isOccued = False
		self.destroyMonster()
		self.createEntity( selfEntity )
	
	def checkActivity( self, selfEntity ):
		"""
		�����Ӫ���ͼ�ͻ����
		"""
		if selfEntity.activityTypes == "":
			return True
			
		if not BigWorld.globalData.has_key( "CampActivityCondition" ):		# ��������( [ spaceNames ], type )
			return False
		
		temp = BigWorld.globalData["CampActivityCondition"]
		if selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) not in temp[0]:
			return False
		
		activityTypeList = [ int( i ) for i in selfEntity.activityTypes.split( "," ) ]			# ��ˢ�µ���ܻᱻ�����õ�
		if temp[1] not in activityTypeList:
			return False
			
		return True

	def destroyMonster( self ):
		"""
		����NPC
		"""
		for eid in selfEntity.spawnList:
			monster = BigWorld.entities.get( eid, None )
			if monster:
				if hasattr( monster, "resetEnemyList" ):
					monster.resetEnemyList()
				monster.destroy()
				
	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if controllerID == selfEntity.recoverTimer:
			self.recoverLocation()
			
		if userData == Const.SPAWN_ON_MONSTER_DIED:
			selfEntity.rediviousTimer = 0
			self.rediviousEntity( selfEntity )
			
		elif userData == Const.SPAWN_ON_SERVER_START:
			self.createEntity( selfEntity )
			
		elif userData == TIMER_ARG_SPAWN_TIMER:
			if selfEntity.currentRedivious >= selfEntity.rediviousTotal:			# ��ȫ���˲�ˢ��һ��
				selfEntity.currentRedivious = 0
				self.rediviousMonster( selfEntity )
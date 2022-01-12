# -*- coding: gb18030 -*-

# CSOL-1774,add by cwl

import BigWorld
import Const
import csconst
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory

SPAWN_TIMER = 111

class SpawnPointCampMonster( SpawnPoint ):
	"""
	��Ӫ�ˢ�µ�
	
	1���ɻ����������ˢ�ֺ�ͳһ���ٹ��ע��ֻ�����ڹ�����ˢ�µ㸽����������������������޷����١�
	2��ˢ��Ƶ�ʼ������������ʱ��⸴�
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )
		BigWorld.globalData["CampMgr"].addActivityMonsterSpawnPoint( selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), selfEntity.entityName, selfEntity.base, selfEntity.camp )
		
	def createEntity( self, selfEntity, dict ):
		"""
		define method
		��ʼˢ��
		"""
		if not self.checkActivity( selfEntity ):			# ���������Ӫ�������ָ���ĵ�ͼ�ͻ���ͣ���ˢ�µ㲻ˢ��
			return
		selfEntity.setTemp( "activityStart", True )
		self.spawnAllMonster( selfEntity )
		
		if selfEntity.spawnTime  >= 0:
			selfEntity.spawnTimer = selfEntity.addTimer( 1, selfEntity.spawnTime , SPAWN_TIMER )				# �����ú���ˢ�֡� ע��Ҫô�����Զ�����ʱ�䣬Ҫô���ü��ˢ��ʱ��
		
	def checkActivity( self, selfEntity ):
		"""
		�����Ӫ���ͼ�ͻ����
		"""
		if not BigWorld.globalData.has_key( "CampActivityCondition" ):		# ��������( [ spaceNames ], type )
			return False
		
		temp = BigWorld.globalData["CampActivityCondition"]
		if selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) not in temp[0]:
			return False
		
		activityTypeList = [ int( i ) for i in selfEntity.activityTypes.split( "," ) ]			# ��ˢ�µ���ܻᱻ�����õ�
		if temp[1] not in activityTypeList:
			return False
			
		return True
		
	def spawnAllMonster( self, selfEntity ):
		"""
		ˢ���������Ĺ�
		@num : ˢ������
		"""
		position = tuple( selfEntity.position )

		d = { "spawnPos" : position, "spawnMB" : selfEntity.base, "randomWalkRange" : selfEntity.randomWalkRange }
		if selfEntity.level > 1:
			d["level"] = selfEntity.level
		if len( selfEntity.patrolPathNode ):
			d["patrolPathNode"] = selfEntity.patrolPathNode
			d["patrolList"] = selfEntity.patrolList
		
		idList = selfEntity.queryTemp( 'monsterIDs', [] )
		for i in xrange( selfEntity.rediviousTotal ):
			entity = g_objFactory.getObject( selfEntity.entityName ).createEntity( selfEntity.spaceID, position, selfEntity.direction, d )
			idList.append( entity.id )
		selfEntity.setTemp( 'monsterIDs', idList )
		
	def spawnDiedMonster( self, selfEntity ):
		"""
		ˢ�����������Ĺ�
		"""
		position = tuple( selfEntity.position )
		d = { "spawnPos" : position, "spawnMB" : selfEntity.base, "randomWalkRange" : selfEntity.randomWalkRange }
		if selfEntity.level > 1:
			d["level"] = selfEntity.level
		if len( selfEntity.patrolPathNode ):
			d["patrolPathNode"] = selfEntity.patrolPathNode
			d["patrolList"] = selfEntity.patrolList
		
		idList = selfEntity.queryTemp( 'monsterIDs', [] )
		for i in xrange( selfEntity.currentRedivious ):
			entity = g_objFactory.getObject( selfEntity.entityName ).createEntity( selfEntity.spaceID, position, selfEntity.direction, d )
			idList.append( entity.id )
		selfEntity.setTemp( 'monsterIDs', idList )
		
	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		if not selfEntity.queryTemp( "activityStart", False ):
			return
			
		if selfEntity.rediviousTime > 0 or selfEntity.spawnTime  > 0:
			selfEntity.currentRedivious += 1
		
		if selfEntity.rediviousTime > 0 and not selfEntity.rediviousTimer:
			selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )
			
	def onActivityEnd( self, selfEntity ):
		"""
		define method
		"""
		if not selfEntity.queryTemp( "activityStart", False ):		# û����ˢ��
			return
		selfEntity.setTemp( "activityStart", False )
		idList = selfEntity.queryTemp( 'monsterIDs', [] )
		for id in idList:
			monster = BigWorld.entities.get( id, None )
			if monster:
				monster.resetEnemyList()
				monster.destroy()
		selfEntity.removeTemp( 'monsterIDs' )
		
		selfEntity.cancel( selfEntity.spawnTimer )
		selfEntity.spawnTimer = 0
		selfEntity.cancel( selfEntity.rediviousTimer )
		selfEntity.rediviousTimer = 0
		selfEntity.currentRedivious = 0
		
	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if userData == SPAWN_TIMER:
			if selfEntity.currentRedivious < selfEntity.rediviousTotal:			# ��ȫ���˲�ˢ��һ��
				return
			self.spawnAllMonster( selfEntity )
			
		elif userData == Const.SPAWN_ON_MONSTER_DIED:
			selfEntity.rediviousTimer = 0
			self.spawnDiedMonster( selfEntity )
		
		selfEntity.currentRedivious = 0
			
	def onBaseGotCell( self, selfEntity ):
		"""
		"""
		pass


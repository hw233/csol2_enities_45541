# -*- coding: gb18030 -*-
#
# ǧ�궾�� 2009-05-25 SongPeifang
#

import BigWorld
import csdefine
import random
import math
import ECBExtend
from Monster import Monster
from ObjectScripts.GameObjectFactory import g_objFactory
from bwdebug import *
from Domain_Fight import g_fightMgr
import csarithmetic
import Math


BLEW_MONSTER_ID = "20321067"	# �Ա�����ID
CALL_MONSTER_DIS = 10.0			# �Ա������ٻ���Χ
CALL_BLEW_MONSTER_TIMER = 50.0	# �ٻ��Ա�����ʱ����

class ToxinFrog( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		if self.getScript().bornNPC:
			self.changeToNPC()
		self.littleMonsterIDs = [] #���С�ֵ��б�
		self.randomWalkRange = 5
		
	def callMonsters( self, subMonsterClassName, subMonsterCount ):
		"""
		define method
		Pram subMonsterClassName : �ٻ���С�ֵ�className
		Pram subMonsterCount : �ٻ���С������
		"""
		# �ٻ�10��С��
		self.setTemp( 'monstersCount', subMonsterCount )
		self.setTemp( 'subMonsterClassName', subMonsterClassName )
		self.addTimer( 0.5, 0, ECBExtend.CALL_MONSTER_FOR_108_CBID )

	def callMonster( self, timerID, cbID ):
		"""
		�ٻ�С��
		"""
		monsterCount = self.queryTemp( 'monstersCount', 0 )
		monsterClassName = self.queryTemp( 'subMonsterClassName', "" )
		monsterLevel = self.queryTemp( 'call_monster_level', 0 )
		if monsterCount <= 0 or monsterClassName == "":
			return
		self.setTemp( 'monstersCount', monsterCount-1 )
		# �������ˢ���ڶԻ������ߵ�3-5�װ뾶����
		x = random.randrange( 0, 5.0, 1, float ) 			# ���ѡȡx��ֵ
		r = random.randrange( max( 3, x ), 5, 1, float )	# ���ѡȡ�뾶ֵ
		z = math.sqrt( math.pow( r, 2 ) - math.pow( x, 2 ) )# ���ݰ뾶��x��õ�z��ֵ
		y = self.position.y
		collide = BigWorld.collide( self.spaceID, ( x, y+0.5, z ), ( x, y, z ) )
		if collide != None:
			# ������Ʒ��ʱ��Ե��������ײ��������Ʒ�������
			 y = collide[0].y
		position = ( self.position.x + x, y+0.5 , self.position.z + z )
		try:
			entity = g_objFactory.getObject( monsterClassName ).createEntity( self.spaceID, position, self.direction, {"spawnPos":position, "randomWalkRange":5 } )
			
			g_fightMgr.buildGroupEnemyRelationByIDs( entity, self.enemyList.keys() )
			self.littleMonsterIDs.append( entity.id ) #���ٻ�������С�ֱ������б���
			entity.setTemp("masterID", self.id )
			if monsterLevel != 0:
				entity.setLevel( monsterLevel )
			bootyOwner = self.queryTemp( "ToxinFrog_bootyOwner", () )
			if bootyOwner:	# �����ս��Ʒӵ����
				entity.setTemp( "ToxinFrog_bootyOwner", bootyOwner )
				if bootyOwner[ 1 ]:
					entity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_TEAM_ANTAGONIZE, bootyOwner[ 1 ] )
				else:
					entity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, bootyOwner[ 0 ] )
		except:
			ERROR_MSG( "No such monster:%s"%monsterClassName )

		self.addTimer( 0.3, 0, ECBExtend.CALL_MONSTER_FOR_108_CBID )

	def onCallBlewMonsterTimer( self, timerID, cbID ):
		"""
		�ٻ��Ա�С��
		"""
		if self.isDestroyed or self.getState() == csdefine.ENTITY_STATE_FREE or self.getState() == csdefine.ENTITY_STATE_DEAD:
			return
		monsterLevel = self.queryTemp( 'call_monster_level', 0 )
		posList = calculatePos( self.spaceID, self.yaw, CALL_MONSTER_DIS, self.position )
		position = random.choice( posList )
		try:
			entity = g_objFactory.getObject( BLEW_MONSTER_ID ).createEntity( self.spaceID, position, self.direction, {"spawnPos":position, "randomWalkRange":5 } )
			g_fightMgr.buildGroupEnemyRelationByIDs( entity, self.enemyList.keys() )
			self.littleMonsterIDs.append( entity.id )
			if monsterLevel != 0:
				entity.setLevel( monsterLevel )
			bootyOwner = self.queryTemp( "ToxinFrog_bootyOwner", () )
			if bootyOwner:	# �����ս��Ʒӵ����
				entity.setTemp( "ToxinFrog_bootyOwner", bootyOwner )
				if bootyOwner[ 1 ]:
					entity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_TEAM_ANTAGONIZE, bootyOwner[ 1 ] )
				else:
					entity.addCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, bootyOwner[ 0 ] )
		except:
			ERROR_MSG( "No such monster:%s" % BLEW_MONSTER_ID )

	def afterDie( self, killerID ):
		"""
		virtual method.

		������ص���ִ��һЩ�����ڹ�����������������顣
		"""
		Monster.afterDie( self, killerID )
		if self.queryTemp( "die_destroy_monsters", False ):
			self.destroyMonsters()
		return

	def onStateChanged( self, old, new ):
		"""
		״̬�л���
			@param old	:	������ǰ��״̬
			@type old	:	integer
			@param new	:	�����Ժ��״̬
			@type new	:	integer
		"""
		Monster.onStateChanged( self, old, new )
		if self.getScript().bornNPC:
			if new == csdefine.ENTITY_STATE_FIGHT:
				self.setDefaultAILevel( 1 )
				self.attrAINowLevel = 1
				self.callBlewMonsterTimer = self.addTimer( CALL_BLEW_MONSTER_TIMER, CALL_BLEW_MONSTER_TIMER, ECBExtend.CALL_BLEW_MONSTER_CBID )
			elif new == csdefine.ENTITY_STATE_FREE:
				self.destroyMonsters()
				self.changeToNPC()
				if self.callBlewMonsterTimer != 0:
					self.cancel( self.callBlewMonsterTimer )
					self.callBlewMonsterTimer = 0
	
	def destroyMonsters( self ):
		"""
		����С��
		"""
		for id in self.littleMonsterIDs:
			if BigWorld.entities.has_key( id ):
				entity = BigWorld.entities[id]
				entity.exitFight()
				entity.destroy()
		self.littleMonsterIDs =[]
	
	def changeToNPC( self ):
		"""
		���NPC
		"""
		Monster.changeToNPC( self )
		#normalLvl = self.queryTemp( 'npc_normal_level', 0 )
		self.setLevel( 0 )
		bootyOwner = self.queryTemp( "ToxinFrog_bootyOwner", () )
		if bootyOwner:	# �����ս��Ʒӵ����
			if bootyOwner[ 1 ]:
				self.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_TEAM_ANTAGONIZE, bootyOwner[ 1 ] )
			else:
				self.removeCombatRelationIns( csdefine.RELATION_DYNAMIC_PRESONAL_ANTAGONIZE_ID, bootyOwner[ 0 ] )
		self.popTemp( "ToxinFrog_bootyOwner" )
		self.littleMonsterIDs = []
	
	def setAINowLevel( self, aiLevel ):
		"""
		���õ�ǰAI �ȼ�
		"""
		self.attrAINowLevel = aiLevel
	
	def disappear( self, timerID, cbID ):
		"""
		"""
		self.resetEnemyList()
		self.destroy()

	def getSpawnPos( self ):
		return self.getScript().getSpawnPos( self )

def calculatePos( spaceID, yaw, dis, pos ):
	"""
	����8���㣬�Ƕ�yaw������dis
	"""
	posL = []
	for i in range( 8 ):
		y = yaw + ( math.pi * 2 / 8 ) * i
		direction = Math.Vector3( math.sin(y), 0.0, math.cos(y) ) 
		direction.normalise()
		dstPos = pos + direction * dis
		collPos = csarithmetic.getCollidePoint( spaceID, pos, dstPos )
		endDstPos = csarithmetic.getCollidePoint( spaceID, Math.Vector3( collPos[0],collPos[1] + 10,collPos[2]), Math.Vector3( collPos[0],collPos[1] - 10,collPos[2]) )
		posL.append( endDstPos )
	return posL
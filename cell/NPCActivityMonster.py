# -*- coding: gb18030 -*-
# $Id: Exp $

from NPC108Star import NPC108Star
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory
from Resource.MonsterActivityMgr import MonsterActivityMgr
import Language
import csdefine
import BigWorld
import random
import math
import ECBExtend
from Domain_Fight import g_fightMgr

#ע�⣺С�ֵ��ٻ���������Χ��û�н�����֮�����ײ�����Բ��ֵ�ʱ�򣬾�����Ҫ��������������塣

class NPCActivityMonster( NPC108Star ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		NPC108Star.__init__( self )
		# self.changeToNPC()	# ���õ����������Ϊ�ڸ�������Ѿ�������
		# self.addTimer( 7200, 0, ECBExtend.ACTIVITY_MONSTER_DISAPPEAR_CBID )
		self.littleMonsterIDs = [] #���С�ֵ��б�
	
	def changeToNPC( self ):
		"""
		"""
		NPC108Star.changeToNPC( self )
		self.setLevel( 1 )
		self.littleMonsterIDs = []


	def callMonsters( self, mailbox ):
		"""
		define method
		"""
		count = 3
		player = BigWorld.entities[mailbox.id]
		if player.isInTeam():
			#teamMembers = self.searchTeamMember( player.getTeamMailbox().id, 30 )
			teamMembers = player.teamMembers
			if len( teamMembers ) >= 4:
				# �����4����4�����ϵ���һ�����ɱ�����ٻ�14��С��
				count = 14
			elif len( teamMembers ) >= 3:
				# �����3����3�����ϵ���һ�����ɱ�����ٻ�9��С��
				count = 9
			elif len( teamMembers ) >= 2:
				# �����2��һ�����ɱ�����ٻ�6��С��
				count = 6
		
		self.setTemp("monsterLevel", player.level )
		self.setTemp("position", player.position)
		self.createCallMonstersID( count )
		self.addTimer( 0.5, 0, ECBExtend.CALL_MONSTER_FOR_108_CBID )
	
	def createCallMonstersID( self, count ):
		"""
		ˢС�ֹ���:
		1.��һ���Ƿ�ʦ��
		2.��ʦС�ֵı���Լ1/4��
		"""
		typeMonsters = MonsterActivityMgr.instance().activityMonsterIDs
		if self.className == '20614004':
			typeMonsters = MonsterActivityMgr.instance().activityCowMonsterIDs
		elif self.className == '20624005':
			typeMonsters = MonsterActivityMgr.instance().activityGhostMonsterIDs
		
		monstersID = []

		for i in xrange( 0, count ):
			if i%4 == 0:
				monstersID.append( typeMonsters[1] )
				continue
			index = random.randint( 0, len(typeMonsters)-2 )
			monstersID.append( typeMonsters[1:][index] )

		self.setTemp( 'monstersID', monstersID )
	
	def callMonster( self, timerID, cbID ):
		"""
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD:	# ����Ѿ�����������С��
			return

		if len(self.queryTemp( 'monstersID' )) == 0:
			return

		monsterClassName = self.queryTemp( 'monstersID' ).pop(0)
		# CSOL-2063���󣬹������ˢ���ڶԻ������ߵ�3-5�װ뾶����
		x = random.randrange( 0, 4.999999, 1, float ) #���ѡȡx��ֵ
		r = random.randrange( max( 3, x ), 5, 1, float ) #���ѡȡ�뾶ֵ
		z = math.sqrt( math.pow( r, 2 ) - math.pow( x, 2 ) ) # ���ݰ뾶��x��õ�z��ֵ
		position = tuple( self.queryTemp( 'position' ) + ( x * random.choice( [-1,1] ), 0, z * random.choice( [-1,1] ) ) )
		try:
			entity = g_objFactory.getObject( monsterClassName ).createEntity( self.spaceID, position, self.direction, {"spawnPos":position, "level": self.queryTemp('monsterLevel',1)} )
			g_fightMgr.buildGroupEnemyRelationByIDs( entity, self.enemyList.keys() )
			entity.setTemp("masterID", self.id )
			self.addLittleMonster( entity.id ) #���ٻ�������С�ֱ������б���
			self.littleMonsterAddFriend( )
		except:
			ERROR_MSG( "NPCActivityMonster->Spwan little monster : No such monster id :%s" % monsterClassName )
			return
		
		if len( self.littleMonsterIDs ) == 4 or len( self.littleMonsterIDs ) == 9:
			self.addTimer( 5, 0, ECBExtend.CALL_MONSTER_FOR_108_CBID )
		else:
			self.addTimer( 0.5, 0, ECBExtend.CALL_MONSTER_FOR_108_CBID )
	
	def disappear( self, timerID, cbID ):
		"""
		"""
		self.resetEnemyList()
		self.destroy()

	def onStateChanged( self, old, new ):
		"""
		״̬�л���
			@param old	:	������ǰ��״̬
			@type old	:	integer
			@param new	:	�����Ժ��״̬
			@type new	:	integer
		"""
		NPC108Star.onStateChanged( self, old, new )
		if new == csdefine.ENTITY_STATE_FIGHT:
			self.setDefaultAILevel( 1 )
			self.attrAINowLevel = 1

	def addLittleMonster( self, id ):
		"""
		"""
		self.littleMonsterIDs.append( id ) #���ٻ�������С�ֱ������б���
	
	
	def littleMonsterAddFriend( self ):
		"""
		"""
		for i in self.littleMonsterIDs:
			entity = BigWorld.entities.get( i )
			if entity is None:
				continue
			entity.setTemp( "friendMonster", self.littleMonsterIDs )

# -*- coding: gb18030 -*-
# $Id: NPC108Star.py,v 1.11 2008-08-21 03:26:27 zhangyuxing Exp $

from Monster import Monster
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory
import Language
import csdefine
import BigWorld
import random
import math
import ECBExtend
from Domain_Fight import g_fightMgr

#ע�⣺С�ֵ��ٻ���������Χ��û�н�����֮�����ײ�����Բ��ֵ�ʱ�򣬾�����Ҫ��������������塣


class NPC108Star( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.changeToNPC()
		self.littleMonsterIDs = [] #���С�ֵ��б�
	
	def changeToNPC( self ):
		"""
		"""
		Monster.changeToNPC( self )
		self.littleMonsterIDs = []


	def createCallMonstersID( self, count ):
		"""
		ˢС�ֹ���:
		1.��һ���Ƿ�ʦ��
		2.��ʦС�ֵı���1/4��
		"""
		level = self.level
		levelStr = str(level)
		if len(levelStr) == 2:
			levelStr = '0'+levelStr

		types = ['1','2','3','5']
		monstersID = []											#��ʦ

		for i in xrange( 0, count ):
			if i%4 == 0:
				monstersID.append( '206'+ '4' +'1'+ levelStr )
			else:
				index = random.randint( 0, len(types)-1 )
				monstersID.append( '206'+ types[index] +'1'+ levelStr )

		self.setTemp( 'monstersID', monstersID )


	def callMonsters( self, playerMailbox ):
		"""
		define method
		"""
		# Ĭ�����ٻ�4��С�ֳ���
		player = BigWorld.entities[playerMailbox.id]
		count = 4
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


		self.setTemp( "position", player.position )
		self.createCallMonstersID( count )
		self.addTimer( 0.5, 0, ECBExtend.CALL_MONSTER_FOR_108_CBID )

	def callMonster( self, timerID, cbID ):
		"""
		�ٻ�ͬ�ȼ����ǹ�
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD:	# ����Ѿ�����������С��
			return
		
		if self.queryTemp( 'monstersID' ) == 0:
			return
		monstersIDs = self.queryTemp( 'monstersID' )
		if len( monstersIDs ) > 0:
			monsterClassName = monstersIDs.pop( 0 )
			# CSOL-2063���󣬹������ˢ���ڶԻ������ߵ�3-5�װ뾶����
			x = random.randrange( 0, 4.999999, 1, float ) #���ѡȡx��ֵ
			r = random.randrange( max( 3, x ), 5, 1, float ) #���ѡȡ�뾶ֵ
			z = math.sqrt( math.pow( r, 2 ) - math.pow( x, 2 ) ) # ���ݰ뾶��x��õ�z��ֵ
			
			y = self.queryTemp( "position" ).y
			
			collide = BigWorld.collide( self.spaceID, ( x, self.queryTemp( "position" ).y+10, z ), ( x, self.queryTemp( "position" ).y - 10, z ) )
			if collide != None:
				# ������Ʒ��ʱ��Ե��������ײ��������Ʒ�������
				 y = collide[0].y

			position = tuple( (self.queryTemp( "position" ).x + x, y+5 , self.queryTemp( "position" ).z + z ) )
			
			try:
				entity = g_objFactory.getObject( monsterClassName ).createEntity( self.spaceID, position, self.direction, {"spawnPos":position} )
				g_fightMgr.buildGroupEnemyRelationByIDs( entity, self.enemyList.keys() )
				self.addLittleMonster( entity.id ) #���ٻ�������С�ֱ������б���
				self.littleMonsterAddFriend( )
				entity.setTemp("masterID", self.id )
			except:
				ERROR_MSG( "No such monster:%s"%monsterClassName )
				
		self.addTimer( 0.1, 0, ECBExtend.CALL_MONSTER_FOR_108_CBID )


	def afterDie( self, killerID ):
		"""
		virtual method.

		������ص���ִ��һЩ�����ڹ�����������������顣
		"""
		Monster.afterDie( self, killerID )
		for id in self.littleMonsterIDs:
			if BigWorld.entities.has_key( id ):
				entity = BigWorld.entities[id]
				if entity.state == csdefine.ENTITY_STATE_DEAD:
					break
				entity.farDestroy()

		self.littleMonsterIDs =[]
		
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

	def setAINowLevel( self, aiLevel ):
		"""
		���õ�ǰAI �ȼ�
		"""
		self.attrAINowLevel = aiLevel

	def onSetAILevelToOne( self, timerID, cbID ):
		"""
		"""
		self.attrAIDefLevel = 1
		

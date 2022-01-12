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

#注意：小怪的召唤不处理周围有没有建筑物之类的碰撞。所以布怪的时候，尽量不要靠近建筑物等物体。

class NPCActivityMonster( NPC108Star ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		NPC108Star.__init__( self )
		# self.changeToNPC()	# 不用调用这句了因为在父类里就已经做过了
		# self.addTimer( 7200, 0, ECBExtend.ACTIVITY_MONSTER_DISAPPEAR_CBID )
		self.littleMonsterIDs = [] #存放小怪的列表
	
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
				# 如果有4个或4个以上的人一起组队杀，就召唤14个小怪
				count = 14
			elif len( teamMembers ) >= 3:
				# 如果有3个或3个以上的人一起组队杀，就召唤9个小怪
				count = 9
			elif len( teamMembers ) >= 2:
				# 如果有2人一起组队杀，就召唤6个小怪
				count = 6
		
		self.setTemp("monsterLevel", player.level )
		self.setTemp("position", player.position)
		self.createCallMonstersID( count )
		self.addTimer( 0.5, 0, ECBExtend.CALL_MONSTER_FOR_108_CBID )
	
	def createCallMonstersID( self, count ):
		"""
		刷小怪规则:
		1.第一个是法师。
		2.法师小怪的比例约1/4。
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
		if self.state == csdefine.ENTITY_STATE_DEAD:	# 如果已经死亡，则不召小怪
			return

		if len(self.queryTemp( 'monstersID' )) == 0:
			return

		monsterClassName = self.queryTemp( 'monstersID' ).pop(0)
		# CSOL-2063需求，怪物随机刷新在对话玩家身边的3-5米半径以内
		x = random.randrange( 0, 4.999999, 1, float ) #随机选取x轴值
		r = random.randrange( max( 3, x ), 5, 1, float ) #随机选取半径值
		z = math.sqrt( math.pow( r, 2 ) - math.pow( x, 2 ) ) # 根据半径和x轴得到z轴值
		position = tuple( self.queryTemp( 'position' ) + ( x * random.choice( [-1,1] ), 0, z * random.choice( [-1,1] ) ) )
		try:
			entity = g_objFactory.getObject( monsterClassName ).createEntity( self.spaceID, position, self.direction, {"spawnPos":position, "level": self.queryTemp('monsterLevel',1)} )
			g_fightMgr.buildGroupEnemyRelationByIDs( entity, self.enemyList.keys() )
			entity.setTemp("masterID", self.id )
			self.addLittleMonster( entity.id ) #将召唤出来的小怪保存在列表中
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
		状态切换。
			@param old	:	更改以前的状态
			@type old	:	integer
			@param new	:	更改以后的状态
			@type new	:	integer
		"""
		NPC108Star.onStateChanged( self, old, new )
		if new == csdefine.ENTITY_STATE_FIGHT:
			self.setDefaultAILevel( 1 )
			self.attrAINowLevel = 1

	def addLittleMonster( self, id ):
		"""
		"""
		self.littleMonsterIDs.append( id ) #将召唤出来的小怪保存在列表中
	
	
	def littleMonsterAddFriend( self ):
		"""
		"""
		for i in self.littleMonsterIDs:
			entity = BigWorld.entities.get( i )
			if entity is None:
				continue
			entity.setTemp( "friendMonster", self.littleMonsterIDs )

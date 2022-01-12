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

#注意：小怪的召唤不处理周围有没有建筑物之类的碰撞。所以布怪的时候，尽量不要靠近建筑物等物体。


class NPC108Star( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.changeToNPC()
		self.littleMonsterIDs = [] #存放小怪的列表
	
	def changeToNPC( self ):
		"""
		"""
		Monster.changeToNPC( self )
		self.littleMonsterIDs = []


	def createCallMonstersID( self, count ):
		"""
		刷小怪规则:
		1.第一个是法师。
		2.法师小怪的比例1/4。
		"""
		level = self.level
		levelStr = str(level)
		if len(levelStr) == 2:
			levelStr = '0'+levelStr

		types = ['1','2','3','5']
		monstersID = []											#法师

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
		# 默认是召唤4个小怪出来
		player = BigWorld.entities[playerMailbox.id]
		count = 4
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


		self.setTemp( "position", player.position )
		self.createCallMonstersID( count )
		self.addTimer( 0.5, 0, ECBExtend.CALL_MONSTER_FOR_108_CBID )

	def callMonster( self, timerID, cbID ):
		"""
		召唤同等级的星官
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD:	# 如果已经死亡，则不召小怪
			return
		
		if self.queryTemp( 'monstersID' ) == 0:
			return
		monstersIDs = self.queryTemp( 'monstersID' )
		if len( monstersIDs ) > 0:
			monsterClassName = monstersIDs.pop( 0 )
			# CSOL-2063需求，怪物随机刷新在对话玩家身边的3-5米半径以内
			x = random.randrange( 0, 4.999999, 1, float ) #随机选取x轴值
			r = random.randrange( max( 3, x ), 5, 1, float ) #随机选取半径值
			z = math.sqrt( math.pow( r, 2 ) - math.pow( x, 2 ) ) # 根据半径和x轴得到z轴值
			
			y = self.queryTemp( "position" ).y
			
			collide = BigWorld.collide( self.spaceID, ( x, self.queryTemp( "position" ).y+10, z ), ( x, self.queryTemp( "position" ).y - 10, z ) )
			if collide != None:
				# 掉落物品的时候对地面进行碰撞检测避免物品陷入地下
				 y = collide[0].y

			position = tuple( (self.queryTemp( "position" ).x + x, y+5 , self.queryTemp( "position" ).z + z ) )
			
			try:
				entity = g_objFactory.getObject( monsterClassName ).createEntity( self.spaceID, position, self.direction, {"spawnPos":position} )
				g_fightMgr.buildGroupEnemyRelationByIDs( entity, self.enemyList.keys() )
				self.addLittleMonster( entity.id ) #将召唤出来的小怪保存在列表中
				self.littleMonsterAddFriend( )
				entity.setTemp("masterID", self.id )
			except:
				ERROR_MSG( "No such monster:%s"%monsterClassName )
				
		self.addTimer( 0.1, 0, ECBExtend.CALL_MONSTER_FOR_108_CBID )


	def afterDie( self, killerID ):
		"""
		virtual method.

		死亡后回掉，执行一些子类在怪物死后必须做的事情。
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
		self.littleMonsterIDs.append( id ) #将召唤出来的小怪保存在列表中
	
	
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
		设置当前AI 等级
		"""
		self.attrAINowLevel = aiLevel

	def onSetAILevelToOne( self, timerID, cbID ):
		"""
		"""
		self.attrAIDefLevel = 1
		

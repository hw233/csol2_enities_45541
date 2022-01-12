# -*- coding: gb18030 -*-
# TreasureMonster.py

#################################################################################
# TreasureMonster,盗宝贼一类的怪物，由玩家挖宝时产生的，一产生即所有权确定但是可以更改的怪物
# 此怪物一旦玩家不鸟了，会自行消失（AI配置实现）
# 重写了死亡接口
#################################################################################

from Monster import Monster
from bwdebug import *
from interface.CombatUnit import CombatUnit
import BigWorld
import csconst
import csstatus
import csdefine
import ECBExtend
import random
import items
import sys

g_items = items.instance()

class TreasureMonster( Monster ):
	"""
	宝藏怪物类
	"""
	def __init__(self):
		Monster.__init__( self )
	
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		初始化自己的entity的数据
		"""
		Monster.initEntity( self, selfEntity )
		selfEntity.setEntityType( csdefine.ENTITY_TYPE_TREASURE_MONSTER )

	def getOwner( self, selfEntity ):
		"""
		获得所有者的baseMailBox
		"""
		return selfEntity.queryTemp( "ownerBaseMailBox", None )
		
	def getOwnerID( self, selfEntity ):
		"""
		"""
		return selfEntity.queryTemp( "ownerID", 0 )

	def setOwner( self, selfEntity, owner ):
		"""
		设置自己的所有者(同时设置所有权)
		"""
		selfEntity.setTemp( "ownerID", owner.id )
		selfEntity.setTemp( "ownerName", owner.getName() )
		if owner.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			selfEntity.bootyOwner = ( owner.id, 0 )

	def dropTreasure( self, selfEntity, bootyOwner ):
		"""
		掉落宝藏
		"""
		dropItem = selfEntity.queryTemp( "dropItem", 0 )
		if dropItem == 0:
			return
		x1 = random.randint(-2,2)
		z1 = random.randint(-2,2)
		pos = selfEntity.position							# 掉落的位置（玩家的位置）
		x, y, z = x1 + pos[0], pos[1], z1 + pos[2]	# 加上偏移量后具体掉落的位置
		direction = (0.0, 0.0, 0.0)					# 方向
		item = g_items.createDynamicItem( dropItem , 1 )
		item.set( 'treasure_space', selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		item.set( "level", selfEntity.level )
		itemsData = [item]
		collide = BigWorld.collide( selfEntity.spaceID, ( x, y + 2, z ), ( x, y - 1, z ) )
		if collide != None:
			# 掉落物品的时候对地面进行碰撞检测避免物品陷入地下
			y = collide[0].y
		itemBox = BigWorld.createEntity( "DroppedBox", selfEntity.spaceID, (x, y, z), direction, {} )
		itemBox.init( bootyOwner, itemsData )


	def onMonsterDie( self, selfEntity, killerID ):
		"""
		"""
		Monster.onMonsterDie( self, selfEntity, killerID )
		bootyOwner = selfEntity.getBootyOwner()
		self.dropTreasure( selfEntity, bootyOwner )	# 掉落宝藏

		# 如果挖宝人存在但是不是挖宝人打死的怪,挖宝人也要获得经验奖励
		ownerID = self.getOwnerID( selfEntity )
		if BigWorld.entities.has_key( ownerID ) and killerID != ownerID:
		 	treasureScooper = BigWorld.entities[ ownerID ]
		 	if not treasureScooper.state == csdefine.ENTITY_STATE_DEAD:
		 		# 挖宝人如果没死亡，即使不是被挖宝人所杀，也要给挖宝人玩家补偿经验
				if selfEntity.bootyOwner[0] != 0 and selfEntity.bootyOwner[0] != ownerID and selfEntity.bootyOwner[1] == 0:
					# 如果怪物所有权不是挖宝人而是其他人
					selfEntity.gainSingleReward( treasureScooper )
					treasureScooper.statusMessage( csstatus.TREATURE_MONSTER_KILLED_BY_OTHERS, selfEntity.exp )
				elif selfEntity.bootyOwner[1] != 0 and not ownerID in selfEntity.searchTeamMember( selfEntity.bootyOwner[1], 50 ):
					# 如果怪物所有权是队伍，但是队伍里没有挖宝人
					selfEntity.gainSingleReward( treasureScooper )
					treasureScooper.statusMessage( csstatus.TREATURE_MONSTER_KILLED_BY_OTHERS, selfEntity.exp )

	def setBirthTime( self, selfEntity ):
		"""
		设置自行销毁时间
		"""
		birthTime = BigWorld.time()
		selfEntity.setTemp( "entity_birth_time", int( birthTime ) )
		
	def getRelationEntity( self ):
		"""
		获取关系判定的真实entity
		"""
		owner = BigWorld.entities.get( self.getOwnerID() )
		if not owner:
			return None
		else:
			return owner
		
	def queryCombatRelation( self, entity ):
		owner = BigWorld.entities.get( self.getOwnerID() )
		if owner:
			return owner.queryCombatRelation( entity )
		else:
			return csdefine.RELATION_FRIEND
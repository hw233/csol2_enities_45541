# -*- coding: gb18030 -*-
from SpawnPoint import SpawnPoint
import BigWorld
import csconst
from ObjectScripts.GameObjectFactory import g_objFactory
import items
import csdefine
g_items = items.instance()
import random
import Const
import cschannel_msgs

itemIDs = [60101008]
keyItemIDs = { csdefine.SPECIAL_BOX_01 : 60101108,
				csdefine.SPECIAL_BOX_02 : 60101109,
				csdefine.SPECIAL_BOX_03 : 60101110,
				}

DROP_BOX_NAMES = { csdefine.SPECIAL_BOX_01  : cschannel_msgs.MONSTER_ATTACK_BOX_MI_WANG,
					csdefine.SPECIAL_BOX_02 : cschannel_msgs.MONSTER_ATTACK_BOX_KONG_JU,
					csdefine.SPECIAL_BOX_03	: cschannel_msgs.MONSTER_ATTACK_BOX_HEI_AN,
					}

"""
monsterType :
		0: 小怪
		1: 头领
		2: boss
		3: buff
		4: 特殊箱子
"""

MONSTER_TYPE_MONSTER		=	0	#小怪
MONSTER_TYPE_TOULING		=	1	#头领
MONSTER_TYPE_BOSS			=	2	#boss
MONSTER_TYPE_BUFF			=	3	#buff
MONSTER_TYPE_BOX			=	4	#特殊箱子

CREATE_ENTITY_TIME 	= 0


class SpawnPointMonsterAttack( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )
		self.registerMgr( selfEntity )
		

	def registerMgr( self, selfEntity ):
		"""
		"""
		spaceLabel = BigWorld.getSpaceDataFirstForKey( selfEntity.spaceID, csconst.SPACE_SPACEDATA_KEY )
		group = selfEntity.queryTemp( "group" )
		part = selfEntity.queryTemp( "part" )
		if self.getMonsterType( selfEntity ) <= MONSTER_TYPE_BOSS:
			BigWorld.globalData["MonsterAttackMgr"].addSpawnPoint( selfEntity.base, spaceLabel, group, part )
		elif self.getMonsterType( selfEntity ) == MONSTER_TYPE_BUFF:
			BigWorld.globalData["MonsterAttackMgr"].addSpawnPointBuff( selfEntity.base, spaceLabel )
		elif self.getMonsterType( selfEntity ) == MONSTER_TYPE_BOX:
			BigWorld.globalData["MonsterAttackMgr"].addSpawnPointBox( selfEntity.base, spaceLabel, group )
	
	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		entityName = ""
		if self.getMonsterType( selfEntity ) == MONSTER_TYPE_BOSS:
			entityName = random.choice( selfEntity.entityName.split((";") ) )
		else:
			entityName = selfEntity.entityName
		args = self.getEntityArgs( selfEntity, params )
		args[ "className" ] = entityName
		entity = self._createEntity( selfEntity, args, 1 )[0] #只创建一个
		selfEntity.setTemp( "monsterID", entity.id )


	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		# 小于0则不复活
		BigWorld.globalData["MonsterAttackMgr"].onMonsterDied( { "monsterType" : self.getMonsterType( selfEntity ) } )
	
	def onAttackEnd( self ):
		"""
		define method
		"""
		monster = BigWorld.entities.get( selfEntity.queryTemp( "monsterID", 0 ), None )
		if monster is not None:
			monster.destroy()
	
	def spawnBox( self ):
		"""
		刷新宝箱
		"""
		itemID = random.choice( itemIDs )
		item = g_items.createDynamicItem( itemID, 1 )
		if item is None:
			return

		params = { "dropType" : csdefine.DROPPEDBOX_TYPE_MONSTER, "droperName" : item.name() }
		itemBox = BigWorld.createEntity( "DroppedBox", selfEntity.spaceID, selfEntity.position, selfEntity.direction, params )
		itemBox.initEntity( [], [item] )
	
	def spawnSpecialBox( self, boxType ):
		"""
		刷新特殊宝箱
		"""
		params = { "dropType" : csdefine.DROPPEDBOX_TYPE_MONSTER, "droperBoxName" : DROP_BOX_NAMES[boxType], "key_itemID" :  keyItemIDs[boxType] }
		BigWorld.createEntity( "DroppedBoxForMonsterAttack", selfEntity.spaceID, selfEntity.position, selfEntity.direction, params )

	def addAreaPlayerBuff( self, selfEntity ):
		"""
		define method
		"""
		buffID = selfEntity.queryTemp( "selfEntity", 0 )
		if buffID == 0:
			return		
		for i in self.entitiesInRangeExt( selfEntity.queryTemp( "buffRange", 0.0 ), 'Role' ):
			i.spellTarget( buffID, i.id )
	
	def getMonsterType( self, selfEntity ):
		return selfEntity.queryTemp( "monsterType", 0 )
	
	def onBaseGotCell( self, selfEntity ):
		pass
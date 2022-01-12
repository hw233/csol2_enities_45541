# -*- coding: gb18030 -*-

# $Id: SpawnPointTianguan.py,v 1.4 2008-08-13 01:20:23 zhangyuxing Exp $
"""
"""

import BigWorld
import cschannel_msgs
import ShareTexts as ST
from bwdebug import *
import csdefine
import csconst
from interface.GameObject import GameObject
from ObjectScripts.GameObjectFactory import g_objFactory
import random
from SpawnPointCopy import SpawnPointCopy

monsters 	= ['20611154','20621154','20631154','20641154','20651154']							#怪物ID列表
littleboss 	= ['20651155','20621155','20631155','20611155','20641155']							#小BOSS ID列表
bigboss 	= ['20611156','20621156','20631156','20641156','20651156']							#大BOSS ID列表

NamesFaction = {'1':cschannel_msgs.TIAN_GUAN_MONSTER_DEF_3,'2':cschannel_msgs.TIAN_GUAN_MONSTER_DEF_4,'3':cschannel_msgs.TIAN_GUAN_MONSTER_DEF_5,'4':cschannel_msgs.TIAN_GUAN_MONSTER_DEF_6,'5':cschannel_msgs.TIAN_GUAN_MONSTER_DEF_7}

monsterNames = [cschannel_msgs.TIAN_GUAN_MONSTER_DEF_8,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_9,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_10,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_11,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_12,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_13,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_14,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_15,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_16,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_17]
littlebossNames = [cschannel_msgs.TIAN_GUAN_MONSTER_DEF_18,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_19,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_20,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_21,cschannel_msgs.TIAN_GUAN_MONSTER_DEF_22]
bigbossNames = [cschannel_msgs.TIAN_GUAN_MONSTER_DEF_23]

class SpawnPointTianguan( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		SpawnPointCopy.initEntity( self, selfEntity )
		level = selfEntity.getEntityData( "level" )
		teamcount = selfEntity.getEntityData( "teamcount" )
		selfEntity.getCurrentSpaceBase().addSpawnPointTianguan( selfEntity.base, level, teamcount )										#spawnPointTianguan 的 level 指的是关卡等级（第几关）
		selfEntity.currentRedivious = 0

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		if selfEntity.getCurrentSpaceBase() == None:
			return
		selfEntity.currentRedivious += 1
		monsterType = selfEntity.getEntityData( "monsterType" )
		if selfEntity.currentRedivious < selfEntity.rediviousTotal:
			params = {}
			params[ "tianguan_level" ] = selfEntity.queryTemp( "tianguan_level" )
			params[ "current_toll_gate" ] = selfEntity.queryTemp( "current_toll_gate" )
			self.createEntity( selfEntity, params )
			selfEntity.getCurrentSpaceBase().cell.onConditionChange( {"monsterType" : monsterType, "redivious": 1 } )
			return
		selfEntity.getCurrentSpaceBase().cell.onConditionChange( {"monsterType" : monsterType, "redivious": 0 } )

	def createEntity( self, selfEntity, params = {} ):
		"""
		define method
		"""
		tianguan_level = params.get( "tianguan_level", 0 )
		current_toll_gate = params.get( "current_toll_gate", 0 )
		"""
		if not tianguan_level:
			tianguan_level = selfEntity.getEntityData( "level", 0 )
		
		if not current_toll_gate:
			current_toll_gate = selfEntity.getEntityData( "current_toll_gate", 0 )
		"""
		selfEntity.setTemp( "tianguan_level", tianguan_level )
		selfEntity.setTemp( "current_toll_gate", current_toll_gate )
		
		d = self.getEntityArgs( selfEntity, params )
		d['level'] = min( tianguan_level, csconst.ROLE_LEVEL_UPPER_LIMIT )
		monsterType = selfEntity.getEntityData( "monsterType" )
		if monsterType == 0:
			if not len( monsters ) == 0:
				j = random.randint(0, len( monsters ) - 1 )
				factionName = NamesFaction[monsters[j][3]] + monsterNames[random.randint( 0, len( monsterNames ) - 1 )]
				d['uname'] = factionName
				selfEntity.createNPCObject( monsters[j], selfEntity.position, selfEntity.direction, d )
		elif monsterType == 1:
			if not len( littleboss ) == 0:
				d['uname'] = littlebossNames[current_toll_gate - 1]
				selfEntity.createNPCObject( littleboss[current_toll_gate - 1], selfEntity.position, selfEntity.direction, d )

		else:
			if not len( bigboss ) == 0:
				j = random.randint(0, len( bigboss ) - 1 )
				factionName = bigbossNames[random.randint( 0, len( bigbossNames ) - 1 )]
				d['uname'] = factionName
				selfEntity.createNPCObject( bigboss[j], selfEntity.position, selfEntity.direction, d )
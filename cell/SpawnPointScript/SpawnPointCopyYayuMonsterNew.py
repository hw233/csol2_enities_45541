# -*- coding: gb18030 -*-



import Language
from SpawnPointCopyYeWai import SpawnPointCopyYeWai
import cschannel_msgs
import ShareTexts as ST
from ObjectScripts.GameObjectFactory import g_objFactory
import random
import ECBExtend
import csdefine
import csconst
import csstatus
import time
import BigWorld
import random
from utils import vector3TypeConvert
from config.server.YayuSpawnConfigScript import Datas as yayuMonster
	
def getMonsterTemplate( difficulty, step, batch ):
	"""
	根据副本难度、阶段、刷挂批次对应的模板中随机选择一个
	"""
	templates = yayuMonster[ difficulty ][ step ][ batch ][ "template" ]
	key = random.randint( 1, len( templates ) )
	return templates[ key ]

class SpawnPointCopyYayuMonsterNew( SpawnPointCopyYeWai ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopyYeWai.initEntity( self, selfEntity )
		selfEntity.getCurrentSpaceBase().addSpawnPointMonsters( selfEntity.base, selfEntity.queryTemp( "monsterType" ) )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		if selfEntity.getCurrentSpaceBase() == None or selfEntity.queryTemp( "monsterType" ) != 1:		# 只有Boss死亡才通知副本
			return
		if selfEntity.getCurrentSpaceBase():
			selfEntity.getCurrentSpaceBase().cell.onConditionChange( { "reason": "monsterDied", "monsterType": selfEntity.queryTemp( "monsterType" ) } )

	def entityBorn( self, className, id ):
		"""
		"""
		if selfEntity.getCurrentSpaceBase() == None:
			return
		if selfEntity.getCurrentSpaceBase():
			selfEntity.getCurrentSpaceBase().cell.onYayuMonsterBorn( className, id )
		
	def createEntity( self, selfEntity, params ):
		"""
		define method
		"""
		selfEntity.setTemp("step",  params["step"] )
		selfEntity.setTemp( "batch", params["batch"] )
		selfEntity.setTemp( "difficulty", params["difficulty"] )
		selfEntity.setTemp( "yayuID", params["yayuID"] )
		self.spawnMonster( selfEntity, { "level": params["level"] } )

	def spawnMonster( self, selfEntity, params = {} ):
		"""
		"""
		d = {}
		d["spawnMB"] = selfEntity.base
		if len( selfEntity.patrolPathNode ):
			d["patrolPathNode"] = selfEntity.patrolPathNode
			d["patrolList"] = selfEntity.patrolList

		# 额外增加的属性
		for key, value in params.iteritems():
			d[key] = value

		# 创建所有的entity
		template = getMonsterTemplate( selfEntity.queryTemp( "difficulty", 1 ), selfEntity.queryTemp( "step", 1 ), selfEntity.queryTemp( "batch", 1 ) )
		entityName = template[ "classNames" ].strip(';').split(';')
		position = template[ "positions" ].strip(';').split(';')
		num = template[ "num" ].strip(';').split(';')
		for e in position:
			index = position.index(e)
			monsterName = entityName[ index ]
			for i in xrange( int( num[ index] ) ):
				d["spawnPos"] = vector3TypeConvert(e)
				entity = g_objFactory.getObject( monsterName ).createEntity( selfEntity.spaceID, vector3TypeConvert( e ), selfEntity.direction, d.copy() )
				entity.setTemp( "enemyYayuID", selfEntity.queryTemp( "yayuID" ) )
				self.entityBorn( entity.className, entity.id )
				entity.viewRange = 200
				entity.territory = 200		
				if entity.className == "10122018":
					return
				entity.addTimer( 3.0, 0, ECBExtend.ADD_YAYU_TO_EMEMY_CBID )
	
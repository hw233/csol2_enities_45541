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
import Const
import csstatus
from utils import vector3TypeConvert
from config.item.yayuConfigScript import Datas as yayuMonster

def getMonsterClassName( difficulty, step, count ):
	"""
	"""
	infos = yayuMonster[ difficulty ][ step ]["spawnClassName"]			# 刷新的怪物className
	return infos[ count ]
	
def getMonsterCount( step, difficulty ):
	"""
	"""
	count = yayuMonster[ difficulty ][ step ][ "monster_number" ]
	if step > 11 and difficulty == csconst.SPACE_COPY_YE_WAI_EASY:
		return
	if step > 16 and difficulty == csconst.SPACE_COPY_YE_WAI_DIFFICULTY:
		return
	return count

def getNextTime( step, difficulty ):
	"""
	"""
	return yayuMonster[ difficulty ][ step ][ "spawn_time" ]


class SpawnPointCopyYayuMonster( SpawnPointCopyYeWai ):
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
		if selfEntity.getCurrentSpaceBase() == None:
			return
		if selfEntity.getCurrentSpaceBase():
			selfEntity.getCurrentSpaceBase().cell.onConditionChange( { "reason": "monsterDied", "monsterType": selfEntity.queryTemp( "monsterType" ) } )

	def createEntity( self, selfEntity, params ):
		"""
		define method
		"""
		selfEntity.setTemp( "monsterStep", params["step"] )
		selfEntity.setTemp( "monsterLevel", params["level"] )
		selfEntity.setTemp( "yayuID", params["yayuID"] )
		selfEntity.setTemp("monsterCount", 0 )
		
		selfEntity.addTimer( 0.0, 0.0, Const.SPAWN_ON_SERVER_START )

	def spawnMonster( self, selfEntity, params = {} ):
		"""
		"""
		args = self.getEntityArgs( selfEntity, params )
		entityName = getMonsterClassName( selfEntity.queryTemp("difficulty"), selfEntity.queryTemp("monsterStep"), selfEntity.queryTemp("monsterCount", 0) )
		position = yayuMonster[ selfEntity.queryTemp("difficulty") ][ selfEntity.queryTemp("monsterStep") ][ "position" ].split( ";" )
		for e in position:
			monsterName = entityName.split(";")[position.index(e)]
			if monsterName == "0":
				continue
			args["spawnPos"] = vector3TypeConvert(e)
			entity = g_objFactory.getObject( monsterName ).createEntity( selfEntity.spaceID, vector3TypeConvert(e), selfEntity.direction, args )
		
			entity.viewRange =  200
			entity.territory = 200
			
			entity.setTemp( "enemyYayuID", params["yayuID"] )
			if entity.className == "10122018":
				return
			entity.addTimer( 3.0, 0, ECBExtend.ADD_YAYU_TO_EMEMY_CBID )

	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if userData == Const.SPAWN_ON_SERVER_START:
			count = selfEntity.queryTemp( "monsterCount", 0 )
			if count < getMonsterCount( selfEntity.queryTemp("monsterStep"), selfEntity.queryTemp("difficulty") ):
				selfEntity.addTimer( getNextTime( selfEntity.queryTemp("monsterStep"), selfEntity.queryTemp("difficulty") ), 0.0, Const.SPAWN_ON_SERVER_START )
				self.spawnMonster( selfEntity, {"level":selfEntity.queryTemp( "monsterLevel", 1 ), "yayuID": selfEntity.queryTemp( "yayuID", 0 )} )
				count += 1
				selfEntity.setTemp( "monsterCount", count )
			
			return

		SpawnPointCopyYeWai.onTimer( self, selfEntity, controllerID, userData )
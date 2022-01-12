# -*- coding: gb18030 -*-

from SpaceCopy import SpaceCopy
from bwdebug import *
import Const
import csconst

AUTO_SPAWN_TYPE = 0						# 副本开启就刷出
PLAYER_SOLDIER_MONSTER_TYPE = 11		# 玩家小兵
NPC_SOLDIER_MONSTER_TYPE = 22			# NPC小兵
ELITE_MONSTER_TYPE = 1					# 精英
NPC_ATTACK_CAR = 2						# NPC攻城车
PLAYER_ATTACK_CAR = 3					# 玩家攻城车
PLAYER_LEAVE_ADD_BOSS = 4 				# BOSS

YXLM_SPAWN_POINT_TYPE = [ "SpawnPointYXLMBoss", "SpawnPointCopyYXLMPVP" ]

class SpaceCopyYXLM( SpaceCopy ):
	"""
	英雄联盟副本
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.spawnMonstersList = {}
		self.cellData['teamLevel'] = self.params['teamLevel']
		self.cellData['teamMaxLevel'] = self.params['teamMaxLevel']
		self.spawnEliteAmount = 1
		self.spawnPlayerSoldierTimes = 0
		self.spawnNpcSoldierTimes = 0
		self.spawnRobots = []
		self.spawnPointCopyDict = {}				# 记录副本中所有怪物出生点 such as:{ "className" : [ spawnPointCopy.base, ... ], ... }
		self.createFinish = False					# 标记spawnPoint是否加载完毕
		self.currParams = None						# 临时变量：记录当前要出生的怪物参数
		self.teamInfos  = ( self.params[ "teamID" ], 0 )
		self.difficulty = self.params[ "difficulty" ]
	
	def checkNeedSpawn( self, sec ):
		# 检查是否要刷出此刷新点
		if self.difficulty == csconst.SPACE_COPY_YE_WAI_NIGHTMARE and sec.readString( "type" ) == "SpawnPointYXLMBoss":
			if sec.readString( "properties/entityName" ) not in self.params[ "robotInfos" ]:
				return False
			
		return SpaceCopy.checkNeedSpawn( self, sec )

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		创建好了一个entity的通知
		@param	entityType		: entity的脚本类别
		@type 	entityType		: String
		@param	entity			: baseEntity实体
		"""
		if entityType in YXLM_SPAWN_POINT_TYPE:
			monsterType =  getattr( baseEntity, "monsterType", 0 )
			if self.spawnMonstersList.has_key( monsterType ):
				self.spawnMonstersList[monsterType].append( baseEntity )
			else:
				self.spawnMonstersList[monsterType] = [ baseEntity ]
		
		SpaceCopy.onLoadedEntity( self, entityType, baseEntity )
	
	def onSpawnPointLoadedOver( self, retCode ):
		"""
		virtual method.
		一个副本的spawnPoint 加载完毕。
		"""
		self.spawnMonsters( { "monsterType":  AUTO_SPAWN_TYPE } )
		SpaceCopy.onSpawnPointLoadedOver( self, retCode )
			
	def spawnMonsters( self, params ):
		"""
		define method
		"""
		params[ "level" ] = self.params['teamLevel']
		if params["monsterType"] == AUTO_SPAWN_TYPE:
			if not self.spawnMonstersList.has_key( params["monsterType"] ):
				return
			
			for i in self.spawnMonstersList[ params["monsterType"] ]:
				i.cell.createEntity( params )
				
		elif params["monsterType"] == ELITE_MONSTER_TYPE:					# 如果是刷精英，下次精英数量递增1
			if not self.spawnMonstersList.has_key( params["monsterType"] ):
				return
			amount = 0
			while( amount < self.spawnEliteAmount ):
				for i in self.spawnMonstersList[ params["monsterType"] ]:
					i.cell.createEntity( params )
				amount += 1
			self.spawnEliteAmount += 1
		
		elif params["monsterType"] == PLAYER_SOLDIER_MONSTER_TYPE:				# 每三波小怪中有一波小兵增加一个攻城车，所以刷小兵的时候记录一下是第几波
			self.spawnPlayerSoldierTimes += 1
			if self.spawnPlayerSoldierTimes == 3:
				self.spawnMonsters( { "monsterType":  PLAYER_ATTACK_CAR } )
				self.spawnPlayerSoldierTimes = 0
			
		elif params["monsterType"] == NPC_SOLDIER_MONSTER_TYPE:				# 每三波小怪中有一波小兵增加一个攻城车，所以刷小兵的时候记录一下是第几波
			self.spawnNpcSoldierTimes += 1
			if self.spawnNpcSoldierTimes == 3:
				self.spawnMonsters( { "monsterType":  NPC_ATTACK_CAR } )
				self.spawnNpcSoldierTimes = 0
			
		elif params["monsterType"] == PLAYER_ATTACK_CAR or params["monsterType"] == NPC_ATTACK_CAR :
			if not self.spawnMonstersList.has_key( params["monsterType"] ):
				return
			for i in self.spawnMonstersList[ params["monsterType"] ]:
				i.cell.createEntity(  params )
				
	def onBeforeDestroyCellEntity( self ):
		"""
		cell destory之前，清空刷新列表。防止space销毁后仍继续刷新怪物
		"""
		self.spawnMonstersList = None

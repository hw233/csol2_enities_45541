# -*- coding: gb18030 -*-

from SpaceCopy import SpaceCopy
from bwdebug import *
import Const
import csconst

AUTO_SPAWN_TYPE = 0						# ����������ˢ��
PLAYER_SOLDIER_MONSTER_TYPE = 11		# ���С��
NPC_SOLDIER_MONSTER_TYPE = 22			# NPCС��
ELITE_MONSTER_TYPE = 1					# ��Ӣ
NPC_ATTACK_CAR = 2						# NPC���ǳ�
PLAYER_ATTACK_CAR = 3					# ��ҹ��ǳ�
PLAYER_LEAVE_ADD_BOSS = 4 				# BOSS

YXLM_SPAWN_POINT_TYPE = [ "SpawnPointYXLMBoss", "SpawnPointCopyYXLMPVP" ]

class SpaceCopyYXLM( SpaceCopy ):
	"""
	Ӣ�����˸���
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
		self.spawnPointCopyDict = {}				# ��¼���������й�������� such as:{ "className" : [ spawnPointCopy.base, ... ], ... }
		self.createFinish = False					# ���spawnPoint�Ƿ�������
		self.currParams = None						# ��ʱ��������¼��ǰҪ�����Ĺ������
		self.teamInfos  = ( self.params[ "teamID" ], 0 )
		self.difficulty = self.params[ "difficulty" ]
	
	def checkNeedSpawn( self, sec ):
		# ����Ƿ�Ҫˢ����ˢ�µ�
		if self.difficulty == csconst.SPACE_COPY_YE_WAI_NIGHTMARE and sec.readString( "type" ) == "SpawnPointYXLMBoss":
			if sec.readString( "properties/entityName" ) not in self.params[ "robotInfos" ]:
				return False
			
		return SpaceCopy.checkNeedSpawn( self, sec )

	def onLoadedEntity( self, entityType, baseEntity ):
		"""
		virtual method.
		��������һ��entity��֪ͨ
		@param	entityType		: entity�Ľű����
		@type 	entityType		: String
		@param	entity			: baseEntityʵ��
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
		һ��������spawnPoint ������ϡ�
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
				
		elif params["monsterType"] == ELITE_MONSTER_TYPE:					# �����ˢ��Ӣ���´ξ�Ӣ��������1
			if not self.spawnMonstersList.has_key( params["monsterType"] ):
				return
			amount = 0
			while( amount < self.spawnEliteAmount ):
				for i in self.spawnMonstersList[ params["monsterType"] ]:
					i.cell.createEntity( params )
				amount += 1
			self.spawnEliteAmount += 1
		
		elif params["monsterType"] == PLAYER_SOLDIER_MONSTER_TYPE:				# ÿ����С������һ��С������һ�����ǳ�������ˢС����ʱ���¼һ���ǵڼ���
			self.spawnPlayerSoldierTimes += 1
			if self.spawnPlayerSoldierTimes == 3:
				self.spawnMonsters( { "monsterType":  PLAYER_ATTACK_CAR } )
				self.spawnPlayerSoldierTimes = 0
			
		elif params["monsterType"] == NPC_SOLDIER_MONSTER_TYPE:				# ÿ����С������һ��С������һ�����ǳ�������ˢС����ʱ���¼һ���ǵڼ���
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
		cell destory֮ǰ�����ˢ���б���ֹspace���ٺ��Լ���ˢ�¹���
		"""
		self.spawnMonstersList = None

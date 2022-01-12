# -*- coding: gb18030 -*-

from SpaceCopy import SpaceCopy
import Const

AUTO_SPAWN_TYPE = 0						# ����������ˢ��
PLAYER_SOLDIER_MONSTER_TYPE = 11		# ���С��
NPC_SOLDIER_MONSTER_TYPE = 22			# NPCС��
ELITE_MONSTER_TYPE = 1					# ��Ӣ
NPC_ATTACK_CAR = 2						# NPC���ǳ�
PLAYER_ATTACK_CAR = 3					# ��ҹ��ǳ�
PLAYER_LEAVE_ADD_BOSS = 4 				# ����˳���ˢBOSS

YXLM_SPAWN_POINT_TYPE = [ "SpawnPointCopyYXLMPVP" ]
YXLM_SPAWN_POINT_BOSS_TYPE = [ "SpawnPointYXLMBoss" ]

class SpaceCopyYXLMPVP( SpaceCopy ):
	"""
	Ӣ�����˸���
	"""
	def __init__( self ):
		SpaceCopy.__init__( self )
		self.spawnMonstersList = {}
		self.spawnBossList= {}
		self.spawnEliteAmount = 1
		self.spawnPlayerSoldierTimes = 0
		self.spawnNpcSoldierTimes = 0
		self.spawnRobots = []
		self.teamInfos  = self.params[ "teamInfos" ]

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
		
		if entityType in YXLM_SPAWN_POINT_BOSS_TYPE:
			if self.spawnBossList.has_key( baseEntity.belong ):
				self.spawnBossList[ baseEntity.belong ].append( baseEntity )
			else:
				self.spawnBossList[ baseEntity.belong ] = [ baseEntity ]
		
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
				i.cell.createEntity( params )
				
		elif params["monsterType"] == PLAYER_LEAVE_ADD_BOSS:
			belong = params.pop( "belong", 0 )
			if belong and self.spawnBossList.has_key( belong ):
				createNum = params.pop( "createNum", 1 )
				for i,sp in enumerate( self.spawnBossList[ belong ] ):
					if i >= createNum:
						break
						
					sp.cell.createEntity( params )
					del self.spawnBossList[ belong ][ i ]
					
	def onBeforeDestroyCellEntity( self ):
		"""
		cell destory֮ǰ�����ˢ���б���ֹspace���ٺ��Լ���ˢ�¹���
		"""
		self.spawnMonstersList = None
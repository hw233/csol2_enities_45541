# -*- coding: gb18030 -*-
import csdefine

MONSTER_SPAWN_YE_WAI = [ "SpawnPointCopyYeWai" ,]

class SpaceCopyYeWaiInterface:
	def __init__( self ):
		self.bossIDs = []
		self.monsterIDs = []
		
	def getDifficulty( self ):
		return self.params[ "difficulty" ]
	
	def checkNeedSpawn( self, sec ):
		if sec.readString( "type" ) in MONSTER_SPAWN_YE_WAI:
			monsterType = sec.readInt( "properties/monsterType" )
			difficulty = sec.readInt( "properties/difficulty" )
			spawnNum = sec.readInt( "properties/rediviousTotal" )
			
			if self.getDifficulty() < difficulty:
				return False
				
			if monsterType == csdefine.MONSTER_TYPE_COMMON_BOSS:
				if self.getDifficulty() != difficulty:
					return False
			
			className = sec.readString( "properties/entityName" )
			self.countMonsterNum( monsterType, difficulty, className, spawnNum )
			
		return True
	
	def countMonsterNum( self, monsterType, difficulty, className, num = 1 ):
		# 统计怪物数量
		if monsterType == csdefine.MONSTER_TYPE_COMMON_MONSTER:
			self.monsterIDs.append( className )
		elif monsterType == csdefine.MONSTER_TYPE_COMMON_BOSS:
			self.bossIDs.append( className )
		
	def onSpawnPointLoadedOver( self, retCode ):
		# spawnPoint 加载完毕。
		self.cell.onSetSpawnInfos( len( self.monsterIDs ), len( self.bossIDs ) )
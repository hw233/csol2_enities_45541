# -*- coding: gb18030 -*-
import copy
import Math

import Language
from config.server.potentialMeleeConfig import Datas as g_config

BOSS_CLASS_NAME = [ "20144087", "20114016", "20124027", "20154023" ]
NOT_CALC_CLASS_NAME = [ "10122018", ]

class CopyPotentialMeleeLoader:
	# 副本信息
	_instance = None
	def __init__( self ):
		assert CopyPotentialMeleeLoader._instance is None
		self.data = {}
		self.monsterCount = 0
		self.bossCount = 0
		self.mustKillAllBath = []
		
	@classmethod
	def instance( self ):
		"""
		"""
		if self._instance is None:
			self._instance = CopyPotentialMeleeLoader()
		return self._instance

	def __getitem__( self, key ):
		"""
		取得Space数据部分
		"""
		if self.data.has_key( key ):
			return self.data[key]
		else:
			return None
	
	def getBatchTotal( self ):
		return len( self.data )
	
	def getMonsterCount( self ):
		return self.monsterCount
	
	def getBossCount( self ):
		return self.bossCount
	
	def getBatchMonsterCount( self, batch ):
		count = 0
		for inf in self.data[ batch ]:
			if inf[ 0 ] not in BOSS_CLASS_NAME and inf[ 0 ] not in NOT_CALC_CLASS_NAME:
				count += inf[ 4 ]
			
		return count
	
	def getBatchBossCount( self, batch ):
		count = 0
		for inf in self.data[ batch ]:
			if inf[ 0 ] in BOSS_CLASS_NAME:
				count += inf[ 4 ]
		
		return count
	
	def getBefBatchMonsterCount( self, batch ):
		count = 0
		for i in xrange( batch ):
			count += self.getBatchMonsterCount( i + 1 )
		
		return count
	
	def getBefBatchBossCount( self, batch ):
		count = 0
		for i in xrange( batch ):
			count += self.getBatchBossCount( i + 1 )
		
		return count
	
	def isKillAllBefMonster( self, batch, mNum, bNum ):
		# mNum : 还剩多少个怪物， bNum：还剩几个BOSS
		bmNum = self.getBefBatchMonsterCount( batch )
		bbNum = self.getBefBatchBossCount( batch )
		if ( self.getMonsterCount() - bmNum ) >= mNum and ( self.getBossCount() - bbNum ) >= bNum:
			return True
			
		return False
		
	def initData( self ):
		for cof in g_config:
			batch = cof[ "batch" ]
			classInf = cof[ "class_name" ].split( ";" )
			posInf = cof[ "spawn_point" ].split( ";" )
			directInf = cof[ "spawn_direction" ].split( ";" )
			delayTimeInf = cof[ "delay_time" ].split( ";" )
			spCountInf = cof[ "spawn_count" ].split( ";" )
			posRandomInf = cof[ "pos_random" ].split( ";" )
			if cof[ "kill_all_next" ]:
				self.mustKillAllBath.append( batch )
				
			spawnInfo = []
			for i in xrange( len( classInf ) ):
				count = int( spCountInf[i] )
				direction = eval( directInf[i] )
				posRandom = int( posRandomInf[i] )
				if direction == 0:
					direction = ( 0, 0, 0 )
				sInf = ( classInf[i], Math.Vector3( eval( posInf[i] ) ), direction, int( delayTimeInf[i] ), count, posRandom )
				spawnInfo.append( sInf )
				if classInf[i] not in NOT_CALC_CLASS_NAME:
					if classInf[i] in BOSS_CLASS_NAME:
						self.bossCount += count
					else:
						self.monsterCount += count

			self.data[ batch ] = spawnInfo
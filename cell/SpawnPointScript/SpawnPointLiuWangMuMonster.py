# -*- coding: gb18030 -*-

import BigWorld
from bwdebug import *
from SpawnPointNormalActivity import SpawnPointNormalActivity
from TimeString import TimeString
import random
import csdefine
import csconst
import Const

class SpawnPointLiuWangMuMonster( SpawnPointNormalActivity ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		selfEntity.setTemp( 'activityManagerKey', "LiuWangMuMgr" )
		selfEntity.setTemp( 'monsterClassNames', [selfEntity.entityName] )
		SpawnPointNormalActivity.initEntity( self, selfEntity )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		# С��0�򲻸���
		if selfEntity.rediviousTime < 0:
			return
			
		selfEntity.currentRedivious += 1
		if not selfEntity.rediviousTimer:
			#�Լ����ڲ�������������ŵĲ���һ��Ϊ1ʱ���ŻḴ��
			if selfEntity.queryTemp( "floorNum" ) == BigWorld.globalData["AS_LiuWangMu"] == 1:
				selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		��ȡҪ������entity����
		"""
		args = SpawnPointNormalActivity.getEntityArgs( self, selfEntity, params )
		
		args[ "className" ] = ""
		monsterType = selfEntity.queryTemp( "monsterType", 0 )
		spawnTime = selfEntity.queryTemp( "spawnTime", 0 )
		if monsterType and TimeString( spawnTime ).timeCheck() or not monsterType:#ˢ��boss
			args[ "className" ] = selfEntity.entityName
		
		return args
	
	def _createEntity( self, selfEntity, args, num ):
		"""
		virtual method.
		��������
		"""
		if args[ "className" ] == "":
			return []
		
		return SpawnPointNormalActivity._createEntity( self, selfEntity, args, num )
	
	def onBaseGotCell( self, selfEntity ):
		"""
		��base�ص�������֪ͨspawn point��base�Ѿ������cell��֪ͨ
		"""
		selfEntity.addTimer( 0.5, 0, Const.SPAWN_ON_SERVER_START  )
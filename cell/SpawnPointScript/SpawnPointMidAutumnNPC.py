# -*- coding: gb18030 -*-

import BigWorld
import csdefine
import csconst
import random
from bwdebug import *
from SpawnPointCopy import SpawnPointCopy
from ObjectScripts.GameObjectFactory import g_objFactory

class SpawnPointMidAutumnNPC( SpawnPointCopy ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopy.initEntity( self, selfEntity )
		BigWorld.globalData["ActivityBroadcastMgr"].registeSpawnPoint( "midAutumn_quest_start", selfEntity.base )
		BigWorld.globalData["ActivityBroadcastMgr"].registeSpawnPoint( "midAutumn_quest_end", selfEntity.base )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		��������֪ͨ
		"""
		pass

	def startSpawn( self ):
		"""
		define method
		ˢ�¹���
		"""
		self.createEntity( )

	def stopSpawn( self ):
		"""
		define method
		"""
		npc = BigWorld.entities.get( selfEntity.queryTemp("autumnNPCID", 0 ) )
		if npc:
			npc.destroy()

	def createEntity( self, selfEntity, params = {} ):
		"""
		"""
		args = self.getEntityArgs( selfEntity, params )
		entity = self._createEntity( selfEntity, args, 1 )[0] # ֻ����һ��
		
		selfEntity.setTemp( "autumnNPCID", entity.id )
		selfEntity.addTimer( 1, 0, 12224 )

	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if userData == 12224:
			"""
			����ͬ�������NPC �� ����ʦ�������ݵ�����������
			ֻ���ھ����������һЩ���⹦�ܸı�ԭ����Ϸ���������ܴ��롣
			"""
			if selfEntity.queryTemp( "TongJunShi_id", 0 ) == 0:
				for i in self.entitiesInRangeExt( 200, "TongJunShi", selfEntity.position ):
					if i.id == selfEntity.queryTemp( "autumnNPCID", 0 ):
						continue
					selfEntity.setTemp( "TongJunShi_id", i.id )
			tongJunShi = BigWorld.entities.get( selfEntity.queryTemp( "TongJunShi_id", 0 ) )
			autumnNPC = BigWorld.entities.get( selfEntity.queryTemp( "autumnNPCID", 0 ) )
			if tongJunShi and tongJunShi.isReal() and autumnNPC and autumnNPC.isReal():
				autumnNPC.buildQuestOpen = tongJunShi.buildQuestOpen
				autumnNPC.ownTongDBID = tongJunShi.ownTongDBID
			if autumnNPC:
				selfEntity.addTimer( 1, 0, 12224 )
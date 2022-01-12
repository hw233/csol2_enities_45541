# -*- coding: gb18030 -*-

# $Id: SpawnPoint.py,v 1.25 2008-07-18 00:58:22 phw Exp $
"""
"""

import BigWorld
from bwdebug import *
import csdefine
import csconst
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory
import random

TWENTY_MINUTE = 1200 

STOP_FINISH_TEST = 1

class SpawnPointFinishPoint( SpawnPoint ):
	"""
	根据与策划的沟通,怪物死亡时一次性复活,即第一个怪物死亡后开始计时,计时结束时后面有怪物死亡时一次性复活.
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		selfEntity.addProximityExt( self.initiativeRange )
		selfEntity.addTimer(  TWENTY_MINUTE, 0, STOP_FINISH_TEST )
		selfEntity.stopFinishTest = False

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		pass

	def createEntity( self, selfEntity, params = {} ):
		"""
		spawn point出生时自动初始化所有的怪物； 
		
		注意：以下代码不能直接放在initEntity()的时候执行，由于底层可能有bug的原因，在某些情况下selfEntity.position的值不正确，这样会导致出生的怪物无法移动且无法被杀死。
		phw.2008-02-19: 经测试，即使使用延迟，仍然会出现这样的问题
		phw.2008-07-17: 改为当base收到onGetCell()消息后再通知cell的onBaseGotCell()消息，以求能解决此问题
		"""
		#d = { "spawnPos" : selfEntity.position, "spawnMB" : selfEntity.base }
		pass
		

	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if userData == STOP_FINISH_TEST:
			selfEntity.stopFinishTest = True


	def onEnterTrapExt( self,selfEntity, entity, range, controllerID ):
		"""
		"""
		if selfEntity.stopFinishTest:
			return
		if len(entity.queryTemp( "pointIDs", [] )) >= self.pointsCount:
			entity.finishRacehorse()
		
		entity.setTemp("pointIDs", [] )
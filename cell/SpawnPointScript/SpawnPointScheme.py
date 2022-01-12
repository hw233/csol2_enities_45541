# -*- coding: gb18030 -*-
# 可通过活动日程控制的刷新点 by 姜毅 17:32 2010-10-13

import Const
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory
from SpawnPoint import SpawnPoint

class SpawnPointScheme( SpawnPoint ):
	"""
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPoint.initEntity( self, selfEntity  )
		
	def createEntity( self, selfEntity, params = {} ):
		"""
		spawn point出生时自动初始化所有的怪物；
		
		注意：以下代码不能直接放在initEntity()的时候执行，由于底层可能有bug的原因，在某些情况下selfEntity.position的值不正确，这样会导致出生的怪物无法移动且无法被杀死。
		phw.2008-02-19: 经测试，即使使用延迟，仍然会出现这样的问题
		phw.2008-07-17: 改为当base收到onGetCell()消息后再通知cell的onBaseGotCell()消息，以求能解决此问题
		"""
		selfEntity.base.registeToScheme()
		if not self.isCanSpawn( selfEntity ):
			return
		self.rediviousEntity( selfEntity, params )
		
	def rediviousEntity( self, selfEntity, params = {} ):
		"""
		复活所有已死亡的怪物
		"""
		if not self.isCanSpawn( selfEntity ):
			return
			
		SpawnPoint.rediviousEntity( self, selfEntity )
		
	def startSpawn( self, selfEntity ):
		"""
		define method
		开始刷新entity/刷新出entity
		"""	
		selfEntity.setTemp( "canSpawn", True )
		selfEntity.currentRedivious = 1
		self.createEntity( selfEntity )
		
	def stopSpawn( self, selfEntity ):
		"""
		define method
		停止刷新entity/销毁所刷新出来的entity
		"""
		selfEntity.setTemp( "canSpawn", False )
		if len( self.createdEntityIDs ) <= 0:
			return
		entities = self.entitiesInRangeExt( selfEntity.randomWalkRange )
		for e in entities:
			if not e.id in self.createdEntityIDs:
				continue
			if e.isReal():
				e.destroy()
			else:
				e.remoteCall( "destroy",[] )
		self.createdEntityIDs = []
	
	def isCanSpawn( self, selfEntity ):
		return selfEntity.queryTemp( "canSpawn", False )
	
	def onBaseGotCell( self, selfEntity ):
		"""
		初始化的时间不刷怪
		"""
		pass
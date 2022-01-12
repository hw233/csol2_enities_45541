# -*- coding: gb18030 -*-
import BigWorld
from bwdebug import *
import csdefine
import csconst
from SpawnPoint import SpawnPoint
from ObjectScripts.GameObjectFactory import g_objFactory
import random

class SpawnPointDoor( SpawnPoint ):
	"""
	门的出生点
	"""
	def initEntity( self, selfEntity ):
		SpawnPoint.initEntity( self, selfEntity  )
		
		#selfEntity.getCurrentSpaceBase().addSpawnPointCopy( selfEntity.base, selfEntity.entityName )
		#去掉这一句，反正现在都是SpawnPoint中onBaseGotCell时就会刷出门了。门就不需要加到刷新点列表去了。不然反而会造成某些副本报错

	def createEntity( self, selfEntity, params = {} ):
		"""
		spawn point出生时自动初始化所有的怪物；
		
		注意：以下代码不能直接放在initEntity()的时候执行，由于底层可能有bug的原因，在某些情况下selfEntity.position的值不正确，这样会导致出生的怪物无法移动且无法被杀死。
		phw.2008-02-19: 经测试，即使使用延迟，仍然会出现这样的问题
		phw.2008-07-17: 改为当base收到onGetCell()消息后再通知cell的onBaseGotCell()消息，以求能解决此问题
		"""
		args = self.getEntityArgs( selfEntity, params )
		entity = self._createEntity( selfEntity, args, 1 )[0] # 只创建一个
		selfEntity.setTemp( "spawnEntityID", entity.id )

	def openDoor( self, selfEntity, switchAct = True ):
		"""
		开门
		"""
		door = BigWorld.entities.get( selfEntity.queryTemp( "spawnEntityID", 0 ) )
		if door:
			if switchAct:
				door.isOpen = True if not door.isOpen else False
				return

			door.isOpen = True
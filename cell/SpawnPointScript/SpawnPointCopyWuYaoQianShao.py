# -*- coding: gb18030 -*-

"""
副本中怪物出生点类型，服务器启动后不需要直接创建怪物，怪物死亡后需要复活，复活类型写死了，把出生怪物id通知给所在的space
"""

import BigWorld
from bwdebug import *
from ObjectScripts.GameObjectFactory import g_objFactory
from SpawnPointCopyYeWai import SpawnPointCopyYeWai
import Math

GUI_YING_SHI		= "20322020"
FU_HUO_GUI_YING_SHI = "20322022"

class SpawnPointCopyWuYaoQianShao( SpawnPointCopyYeWai ):
	"""
	副本中怪物出生点类型，把出生怪物id通知给所在的space
	"""
	def initEntity( self, selfEntity ):
		"""
		"""
		SpawnPointCopyYeWai.initEntity( self, selfEntity )

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		pass

	def wuyaoqiangshao_entityDead( self, selfEntity, currentPosition, currentDirection ):
		"""
		Define method.
		怪物死亡通知
		"""
		self.setTemp( "currentPosition", tuple( currentPosition ) )
		self.setTemp( "currentDirection", tuple( currentDirection ) )
		
		# 找到副本实例
		if BigWorld.cellAppData.has_key( "spaceID.%i" % selfEntity.spaceID ):	# 防止，副本destroy后，怪物复活
			spaceBase = BigWorld.cellAppData["spaceID.%i" % selfEntity.spaceID]
			try:
				spaceEntity = BigWorld.entities[ spaceBase.id ]
			except:
				DEBUG_MSG( "not find the spaceEntity!" )

			if spaceEntity.isNotRevive:		# 如果副本不再出生怪物
				return

			selfEntity.currentRedivious += 1

			if selfEntity.entityName == GUI_YING_SHI:		# 副本，只让出生怪物为鬼影狮的出生点复活怪物
				if not selfEntity.rediviousTimer:
					selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )

	def createEntity( self, selfEntity, params = {} ):
		"""
		初始化怪物
		"""
		
		# 找到副本实例
		spaceBase = BigWorld.cellAppData["spaceID.%i" % selfEntity.spaceID]
		try:
			spaceEntity = BigWorld.entities[ spaceBase.id ]
		except:
			DEBUG_MSG( "not find the spaceEntity!" )

		# 创建所有的entity
		args = self.getEntityArgs( selfEntity, params )
		for i in xrange( selfEntity.rediviousTotal ):
			entity = g_objFactory.getObject( selfEntity.entityName ).createEntity( selfEntity.spaceID, selfEntity.position, selfEntity.direction, args )
			if params.pop( "isReal", False ):	# 如果这个出生点，出生的怪物是真的鬼影狮
				entity.setTemp( "isReal", True )	# 给鬼影狮加一个标记
				continue	# 真的鬼影狮不需要addSpawnEntityID()
				
			spaceEntity.base.addSpawnEntityID( selfEntity.entityName, entity.id )

	def rediviousEntity( self, selfEntity, params = {} ):
		"""
		virtual method.
		复活所有已死亡的怪物
		"""
		selfEntity.rediviousTimer = 0
		args = self.getEntityArgs( selfEntity, params )

		# 找到副本实例
		spaceBase = BigWorld.cellAppData["spaceID.%i" % selfEntity.spaceID]
		try:
			spaceEntity = BigWorld.entities[ spaceBase.id ]
		except:
			DEBUG_MSG( "not find the spaceEntity!" )
			
		if spaceEntity.isNotRevive:		# 如果副本不再出生怪物
			selfEntity.currentRedivious = 0
			return
		
		currentPosition = self.queryTemp( "currentPosition" )
		currentDirection = self.queryTemp( "currentDirection" )
		args[ "spawnPos" ] = currentPosition
		for i in xrange( selfEntity.currentRedivious ):
			entity = g_objFactory.getObject( FU_HUO_GUI_YING_SHI ).createEntity( selfEntity.spaceID, currentPosition, currentDirection, args)	# 复活鬼影狮
			spaceEntity.base.addSpawnEntityID( FU_HUO_GUI_YING_SHI, entity.id )
			
		selfEntity.currentRedivious = 0
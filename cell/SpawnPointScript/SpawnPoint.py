# -*- coding: gb18030 -*-

# $Id: SpawnPoint.py,v 1.25 2008-07-18 00:58:22 phw Exp $
"""
"""

import BigWorld
from bwdebug import *
import csdefine
import csconst
import Const
from ObjectScripts.GameObjectFactory import g_objFactory
import random
import copy

import Love3

CREATE_ENTITY_TIME 	= 0

class SpawnPoint(object):
	"""
	根据与策划的沟通,怪物死亡时一次性复活,即第一个怪物死亡后开始计时,计时结束时后面有怪物死亡时一次性复活.
	"""
	def __init__( self ):
		object.__init__( self )
		
	def initEntity( self, selfEntity ):
		pass

	def entityDead( self, selfEntity ):
		"""
		Define method.
		怪物死亡通知
		"""
		# 小于0则不复活
		if selfEntity.rediviousTime < 0:
			return
			
		selfEntity.currentRedivious += 1
		if not selfEntity.rediviousTimer:
			selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )

	def createEntity( self, selfEntity, params = {} ):
		"""
		virtual method.
		通知刷出怪物
		"""
		args = self.getEntityArgs( selfEntity, params )
		self._createEntity( selfEntity, args, selfEntity.rediviousTotal )
	
	def destroyEntity( self, selfEntity, params ):
		"""
		virtual method.
		通知销毁怪物
		"""
		planesID = params.get( "planesID", 0 )
		destroyList = []
		if planesID:
			destroyList = selfEntity.spawnRecord.get( planesID )
		else:
			destroyList = selfEntity.spawnRecord.getAll()
		
		for eid in destroyList:
			if BigWorld.entities.has_key( eid ):
				Love3.callEntityMedthod( eid, "destroy", () ) #由于不知道当前spawnPoint是否能取得到刷出entity，所以调用了此方法
	
	def rediviousEntity( self, selfEntity, params = {} ):
		"""
		virtual method.
		复活所有已死亡的怪物
		"""
		selfEntity.rediviousTimer = 0
		args = self.getEntityArgs( selfEntity, params )
		self._createEntity( selfEntity, args, selfEntity.currentRedivious )
		selfEntity.currentRedivious = 0
	
	def _createEntity( self, selfEntity, args, num ):
		"""
		virtual method.
		创建怪物
		"""
		creates = []
		className = selfEntity.entityName
		planesID = args.get( "planesID", 0 )
		if args.has_key( "className" ):
			className = args[ "className" ]
		
		position = selfEntity.position
		if args.has_key( "position" ):
			position = args[ "position" ]
			
		direction = selfEntity.direction
		if args.has_key( "direction" ):
			direction = args[ "direction" ]
					
		for i in xrange( num ):
			if g_objFactory.getObject( className ):
				e = selfEntity.createObjectNear( className, position, direction, args )
				creates.append( e )
				selfEntity.spawnRecord.add( planesID, e.id )
			else:
				spaceType = selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
				ERROR_MSG( " %s no such classname: %s entity" % ( spaceType, selfEntity.entityName ) )	# 这个应该永远都不可能到达
			
		return creates
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		获取要创建的entity参数
		"""
		args = {}
		args[ "planesID" ] = params.pop( "planesID", selfEntity.planesID )
		args["spawnMB"] = selfEntity.base
		# 引擎可能有一个bug，如果使用VECTOR3来存储，
		# 在某一时刻，这个被创建出来的entity的spawnPos.z的值会非常大，
		# spawnPos.z == 340282346638528859811704183484516925440.000000
		# 但，这个问题似乎不是必然出现，出现机率却很高，使用tuple来避开这个bug
		args["spawnPos"] = tuple( selfEntity.position )
		args["randomWalkRange"] = selfEntity.randomWalkRange
		if len( selfEntity.patrolPathNode ):
			args["patrolPathNode"] = selfEntity.patrolPathNode
			args["patrolList"] = selfEntity.patrolList
		
		selfEntity.entityParams.update( params )
		args.update( selfEntity.entityParams )
		return args

	def onTimer( self, selfEntity, controllerID, userData ):
		"""
		"""
		if userData == Const.SPAWN_ON_MONSTER_DIED:
			self.rediviousEntity( selfEntity )
		elif userData == Const.SPAWN_ON_SERVER_START:
			self.createEntity( selfEntity, {} )

	def onBaseGotCell( self, selfEntity ):
		"""
		由base回调回来，通知spawn point，base已经获得了cell的通知
		"""
		# 当base获得了onGetCell()回调后再开始怪物的增产生，以求能解决怪物出生时出生点不正确的问题
		# 当前该问题很可能是底层的bug
		if selfEntity.entityName == "":
			spaceType = selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			ERROR_MSG( "space %s: spawn point entity name is Null." % spaceType, selfEntity.position )
			return

		if selfEntity.lineNumber == 0 or selfEntity.lineNumber == selfEntity.getCurrentSpaceLineNumber():
			selfEntity.addTimer( random.random() * CREATE_ENTITY_TIME, 0, Const.SPAWN_ON_SERVER_START  )
	
	def destroySpawnPoint( self, selfEntity ):
		"""
		销毁刷新点
		"""
		selfEntity.destroy()

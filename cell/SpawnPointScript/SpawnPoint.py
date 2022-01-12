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
	������߻��Ĺ�ͨ,��������ʱһ���Ը���,����һ������������ʼ��ʱ,��ʱ����ʱ�����й�������ʱһ���Ը���.
	"""
	def __init__( self ):
		object.__init__( self )
		
	def initEntity( self, selfEntity ):
		pass

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
			selfEntity.rediviousTimer = selfEntity.addTimer( selfEntity.rediviousTime, 0, Const.SPAWN_ON_MONSTER_DIED )

	def createEntity( self, selfEntity, params = {} ):
		"""
		virtual method.
		֪ͨˢ������
		"""
		args = self.getEntityArgs( selfEntity, params )
		self._createEntity( selfEntity, args, selfEntity.rediviousTotal )
	
	def destroyEntity( self, selfEntity, params ):
		"""
		virtual method.
		֪ͨ���ٹ���
		"""
		planesID = params.get( "planesID", 0 )
		destroyList = []
		if planesID:
			destroyList = selfEntity.spawnRecord.get( planesID )
		else:
			destroyList = selfEntity.spawnRecord.getAll()
		
		for eid in destroyList:
			if BigWorld.entities.has_key( eid ):
				Love3.callEntityMedthod( eid, "destroy", () ) #���ڲ�֪����ǰspawnPoint�Ƿ���ȡ�õ�ˢ��entity�����Ե����˴˷���
	
	def rediviousEntity( self, selfEntity, params = {} ):
		"""
		virtual method.
		���������������Ĺ���
		"""
		selfEntity.rediviousTimer = 0
		args = self.getEntityArgs( selfEntity, params )
		self._createEntity( selfEntity, args, selfEntity.currentRedivious )
		selfEntity.currentRedivious = 0
	
	def _createEntity( self, selfEntity, args, num ):
		"""
		virtual method.
		��������
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
				ERROR_MSG( " %s no such classname: %s entity" % ( spaceType, selfEntity.entityName ) )	# ���Ӧ����Զ�������ܵ���
			
		return creates
	
	def getEntityArgs( self, selfEntity, params = {} ):
		"""
		virtual method.
		��ȡҪ������entity����
		"""
		args = {}
		args[ "planesID" ] = params.pop( "planesID", selfEntity.planesID )
		args["spawnMB"] = selfEntity.base
		# ���������һ��bug�����ʹ��VECTOR3���洢��
		# ��ĳһʱ�̣����������������entity��spawnPos.z��ֵ��ǳ���
		# spawnPos.z == 340282346638528859811704183484516925440.000000
		# ������������ƺ����Ǳ�Ȼ���֣����ֻ���ȴ�ܸߣ�ʹ��tuple���ܿ����bug
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
		��base�ص�������֪ͨspawn point��base�Ѿ������cell��֪ͨ
		"""
		# ��base�����onGetCell()�ص����ٿ�ʼ������������������ܽ���������ʱ�����㲻��ȷ������
		# ��ǰ������ܿ����ǵײ��bug
		if selfEntity.entityName == "":
			spaceType = selfEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			ERROR_MSG( "space %s: spawn point entity name is Null." % spaceType, selfEntity.position )
			return

		if selfEntity.lineNumber == 0 or selfEntity.lineNumber == selfEntity.getCurrentSpaceLineNumber():
			selfEntity.addTimer( random.random() * CREATE_ENTITY_TIME, 0, Const.SPAWN_ON_SERVER_START  )
	
	def destroySpawnPoint( self, selfEntity ):
		"""
		����ˢ�µ�
		"""
		selfEntity.destroy()

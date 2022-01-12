# -*- coding: gb18030 -*-

"""
���߶�����Ļ�����
"""

import BigWorld
import math
import Math
import ECBExtend
from bwdebug import *
import csdefine
import csconst
import Const
from Function import distancePosition
from Resource import PatrolMgr
import random
import utils
import csarithmetic
g_patrolMgr = PatrolMgr.PatrolMgr.instance()

VOLATILE_INFO_CLOSED = (BigWorld.VOLATILE_NEVER,) * 4
VOLATILE_INFO_OPENED = (BigWorld.VOLATILE_ALWAYS, BigWorld.VOLATILE_ALWAYS, None, None)

def pointsEqual(v1, v2):
	"""
	���������Ƿ���ͬһλ��

	@param v1: λ��1
	@param v1: VECTOR3
	@param v2: λ��2
	@param v2: VECTOR3
	@return:   �ɹ�/ʧ��
	@rtype:    BOOL
	"""
	return math.fabs(v1[0]-v2[0]) < 0.1 and math.fabs(v1[2]-v2[2]) < 0.1

class AmbulantObject:
	"""
	NPC����
	"""
	def __init__( self ):
		"""
		"""
		# Ĭ�Ϲر����м̳��ڴ����entity������㲥
		self.volatileInfo = VOLATILE_INFO_CLOSED

	# =======================================
	# �ƶ�������ؽӿ�
	# =======================================
	def stopMoving( self ):
		"""
		ֹͣ��ǰ���ƶ���Ϊ

		@return: None
		"""
		if self.movingControlID != 0:
			self.cancel( self.movingControlID )
			self.movingControlID = 0
		self.closeVolatileInfo()
		self.setMovingType( Const.MOVE_TYPE_STOP )
		

	def closeVolatileInfo( self ):
		"""
		virtual method.
		�ر�������Ϣ���͹��ܡ�
		�������ģ��ᱻ��ͬ��entity���ã���ĳЩentity���ܻ���Ҫ�Բ�ͬ
		�ķ�ʽ��ʱ���ر������Ϊ���������ӿ�����������ء�
		"""
		if self.volatileInfo == VOLATILE_INFO_CLOSED:
			return
		if self.hasFlag( csdefine.ENTITY_FLAG_ONLY_FACE_LEFT_OR_RIGHT ):
			return
		if self.hasFlag( csdefine.ENTITY_VOLATILE_ALWAYS_OPEN ) :
			return
		self.volatileInfo = VOLATILE_INFO_CLOSED
		self.planesAllClients( "setFilterLastPosition", ( self.position, ) )

	def openVolatileInfo( self ):
		"""
		virtual method.
		��������Ϣ���͹���
		�������ģ��ᱻ��ͬ��entity���ã���ĳЩentity���ܻ���Ҫ�Բ�ͬ
		�ķ�ʽ��ʱ���ر������Ϊ���������ӿ�����������ء�
		"""
		if self.volatileInfo == VOLATILE_INFO_OPENED:
			return
		if self.hasFlag( csdefine.ENTITY_VOLATILE_ALWAYS_CLOSE ):
			return
		self.volatileInfo = VOLATILE_INFO_OPENED
		self.planesAllClients( "restartFilterMoving", () )

	def doRandomRun( self, centerPos, radius ):
		"""
		�ߵ�centerPosΪԭ�㣬radiusΪ�뾶�����������
		@param  centerPos: ԭ��
		@type   centerPos: Vector3
		@param  radius:    �뾶
		@type   radius:    FLOAT
		"""
		initRad = 2*math.pi * random.random()		# �漴ѡȡһ����ʼ�Ƕ�
		for tryNum in xrange( 0, 8 ): #��ԭ����30�θ�Ϊ8��,��Բ����ѡȡ�˸���
			rad = initRad + tryNum * 45.0
			pos = Math.Vector3( centerPos )
			distance = radius * random.random()
			if distance < 2: 					# ��֤������׷��Ŀ��ľ����������
				distance = 2
			pos.x += distance * math.sin( rad )
			pos.z += distance * math.cos( rad )
			if self.gotoPosition(pos):
				return True

		return False

	def resetMoving( self ):
		"""
		ֹͣ��ǰ�ƶ���Ϊ�����½����ƶ���
		���entity��ǰû���ƶ�����ôʲô��Ҳ���������򽫻���ݵ�ǰ���ƶ��ٶȵ�����
		"""
		if not self.isMoving(): return
		if self.isMovingType( Const.MOVE_TYPE_DEFAULE ):
			self.gotoPosition( self.queryTemp( "gotoPosition" ), self.queryTemp( "faceTo", True ) )
		elif self.isMovingType( Const.MOVE_TYPE_PATROL ):
			self.doPatrol()
		elif self.isMovingType( Const.MOVE_TYPE_CHASE ):
			entity = BigWorld.entities.get( self.chaseEntityID, None )
			if not entity:
				ERROR_MSG("Chase entity: Monster(%s) but not find the entity(id:%i)!"%(self.className, self.chaseEntityID))
				return
			self.chaseEntity( entity, self.queryTemp( "chaseEntityDist" ) )

	def navigateStepEx_( self, position, velocity, maxDistance, userData, faceToMove ):
		"""
		protected method
		������װ��self.navigateStep()��һЩ�������Լ�����һЩ���ò�����
		�˷������������أ�

		@param    position: (Vector3) The destination point for the Entity to move towards
		@param    velocity: (float) The speed to move the Entity in m/s
		@param maxDistance: (float) Maximum distance to move
		@param    userData: (optional object) Data that can be passed to notification method.
		@return: ControlID��ֵΪ0��ʾʧ��
		@rtype:  INT32
		"""
		try:
			return self.navigateStep( position, velocity, maxDistance, 500.0, faceToMove, 0.5, userData )
		except ValueError, errstr:
			ERROR_MSG( self.getName(), self.className, self.id, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), self.position, position, userData )
			return 0
		except Exception, errstr:
			ERROR_MSG( self.getName(), self.className, self.id, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), self.position, position, userData )
			return 0

	def gotoPosition( self, position, faceTo = True ):
		"""
		�ƶ���һ��λ�ã�
		�˷������������أ�

		�Զ����ƶ��ӿڵĺô�֮һ�ǿ������ƶ���Ϊ����npc��������ƶ��ٶ���ͳһ���У�ʡȥ�������ط�����ʱ�Ķ��⿼�ǡ�
		ͨ���˺����ƶ���������Զ�����onMovedOver()�ص�������
		���ƶ��Ĺ�����ȡ���ƶ������ᴥ��onMovedOver()��

		ע�⣺�˺�����chaseEntity()�Լ������ṩ������ƶ�����һ�����κ�ʱ��ֻ����һ���ƶ����ڣ�

		@param position: Ŀ��λ��
		@type  position: VECTOR3
		@param faceTo: �Ƿ�����
		@type  faceTo: BOOL
		@return: ���ش˴νӿڵ����Ƿ�ɹ�
		@rtype:  BOOL
		"""
		self.stopMoving()
		if self.move_speed <= 0.0:	# �ٶ�̫С�����ƶ�
			return False
		if self._goto_position( position, faceTo ):
			self.openVolatileInfo()
			return True
		else:
			return False

	def _goto_position( self, position, faceTo ):
		"""
		gotoPosition()���ڲ�ʵ�֣�����˵�������gotoPosition()
		�˷������������أ�

		@return: ���ش˴νӿڵ����Ƿ�ɹ�
		@rtype:  BOOL
		"""
		self.setTemp( "gotoPosition", tuple( position ) )
		self.setTemp( "faceTo", faceTo )
		self.movingControlID = self.navigateStepEx_( position, self.move_speed, 0xFF, ECBExtend.GOTO_POSITION_CBID, faceTo )
		if not self.movingControlID:
			return False
		self.setMovingType( Const.MOVE_TYPE_DEFAULE )		# �����ƶ���ָ��λ��״̬��
		return True

	def onMovedFinish( self, controllerId, userData, state ):
		"""
		����gotoPosition()������ECBExtendģ���еĻص�����

		@param state: bool; ��ʶ�Ƿ��ƶ��ɹ�,����1.72��,�ƺ����ǳɹ��ġ������¸����޷��ƶ���Ŀ��λ��
		@param controllerId: �ƶ������Ŀ�����ID
		"""
		#DEBUG_MSG( self.id, controllerId, userData, state )
		if self.movingControlID == 0: return	# �ƺ���������������ܵ��õ�����Ķ�������Ϊ0

		if not state:
			# �ƶ�ʧ�ܣ�û�м����ƶ��ı�Ҫ��
			self.onMovedOver( False )
			return

		t = self.navigateTime
		self.navigateTime = BigWorld.time()
		#DEBUG_MSG( self.id, "moving delay", self.navigateTime - t )
		# ����������ζ�ʱ�����ƶ����ж�ʱ�䳤�����⣬�����ԣ���СҲ��ҪΪ0.1���������գ������Ϊ0.5��Ϊ����Щ��
		# ��ʵ���ֵ����ٶ���̫���ʣ�����ʵ���c++�ײ�Դ˽��з�װ�����޷��ƶ���Ŀ��λ��ʱ�����ƶ�ʧ��״̬��
		if self.navigateTime - t > 0.3:
			self.navigateCount = 0
		else:
			# ��������ڶ�ʱ�����ƶ����¼������������ʧ���ж�
			# ��Ҫ�������ԭ����navigateStep()��navigateFollow()�����޷�����һ���ط�ʱ������False
			self.navigateCount += 1

		if self.navigateCount >= 10:
			# ����ڼ��̵�ʱ����ֹͣ�ƶ���������Ϊ���ƶ�ʧ��
			self.navigateTime = 0.0
			self.onMovedOver( False )
			return

		pos = self.queryTemp( "gotoPosition", None )	# �����۶��ԣ�����ȡֵ������ΪNone������ܿ�����BUG��������ﲻ���ж�
		if pointsEqual( self.position, pos ):
			self.onMovedOver( True )
		else:
			faceTo = self.queryTemp( "faceTo", True )
			if not faceTo:
				y = utils.yawFromPos( pos, self.position  )
				self.direction = ( 0, 0, y )

			if not self._goto_position( pos, faceTo ):
				self.onMovedOver( False )

	def onMovedOver( self, state ):
		"""
		virtual method.
		ʹ��gotoPosition()�ƶ�����ͨ��

		@param state: �ƶ��������ʾ�Ƿ�ɹ�
		@type  state: bool
		@return:      None
		"""
		self.stopMoving()


	def chaseEntity( self, entity, distance ):
		"""
		׷��һ��entity��
		�˷������������أ�

		�Զ����ƶ��ӿڵĺô�֮һ�ǿ������ƶ���Ϊ����npc��������ƶ��ٶ���ͳһ���У�ʡȥ�������ط�����ʱ�Ķ��⿼�ǡ�
		ͨ���˺����ƶ���������Զ�����onChaseOver()�ص�������
		���ƶ��Ĺ�����ȡ���ƶ������ᴥ��onChaseOver()��

		ע�⣺�˺�����gotoEntity()�Լ������ṩ������ƶ�����һ�����κ�ʱ��ֻ����һ���ƶ����ڣ�

		@param   entity: ��׷�ϵ�Ŀ��
		@type    entity: Entity
		@param distance: ��Ŀ��entity��Զ�ľ���ͣ����(��/��)
		@type  distance: FLOAT
		@return: ���ش˴νӿڵ����Ƿ�ɹ�
		@rtype:  BOOL
		"""
		self.stopMoving()     # Ϊ��׷��������
		if self._chase_entity( entity, distance ):
			self.openVolatileInfo()
			return True
		else:
			return False

	def _chase_entity( self, entity, distance ):
		"""
		׷��һ��entity��
		�˷������������أ�

		@return: ���ش˴νӿڵ����Ƿ�ɹ�
		@rtype:  BOOL
		"""
		self.chaseEntityID = entity.id
		self.setTemp( "chaseEntityDist", distance )
		self.movingControlID = self.navigateStepEx_( entity.position, self.move_speed, 1.5, ECBExtend.CHASE_ENTITY_CBID, True )
		if not self.movingControlID:
			return False
		self.setMovingType( Const.MOVE_TYPE_CHASE )		# ����׷��Ŀ����
		return True

	def onChaseFinish( self, controllerId, userData, state ):
		"""
		����chaseEntity()������ECBExtendģ���еĻص�����
		"""
		#DEBUG_MSG( self.id, controllerId, userData, state )
		if self.movingControlID == 0: return	# �ƺ���������������ܵ��õ�����Ķ�������Ϊ0
		chaseEntityID = self.chaseEntityID		# ��Ŀ�� ID ������������Ϊ����� stopMoving �Ὣ׷��Ŀ�� ID �������hyw--08.07.22��

		try:
			entity = BigWorld.entities[chaseEntityID]
		except KeyError:
			entity = None

		if (not state) or (not entity) or (entity.spaceID != self.spaceID):
			# �ƶ�ʧ�ܻ�Ŀ���Ѿ��������ֻ���ͬһ��������û��׷�ٵı�Ҫ��
			self.onChaseOver( entity, False )
			return
		t = self.navigateTime
		self.navigateTime = BigWorld.time()
		#DEBUG_MSG( self.id, "moving delay", self.navigateTime - t )
		if self.navigateTime - t > 0.5:
			self.navigateCount = 0
		else:
			# ��������ڶ�ʱ�����ƶ����¼������������ʧ���ж�
			# ��Ҫ�������ԭ����navigateStep()��navigateFollow()�����޷�����һ���ط�ʱ������False
			self.navigateCount += 1
		if self.navigateCount >= 2:
			# ����ڼ��̵�ʱ����ֹͣ�ƶ���������Ϊ���ƶ�ʧ��
			self.navigateTime = 0.0
			self.onChaseOver( entity, False )
			return

		if self.position.flatDistTo( entity.position ) <= self.queryTemp( "chaseEntityDist", 0.0 ) + 0.3:
			self.onChaseOver( entity, True )
		else:
			if not self._chase_entity( entity, self.queryTemp( "chaseEntityDist", 0.0 ) ):
				self.onChaseOver( entity, False )

	def onChaseOver( self, entity, state ):
		"""
		virtual method.
		ʹ��chaseEntity()�ƶ�����ͨ��

		@param   entity: ��׷�ϵ�Ŀ�꣬����ڽ���ʱĿ���Ҳ�������Ŀ����ʧ�ˣ����ֵΪNone
		@type    entity: Entity
		@param    state: �ƶ��������ʾ�Ƿ�ɹ�
		@type     state: bool
		@return:         None
		"""
		self.stopMoving()

	#-----------------------------------------------------------------------------------------------------
	# Ѳ�����  kb
	#-----------------------------------------------------------------------------------------------------
	def stopPatrol( self ):
		"""
		ֹͣѲ��
		"""
		self.stopMoving()

	def doPatrol( self, patrolPathNode = '', patrolList = None ):
		"""
		virtual method.
		ִ��һ���µ�Ѳ����Ϊ
		@param  patrolPathNode	:  patrolPathNode ��ʼ�����ĵ�
		@type   patrolPathNode	:  string
		@param  patrolList		: PatrolPathʵ��
		@type   patrolList		: PATROL_PATH
		"""
		if self.isMoving():
			if not self.isMovingType( Const.MOVE_TYPE_PATROL ):
				self.stopMoving()
				self.openVolatileInfo()
		else:
			self.openVolatileInfo()

		# ����ⲿ����һ���µ�Ѳ������ ��ô����Ӧ�øı�Ѳ������
		if len( patrolPathNode ) > 0 and patrolList != None:
			self.setTemp( "patrolPathNode", patrolPathNode )
			self.patrolListRecord = patrolList
		else:
			# ���û����ص�Ѳ����Ϣ ��ô�˳�
			patrolPathNode = self.queryTemp( "patrolPathNode", "" )
			patrolList = self.patrolListRecord
			
		if len( patrolPathNode ) <= 0 or patrolList is None:
			if hasattr( self, "playerName" ):
				ERROR_MSG( "patrol is failed! please to check the patrolPathNode and patrolList in config.    playerName: %s, player spaceName: %s." % ( self.playerName, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) ) )
			else:
				ERROR_MSG( "patrol is failed! please to check the patrolPathNode and patrolList in config.    className: %s, monster spaceName: %s." % ( self.className, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) ) )
			
			self.removeTemp( "Patrol_OldNode" )
			self.removeTemp( "Patrol_gotoNode" )
			self.removeTemp( "patrolPathNode" )
			self.patrolListRecord = None
			self.canPatrol = False
			return False
			
		if not patrolList.isReady():
			patrolListID = ""
			patrolListID = patrolList.graphIDAsString()
			if hasattr( self, "playerName" ):
				WARNING_MSG( "patrol list is not ready yet!    playerName: %s, patrolList: %s, player spaceName: %s." % ( self.playerName, patrolListID, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) ) )
			else:
				WARNING_MSG( "patrol list is not ready yet!    className: %s, patrolList: %s, monster spaceName: %s." % ( self.className, patrolListID, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) ) )
			return False

		# �õ���һ�����ӵ�
		patrolInfo = patrolList.nodesTraversableFrom( patrolPathNode )
		patrolCount = len( patrolInfo )

		def gotoPoint( position ):
			try:
				self.setTemp( "patrol_moving_start_time", BigWorld.time() )
				self.movingControlID = self.moveToPoint( position, self.move_speed, ECBExtend.MOVE_TO_PATROL_POINT_FINISH_CB, True, True )
			except ValueError, errstr:
				ERROR_MSG( self.getName(), self.id, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), self.position, position )
				self.canPatrol = False
				return False
			except:
				ERROR_MSG( errstr )
				self.canPatrol = False
				return False
			return True

		
		if patrolCount == 1:
			# ���ֻ��һ�����ӵ� ( ͨ���ǵ������� ����˫�������һ����֧ĩ�˵ķ��ص� )
			self.setTemp( "Patrol_gotoNode", patrolInfo[ 0 ][ 0 ] )
			position = patrolInfo[0][1]
			if abs( position.x ) < 0.000001 and abs( position.y ) < 0.000001 and abs( position.z ) < 0.000001:				# ��һ���������Ϊ0˵��linkTo�ĵ㲻���ڣ���������
				ERROR_MSG( " can not get the next patrol point!    className: %s, monster spaceName: %s, monster position: %s, patrolList: %s,current patrolNode is: %s"%( self.className, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), str(self.position), patrolList.graphIDAsString(), patrolPathNode )  )
				self.canPatrol = False
				return False
			if not gotoPoint( position ):
				ERROR_MSG( " gotoPoint is failed." )
				self.canPatrol = False
				return False
		elif patrolCount >= 2:
			# ����ͨ���Ƕ�������
			patrolInfoList = list( patrolInfo )
			while patrolCount > 0:
				idx = random.randint( 0, patrolCount - 1 )
				if patrolInfoList[ idx ][ 0 ] in [ patrolPathNode, self.queryTemp( "Patrol_OldNode" ) ]:
					patrolInfoList.pop( idx )
					patrolCount -= 1
					continue
				self.setTemp( "Patrol_gotoNode", patrolInfoList[ idx ][ 0 ] )
				position = patrolInfoList[ idx ][ 1 ]
				if abs( position.x ) < 0.000001 and abs( position.y ) < 0.000001 and abs( position.z ) < 0.000001:				# ��һ���������Ϊ0˵��linkTo�ĵ㲻���ڣ���������
					ERROR_MSG( " can not get the next patrol point!    className: %s, monster spaceName: %s, monster position: %s, patrolList: %s,current patrolNode is: %s"%( self.className, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), str(self.position), patrolList.graphIDAsString(), patrolPathNode )  )
					self.canPatrol = False
					return False
				if not gotoPoint( patrolInfoList[ idx ][ 1 ] ):
					ERROR_MSG( " gotoPoint is failed." )
					self.canPatrol = False
					return False
				break
		else:
			INFO_MSG(" arrive last node of patrolList. className: %s, monster spaceName: %s, monster position: %s, patrolList: %s,current patrolNode is: %s"%( self.className, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), str(self.position), patrolList.graphIDAsString(), patrolPathNode )  )
			self.stopMoving()
			return False

		self.setMovingType( Const.MOVE_TYPE_PATROL )		# ����Ѳ����
		self.canPatrol = True
		return True

	def onPatrolToPointFinish( self, controllerId, userData, state ):
		"""
		����doPatrol()������ECBExtendģ���еĻص�����

		@param state: bool; ��ʶ�Ƿ��ƶ��ɹ�,����1.72��,�ƺ����ǳɹ��ġ������¸����޷��ƶ���Ŀ��λ��
		@param controllerId: �ƶ������Ŀ�����ID
		"""
		if state:
			self.setTemp( "Patrol_OldNode", self.queryTemp( "patrolPathNode" ) )
			patrolPathNode = self.queryTemp( "Patrol_gotoNode", "" )
			self.setTemp( "patrolPathNode", patrolPathNode )
			command = g_patrolMgr.getUserString( patrolPathNode )

			if self.onPatrolToPointOver( command ):
				self.doPatrol()
			else:
				self.stopMoving()
		else:
			self.stopMoving()

	def onPatrolToPointOver( self, command ):
		"""
		virtual method.
		����onPatrolToPointFinish()������ECBExtendģ���еĻص�����

		@param command: Ѳ�ߵ�һ�������õ����������
		"""
		if BigWorld.time() - self.queryTemp( "patrol_moving_start_time" )  < 0.01:
			return False
		return True


	#-----------------------------------------------------------------------------------------------------
	# ֱ���˶����,�����˶�������ײ�������ײ
	#-----------------------------------------------------------------------------------------------------
	def lineToPoint( self, dstPos, moveSpeed, faceMovement ):
		"""
		virtual method.
		�˶���ĳ�㣬�����˶�������ײ�������ײ,��entity���յ㲻һ����dstPos��
		@param dstPos			: �˶�Ŀ���
		@type dstPos			: Vector3
		@param faceMovement		: entity�����Ƿ���˶�����һ��
		@type faceMovement		: Bool
		"""
		self.stopMoving()
		self.openVolatileInfo()
		self.setMovingType( Const.MOVE_TYPE_BACK )
		try:
			# moveToPointObstacle_cpp:����ײ���ܵ�moveToPoint��
			# crossHight����Ĭ��0.5��Ϊ��Խ�ϰ��ĸ߶ȣ�distance����Ĭ��0.5����ײ�����ľ���,���������entityǶ����ײ���ڲ���
			#@param destination		The location to which we should move
			#@param velocity			Velocity in metres per second
			#@param crossHight		Ignoring the barrier height,
			#@param distance			Stop once we collide with obstacle within this range,
			#@param faceMovement		Whether or not the entity should face in the
			#							direction of movement.
			#@param moveVertically	Whether or not the entity should move vertically.
			self.movingControlID = self.moveToPointObstacle_cpp( dstPos, moveSpeed, ECBExtend.MOVE_TO_POINT_FINISH_CB, 0.5, 0.5, faceMovement, False )
		except ValueError, errstr:
			ERROR_MSG( self.getName(), self.id, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), self.position, dstPos )
			return False
		return True

	def onLineToPointFinish( self, controllerID, userData, state ):
		"""
		virtual method.
		�ƶ���ĳ��ص�
		"""
		self.stopMoving()

	def moveRadiFollow( self, targetID, angle, distanceRange ):
		"""
		������ε���Ϊ
		
		@param angle: �Ƕ�
		"""
		self.stopMoving()
		target = BigWorld.entities.get( targetID )
		if not target:
			return
		if self.spaceID != target.spaceID:
			return

		self.setTemp("targetPos", target.position)
		radius = angle * math.pi / 180.0
		pos_v =  self.position - target.position
		distance_a = random.uniform( distanceRange[0], distanceRange[1] )

		angle_new = radius + ( pos_v.yaw - target.yaw )
		speed = random.uniform( Const.ROUND_SPEED[0], Const.ROUND_SPEED[1] )

		try:
			self.setMovingType( Const.MOVE_TYPE_ROUND )
			self.openVolatileInfo()
			self.movingControlID = self.navigateFollow( target, angle_new, distance_a, speed, distance_a, distance_a*2,0, 0.5,ECBExtend.MOVE_RADI_FOLLOW_CBID )
			
			cbidTag = self.addTimer( 0.5,0.5,ECBExtend.CHANGE_YAW )
			self.setTemp( "cbidTag",cbidTag )
		except EnvironmentError:
			DEBUG_MSG( "id is %s,className is %s Entity.navigateFollow: No path found" % ( self.id, self.className ) )
		except ValueError:
			DEBUG_MSG("id is %s,className is %s Entity.navigateFollow:target position is %s,angle: %s,distance: %s" % ( self.id, self.className, target.position, angle_new, distance_a ) ) 
		else:
			DEBUG_MSG( "id is %s,className is %s Entity.navigateFollow" % ( self.id, self.className ) )

	def moveTowardsNearOrFarRadiFollow( self, targetID, angle, distanceRange, speedRange, callBackID ):
		"""
		����Ŀ�������Զ���ε���Ϊ
		@param angle: �Ƕ�
		
		�˴���navigateStep��ԭ���У�1��navigateFollow��navigateStep�Ĳ�������һ����Χ��entity�˶���һ����Χ��Ŀ����˶���
		2������self.navigateFollow( target, angle_new, distance_a, speed, distance_a, distance_a*2,0, 0.5,ECBExtend.MOVE_RADI_FOLLOW_CBID )��ͨ������angle_new��ֵ��
		��Ҫ�ﵽԶ���Ч�������־�����ͬһ���Ƕȣ�Ҳ�ᵼ�ºܶ�ʱ��Զ���ˣ�Ȼ���ֿ����ˡ����ܴﵽԶ���Ч����
		Ϊ�˱�֤Զ���ε��Լ������ε���
		"""
		self.stopMoving()
		target = BigWorld.entities.get( targetID )
		if not target:
			return
		if self.spaceID != target.spaceID:
			return

		self.setTemp("targetPos", target.position)
		if callBackID == ECBExtend.MOVE_NEAR_RADI_FOLLOW_CBID:
			direction = self.calDstDirection( target.position, self.position, angle )
			distance_max = min( distanceRange[1], self.distanceBB( target ) )
			distance_a = random.uniform( distanceRange[0], distance_max )
		elif callBackID == ECBExtend.MOVE_FAR_RADI_FOLLOW_CBID:
			direction = self.calDstDirection( self.position, target.position, angle )
			distance_a = random.uniform( distanceRange[0], distanceRange[1] )
		dstPos = Math.Vector3( ( self.position.x + distance_a * direction.x, self.position.y, self.position.z + distance_a * direction.y ) )

		speed = random.uniform( speedRange[0], speedRange[1] )

		try:
			self.setMovingType( Const.MOVE_TYPE_ROUND )
			self.openVolatileInfo()
			#self.movingControlID = self.navigateFollow( target, angle_new, distance_a, speed, distance_a, distance_a*2,0, 0.5,ECBExtend.MOVE_RADI_FOLLOW_CBID )
			if callBackID == ECBExtend.MOVE_NEAR_RADI_FOLLOW_CBID:
				self.movingControlID = self.navigateStep( dstPos, speed, distance_a, distance_a*2,0, 0.5,ECBExtend.MOVE_NEAR_RADI_FOLLOW_CBID )
			elif callBackID == ECBExtend.MOVE_FAR_RADI_FOLLOW_CBID:
				self.movingControlID = self.navigateStep( dstPos, speed, distance_a, distance_a*2,0, 0.5,ECBExtend.MOVE_FAR_RADI_FOLLOW_CBID )
			cbidTag = self.addTimer( 0.5,0.5,ECBExtend.CHANGE_YAW )
			self.setTemp( "cbidTag",cbidTag )
		except EnvironmentError:
			DEBUG_MSG( "id is %s,className is %s Entity.navigateStep: No path found" % ( self.id, self.className ) )

	def onMoveRaidFollowCB( self, controllerId, userData, state ):
		"""
		Monster.navigateFollow�Ļص�����
		"""
		self.stopMoving()
		
	def onMoveNearRaidFollowCB( self, controllerId, userData, state ):
		"""
		Monster.navigateFollow�Ļص�����
		"""
		self.stopMoving()
		AICommandID = self.queryTemp( "NearFollow_AICommandID", 0 )
		if AICommandID:
			self.sendAICommand( self.id, AICommandID )
			
	def onMoveFarRaidFollowCB( self, controllerId, userData, state ):
		"""
		Monster.navigateFollow�Ļص�����
		"""
		self.stopMoving()
		AICommandID = self.queryTemp( "FarFollow_AICommandID", 0 )
		if AICommandID:
			self.sendAICommand( self.id, AICommandID )
		
	def changeYaw( self, controllerId, userData ):
		"""
		û�����Ƶ�ͬ������
		"""
		targetPos = self.queryTemp( "targetPos", self.position )
		yaw = ( targetPos - self.position ).yaw
		self.direction = ( 0, 0, yaw )

	def moveBack( self, targetID, distance ):
		"""
		����һ�ξ���
		"""
		if self.isMoving() and self.isMovingType( Const.MOVE_TYPE_BACK ):		# �����˾Ͳ�����
			return
		target = BigWorld.entities.get( targetID )
		if not target:
			return
		if self.spaceID != target.spaceID:
			return

		direction = Math.Vector3( target.position - self.position )
		if direction.x == 0 and direction.z == 0:
			direction = self.direction
		direction.normalise()
		targetPos = self.position + direction * distance
		speed = random.uniform( Const.BACK_SPEED[0], Const.BACK_SPEED[1]  )
		if random.randint( 1, 10 ) < 4:  # 70%����ִ��run_back,30%��������ƶ���ʱ��ִ����Ծ����
			self.planesAllClients( "jumpBackFC", () )
		self._moveBack( speed, targetPos )
	
	def _moveBack( self, speed, targetPos ):
		"""
		run_back
		"""
		self.lineToPoint( targetPos, speed, False )
		
	def calDstDirection( self, positionX, positionY, angle ):
		"""
		���������Լ�ƫ�Ƶõ����յķ���
		"""
		direction = Math.Vector2( ( positionX.x - positionY.x, positionX.z - positionY.z ) )
		direction.normalise()
		radius = angle * math.pi / 180.0
		sin_angle = math.sin( radius )
		cos_angle = math.cos( radius )
		sin_angle_new = sin_angle * direction.y + cos_angle * direction.x
		cos_angle_new = cos_angle * direction.y - sin_angle * direction.x
		direction = Math.Vector2( sin_angle_new, cos_angle_new )
		return direction

	def isMoving( self ):
		"""
		�ж�entity��ǰ�Ƿ������ƶ���

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.movingControlID != 0


	def setMovingType( self, movingType ):
		"""
		�����ƶ�����
		"""
		self.lastMovingType = self.movingType
		self.movingType = movingType
		self.onMovingTypeChange()


	def isMovingType( self, movingType ):
		"""
		�ж��Ƿ���ĳ���ƶ�����
		"""
		return self.movingType == movingType

	def isLastMovingType( self, lastMovingType ):
		"""
		�ж�֮ǰ���ƶ������Ƿ�ĳ����
		"""
		return self.lastMovingType == lastMovingType


	def onMovingTypeChange( self ):
		"""
		"""
		if self.isMovingType( Const.MOVE_TYPE_STOP ):
			# ��Ѳ�ߵĻ� ��ֹͣѲ��
			if self.isLastMovingType( Const.MOVE_TYPE_PATROL ):
				self.canPatrol = False
	
			# ���ε��Ļ� ��ֹͣ�ε�
			elif self.isLastMovingType( Const.MOVE_TYPE_ROUND ):
				cbidTag = self.popTemp("cbidTag")
				if cbidTag:
					self.cancel( cbidTag )
			elif self.isLastMovingType( Const.MOVE_TYPE_CHASE ):
			 	self.chaseEntityID = 0



	
#--------------------------------------------------------
# ת��
#--------------------------------------------------------
	def rotateToPos( self, position ):
		"""
		ת��һ������
		"""
		disPos = position - self.position
		self.direction = (0,0,disPos.yaw)
		self.planesAllClients( "setFilterYaw", (disPos.yaw,) )
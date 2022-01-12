# -*- coding: gb18030 -*-
#
# $Id: Action.py,v 1.110 2008-08-09 10:10:22 huangdong Exp $

"""
actions manager

2006/10/09 : writen by huangyongwei
2008/12/20 : tidy up by huangyongwei
			 �� ����������������ƶ�״̬�����ƶ�״̬�뷽��ָʾ����һ���Ǵ���ģ�
			 �� �Գ�ʼ���ĳ�Ա��������ע��
"""

import math
import time
import BigWorld
import Math
import Timer
import csstatus
import csstatus_msgs
import csdefine
from Function import Functor
from bwdebug import *
from navigate import NavigateEx
from StraightMoveMotor import StraightMoveMotor
from StraightMoveMotor import STRAIGHT_MOVE_SUCCESS, STRAIGHT_MOVE_CANCEL, STRAIGHT_MOVE_COLLIDE
from gbref import rds
import Const
import csarithmetic

# --------------------------------------------------------------------
# ȫ�ֶ���( tidy up by hyw -- 2008.12.20 )
# ע�⣺���ڷ���ָʾ��ĿǰΪֹ��Ӧ��ֻ��������Щ��
#	    Ҫ���������������ʱ������ϸ˼�����Ƿ��뷽�����
# --------------------------------------------------------------------
# ����ָʾ
DIRECT_NONE			= 0		# û�з���ָʾ	\
DIRECT_FORWARD		= 1		# ��ǰ			|
DIRECT_LEFT			= 2		# ����			 > ����
DIRECT_BACKWARD		= 4		# ���			|
DIRECT_RIGHT		= 8		# ����			/
DIRECT_JUMPUP		= 16	# ���ϣ����� ����> ����

# ��Ϸ���ָʾ
POINT_LEFT			= lambda du : ( du & DIRECT_LEFT ) and not ( du & DIRECT_RIGHT )		# ��������ָʾ
POINT_RIGHT			= lambda du : ( du & DIRECT_RIGHT ) and not ( du & DIRECT_LEFT )		# ��������ָʾ
POINT_FORWARD		= lambda du : ( du & DIRECT_FORWARD ) and not ( du & DIRECT_BACKWARD )	# ������ǰָʾ
POINT_BACKWARD		= lambda du : ( du & DIRECT_BACKWARD ) and not ( du & DIRECT_FORWARD )	# �������ָʾ
POINT_JUMPUP		= lambda du : du & DIRECT_JUMPUP										# ��������ָʾ
POINT_UNQUITS		= lambda du : POINT_LEFT( du ) or POINT_RIGHT( du ) or \
								  POINT_FORWARD( du ) or POINT_BACKWARD( du ) 				# �Ƿ��з���ָʾ( û�з������ )

# -----------------------------------------------------
# ��Ϊ״̬����Щ״̬���Ṳ�棩
ASTATE_CONTROL		= 1		# ��ҿ���״̬
ASTATE_DEST			= 2		# �ƶ���ָ��Ŀ�ĵ�
ASTATE_AUTOFORWARD	= 3		# �Զ�����״̬
ASTATE_NAVIGATE		= 4		# �Զ�Ѱ·״̬
ASTATE_FOLLOW		= 5		# ����״̬
ASTATE_PURSUE		= 6		# ׷��Ŀ��״̬


# --------------------------------------------------------------------
# implement Action class
# --------------------------------------------------------------------
class Action :
	def __init__( self ) :
		self.__speed = 0									# �ƶ��ٶ�
		self.__directUnion = DIRECT_NONE					# �������
		self.__actionState = ASTATE_CONTROL					# ���

		self.__navigator = NavigateEx( self )
		self.__turnaroundTimerID = 0						# ת���� timer ID
		self.__velocityCBID = 0
		self.__guideCBID = 0								# ָ��timer

		self._straightMoveMotor = StraightMoveMotor()
		self.modeList_ = []

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onStraightMoveCallback( self, callback, destination, result ):
		"""ֱ���ƶ���Ŀ��λ�ûص�"""
		if result == STRAIGHT_MOVE_SUCCESS:
			if callable( callback ):
				callback( True )
		elif result == STRAIGHT_MOVE_CANCEL:
			if callable( callback ):
				callback( False )
		elif result == STRAIGHT_MOVE_COLLIDE:
			self.navigateTo(destination, Functor(self.__onNavigateCallback, callback))

	def __onNavigateCallback( self, callback, isSuccess ) :
		"""
		Ѱ·�ƶ���ָ����ص�
		"""
		self.stopMove( )
		if type(callback) == type((2,)):#tuple
			callback = callback[0]
		if callable( callback ) :
			callback( isSuccess )

	def __onStraightChaseCallback( self, callback, nearby, chaser, target, result ):
		"""����ֱ��׷��Ŀ�귽ʽ�Ļص�"""
		if result == STRAIGHT_MOVE_SUCCESS:
			if callable( callback ):
				callback( chaser, target, True )
		elif result == STRAIGHT_MOVE_CANCEL:
			if callable( callback ):
				callback( chaser, target, False )
		elif result == STRAIGHT_MOVE_COLLIDE:
			self.navigatePursue(target, nearby, callback)

	def __autoRunCallback( self, callback, isSuccess ):
		"""
		����Ѱ·�Ļص�����
		@type		callback:  Functor
		@param		callback:  �ص�����
		@type		isSuccess: bool
		@param		isSuccess: �Ƿ�ִ�Ŀ�ĵ�
		"""
		self.stopMove()
		self.endAutoRun( isSuccess )
		if callable( callback ) :
			callback( isSuccess )

	def __onTurnaroundOver( self, old_param, callback ) :
		"""
		ת������ص�
		@param 		old_param : see also method turnaround() in old_param = ......
		@param   	callback  : callback specifies turnaround over��it must contain an argument, PlayerRole will be passed as the callback argument
		@return				  : None
		"""
		physics = self.getPhysics()
		self.__turnaroundTimerID = 0
		# rever to the old coefficients
		self.am.turnModelToEntity = old_param[0]
		physics.dcLocked = old_param[1]
		physics.targetSource = None
		physics.targetDest = None
		if callback is not None :										# callback--if it is not None
			callback( self )

	def __velocityDetect( self, sourcePos, dstPos, dist, callback, tickCallback ) :
		"""
		velocity ���
		"""
		currPos = self.position
		p1 = currPos - sourcePos
		p2 = dstPos - currPos
		if callable( tickCallback ) :
			tickCallback( self.position )
		if p1.x * p2.x < 0 or p1.y * p2.y < 0 or p1.z * p2.z < 0 or \
			currPos.distTo( dstPos ) < dist :
				callback( True )
		elif time.time() > self.__endVelecotyTime :
			callback( False )
		else :
			func = Functor( self.__velocityDetect, sourcePos, dstPos, dist, callback, tickCallback )
			BigWorld.cancelCallback( self.__velocityCBID )
			self.__velocityCBID = BigWorld.callback( 0.1, func )

	# -------------------------------------------------
	def __calcYaw( self ) :
		"""
		���ݵ�ǰ�������ָʾ�������������ɫ����
		"""
		yaw = 0
		if self.__directUnion & DIRECT_LEFT :
			yaw -= math.pi * 0.5
		if self.__directUnion & DIRECT_RIGHT :
			yaw += math.pi * 0.5
		if self.__directUnion & DIRECT_FORWARD :
			yaw = yaw * 0.5
		if self.__directUnion & DIRECT_BACKWARD :
			yaw = math.pi - yaw * 0.5
		return BigWorld.camera().direction.yaw + yaw


	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onCameraDirChanged( self, direction ) :
		"""
		���������ı�ʱ������
		������ʵ�֣�ʹ�ü����ƶ������У���ɫ�߶��ķ���ʼ����Ծ�ͷ�������
		"""
		if self.isMoving() and ( self.isActionState( ASTATE_CONTROL ) or self.isActionState( ASTATE_AUTOFORWARD ) ):
			BigWorld.dcursor().yaw = self.__calcYaw()

	# -------------------------------------------------
	def onBeforeAutoRun( self ):
		"""
		�Զ�Ѱ·֮ǰ��������
		"""
		pass

	def startAutoRun( self, position ):
		"""
		��ʼ�Զ�Ѱ·�������Զ�Ѱ·״̬������һЩ����
		@type    position: Vector3
		@param   position: �Զ�Ѱ·��
		"""
		self.setActionState( ASTATE_NAVIGATE )
		self.onStartAutoRun( position )

	def onStartAutoRun( self, position ):
		"""
		�Զ�Ѱ·���������顣
		"""
		pass

	def endAutoRun( self, state ) :
		"""
		�Զ�Ѱ·�Ƿ񵽴�Ŀ�ĵصĻص�֪ͨ�������ڴ���һЩ����
		@type    state: bool
		@param   state: �Ƿ�ɹ�����Ŀ�ĵ�
		wsf ���� 11:39 2008-7-25
		"""
		# �����Զ�Ѱ·״̬
		self.setActionState( ASTATE_CONTROL )
		self.onEndAutoRun( state )

	def onEndAutoRun( self, state ):
		"""
		��������������
		virtual Method
		"""
		pass

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSpeed( self ) :
		"""
		��ȡ�ƶ��ٶ�
		"""
		return self.__speed

	def setSpeed( self, speed ) :
		"""
		�����ƶ��ٶ�
		@type			speed  : float
		@param			speed  : �ٶ�ֵ
		"""
		self.__speed = speed
		if self.isMoving() :
			self.updateVelocity()

	def getPhysics( self ):
		"""
		��ȡ Entity �� physics
		"""
		if hasattr( self, "physics" ):
			return self.physics
		return None

	# -------------------------------------------------
	def updateDirection( self, flag, isset ) :
		"""
		���·�����
		@type			flag  : MACRO DEFINATION
		@param			flag  : ������: DIRECT_*
		@type			isset : bool
		@param			isset : ָ��������ָ����ǻ������ָ����ǣ�Ϊ True ���趨����֮�����
		"""
		if isset :
			self.__directUnion |= flag
			if POINT_UNQUITS( self.__directUnion ) :		# ����������ƶ���ǣ�������ָʾ�������������Ϊ������������Զ���ǰ�ߣ�ͻȻ�����˷�����̣���Ҫֹͣ���Զ����ߣ�
				self.__actionState = ASTATE_CONTROL			# �����ܿ�״̬
				self.__directUnion &= ~DIRECT_JUMPUP		# ȡ����Ծ��ǣ�ע��������ȡ����Ծ���ʵ�����ǲ�����ģ�
															# �����������Է�ֹ��Ծ�󣬱����ʱ���ᱻ��������⣬
															# ���ң���Ծ����� entity ��������Ͳ��������ˣ����ֻҪ�����ˣ����ǾͿ��������
		else :
			self.__directUnion &= ~flag						# ���ָ��������

	def testDirection( self, flag ) :
		"""
		��⵱ǰ�Ƿ���ָ��������
		@type			flag : MACRO DEFINATION
		@param			flag : ������: DIRECT_*
		"""
		return self.__directUnion & flag == flag

	def emptyDirection( self ) :
		"""
		�������ǣ��� resumeAction ����Ϊ emptyDirection��
		"""
		self.__directUnion = DIRECT_NONE

	# ---------------------------------------
	def setActionState( self, state ) :
		"""
		������Ϊ״̬
		"""
		self.__actionState = state
		if state != ASTATE_CONTROL :
			self.emptyDirection()

	def isActionState( self, state ) :
		"""
		ָ��ĳ�ƶ���־�Ƿ�����
		"""
		return self.__actionState == state

	# -------------------------------------------------
	def flushAction( self ) :
		"""
		������Ϊ״̬���ƶ���ͼ���򣬸�����Ϊ������ֹͣ��ĳ�������ƶ���
		"""
		if not self.allowMove() : return							# ����������ƶ����򷵻�
		if self.__actionState != ASTATE_CONTROL : return			# ��������Զ��ƶ�״̬�����ƶ����ܷ���Ӱ��
		if POINT_UNQUITS( self.__directUnion ) :					# �Ƿ�����Ϻ�ķ�������������Ϸ��򣬻��򲻵�����
			BigWorld.dcursor().yaw = self.__calcYaw()	# �򣬸��Ľ�ɫ����Ϊָʾ����
			self.startMove() # �ý�ɫ�ƶ�
		else:						# ����
			self.stopMove( True )				# ֹͣ�ƶ�״̬

	def flushActionByKeyEvent( self ):
		"""
		���ݼ�����Ϣ��������Ϊ��������Ծ���ݲ�����
		"""
		scAhead = rds.shortcutMgr.getShortcutInfo( "ACTION_FORWARD" ).key
		scBack = rds.shortcutMgr.getShortcutInfo( "ACTION_BACKWORD" ).key
		scLTurn = rds.shortcutMgr.getShortcutInfo( "ACTION_TURN_LEFT" ).key
		scRTurn = rds.shortcutMgr.getShortcutInfo( "ACTION_TURN_RIGHT" ).key

		keyList = [
			( scAhead, DIRECT_FORWARD ),		# move forward
			( scBack, DIRECT_BACKWARD ),		# move backward
			( scLTurn, DIRECT_LEFT ),			# move leftward
			( scRTurn, DIRECT_RIGHT ),			# move rightward
			]

		for key, flag in keyList:
			isDown = BigWorld.isKeyDown( key )
			self.updateDirection( flag, isDown )
		self.flushAction()

	def updateVelocity( self ) :
		"""
		������ɫ velocity
		"""
		physics = self.getPhysics()
		if self.isBlowUp:return
		if not self.isPursueState( ) :
			physics.brake = 0
		if hasattr( self, "getJumpState" ) and self.getJumpState() != Const.STATE_JUMP_DEFAULT:
			physics.velocity = ( physics.velocity[0], physics.velocity[1], self.__speed )
		elif self.moveDirection:
			powVector = Math.Vector3( self.moveDirection[0], 0, self.moveDirection[1] )
			yaw = powVector.yaw - self.yaw
			speedX = self.moveDirection[2] * math.cos(yaw)
			speedY = self.moveDirection[2] * math.sin(yaw)
			physics.velocity = ( speedY, 0.0, self.__speed + speedX )
		else:
			physics.velocity = ( 0.0, 0.0, self.__speed )

	# -------------------------------------------------
	def allowMove( self ):
		"""
		�ж��Լ��Ƿ����ƶ���������д
		"""
		return True

	def isMoving( self ):
		"""
		ָ����ɫ��ǰ�Ƿ����ƶ�״̬
		"""
		physics = self.getPhysics()
		return physics and physics.moving and Math.Vector3( physics.velocity ) != Math.Vector3( 0, 0, 0 )

	def startMove( self ):
		"""
		�Խ�ɫ��ǰ�ĳ�����ǰ�ƶ�
		"""
		self.stopMove(True)
		self.updateVelocity()
		if self.modeList_ or self.canShowGuideModel() or self.fubenGuideModel:
			self.__guideCBID = Timer.addTimer( Const.AUTO_RUN_TIME_TICK, Const.AUTO_RUN_TIME_TICK, self.guideModelDetect_ )

	def stopMove( self, isControl = False) :
		"""
		ֹͣ�ƶ�
		"""
		physics = self.getPhysics()
		if physics == None:
			return
		if self._straightMoveMotor.running():
			self._straightMoveMotor.stop()
		elif self.__navigator.isRunning():
			self.__navigator.forceStop()
		elif physics.seeking:									# ������� seeking����֮ͣ
			physics.setSeekCallBackFn( None )
			physics.seek( None, 0, 0, None )
		#�������Ծ״̬�������ٶ�
		if hasattr( self, "getJumpState" ) and self.getJumpState() != Const.STATE_JUMP_DEFAULT:
			physics.velocity = ( 0, physics.velocity[1], 0 )
		else:
			physics.stop()
		Timer.cancel( self.__guideCBID )
		self.__guideCBID = 0

	def stopVelocity( self ) :
		"""
		ֹͣ���
		"""
		BigWorld.cancelCallback( self.__velocityCBID )
		self.getPhysics().stop()

	# -------------------------------------------------
	def seek( self, position, verticalRange, callback, isSeekToGoal = True, isFacetoPos = True ) :
		"""
		�ƶ���ָ��λ�ã������Զ����Խ�ϰ��߶�
		@type 			position	  : Vector3
		@param			position	  : Ŀ��λ��
		@type			verticalRange : float
		@param			verticalRange : �ϰ��߶�
		@type			callback	  : functor
		@param			callback	  : seek �����ص�
		@type			isSeekToGoal  : bool
		@param 			isSeekToGoal  : �Ƿ�ǿ�Ƶ���ָ��λ�ã� ΪFalseʱ������ƽ�����崦��
		"""
		x, y, z = position
		decVector = position - self.position
		distance = decVector.length
		timeout = 0
		if self.__speed != 0 :
			timeout = 1.5* distance / self.__speed
		else :
			DEBUG_MSG( "you can't move, your speed value is zero!" )
		if isFacetoPos and ( not self.effect_state & csdefine.EFFECT_STATE_BE_HOMING ):
			destination = ( x, y, z, decVector.yaw )
		else:
			destination = ( x, y, z, self.yaw )
		self.getPhysics().seek( destination, timeout, verticalRange, callback, isSeekToGoal )
		if not self.effect_state & csdefine.EFFECT_STATE_BE_HOMING:
			BigWorld.dcursor().yaw = decVector.yaw

	def onNavigateExNoPathFind( self, navExState ):
		"""
		Ѱ·״̬��,��û���ҵ�·��ʱ,�ص��ú���
		@type		navExState: NAV_STATE @see navigate.py in NavigateEx class
		@param		navExState: Ѱ·��״̬
		"""
		#ToDo��������ʾѰ·ʧ�ܵ������Ϣ
		if navExState == NavigateEx.NAV_STATE_MCTRL:
			BigWorld.player().statusMessage( csstatus.AUTO_RUN_CAN_NOT_FIND_PATH )
		elif navExState == NavigateEx.NAV_STATE_SDEST:
			BigWorld.player().statusMessage( csstatus.AUTO_RUN_CAN_NOT_FIND_PATH )
		elif navExState == NavigateEx.NAV_STATE_LDEST:
			BigWorld.player().statusMessage( csstatus.AUTO_RUN_NOT_IN_RIGHT_SPACE )
		elif navExState == NavigateEx.NAV_STATE_TRAP:
			BigWorld.player().statusMessage( csstatus.AUTO_RUN_CURRENT_POS_CAN_NOT_MOVE )
		#elif navExState == self.__navigator.NAV_STATE_PURSUE:
		#	do something here

	def moveTo( self, position, callback = None ) :
		"""
		�ƶ���ָ��λ��
		@type			RETURN: bool
		@param			RETURN: Ŀ�ĵ��Ƿ���Եִ�
		@type			position	  : Vector3
		@param			position	  : Ŀ��λ��
		@type			callback	  : functor / method with one parameter
		@param			callback	  : �ƶ������ص�
		"""
		if self.moveStraightTo(position, Functor(self.__onStraightMoveCallback, callback, position)):
			return True
		else:
			return self.navigateTo(position, Functor(self.__onNavigateCallback, callback))

	def moveStraightTo( self, position, callback = None ):
		"""
		Ѱ·�ƶ���ָ��λ��
		@type			RETURN: bool
		@param			RETURN: Ŀ�ĵ��Ƿ���Եִ�
		@type			position	  : Vector3
		@param			position	  : Ŀ��λ��
		@type			callback	  : functor / method with one parameters
		@param			callback	  : �ƶ������ص�
		"""
		return self._straightMoveMotor.seek(self, position, callback)

	def navigateTo( self, position, callback = None ):
		"""
		Ѱ·�ƶ���ָ��λ��
		@type			RETURN: bool
		@param			RETURN: Ŀ�ĵ��Ƿ���Եִ�
		@type			position	  : Vector3
		@param			position	  : Ŀ��λ��
		@type			callback	  : functor / method with one parameter
		@param			callback	  : �ƶ������ص�
		"""
		self.startMove()
		if self.__navigator.mouseCtrlRun( position, callback ):
			return True
		else:
			self.stopMove()
			return False

	def getSrcAndNearDstPos( self, dstPos ) :
		"""
		��ȡ��Ŀ����·���б�
		"""
		return self.__navigator.getPathList( dstPos )

	def velocityTo( self, position, callback, tickCallback = None ) :
		"""
		����ֱ������ײ��ˢһ�µ�ĳ���ط�ȥ,( ��ʱû�� ) 11:02 2008-6-25 yk
		velocity to one position( when arrived destination, it will not stop, so you must set stop at callback )
		@type			position	 : Vector3
		@param			position	 : destination position
		@type			callback	 : Fucntor
		@param			callback	 : when arrive distacne or out time, it will be called, it must contain one argument
		@type			tickCallback : Functor
		@param			tickCallback : if it is not None, it will be called every velocity tick
		@return						 : None
		"""
		BigWorld.dcursor().yaw = 0
		pos = Math.Vector3( position )
		dist = pos.distTo( self.position )
		needTime = dist * 1.2 / self.__speed
		startTime = time.time()
		self.__endVelecotyTime = startTime + needTime

		dpos = pos - self.position
		yaw = dpos.yaw
		pitch = dpos.pitch
		x = self.__speed * math.sin( yaw )
		y = -self.__speed * math.sin( pitch )
		z = self.__speed * math.cos( yaw )
		self.getPhysics().velocity = x, y, z
		self.__velocityDetect( self.position, pos, 1.0, callback, tickCallback )

	# -------------------------------------------------
	def pursueEntity( self, entity, nearby, callback = lambda player, entity, success : False ) :
		"""
		pursue entity
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		callback		  : callback functor
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���player, targetEntity, success��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
		@return						  : None
		"""
		if entity.__class__.__name__ == "MonsterBuilding": #�������ײ���������뽫���¼���
			dis = ( self.position - entity.position ).length
			disBB = entity.distanceBB( self )
			if disBB < 0: disBB = 0
			nearby += dis - disBB
		if not self.straightPursue(entity, nearby, Functor(self.__onStraightChaseCallback, callback, nearby)):
			self.navigatePursue(entity, nearby, callback)

	def navigatePursue( self, entity, nearby, callback = lambda player, entity, success : False ):
		"""
		pursue entity with navigate system.
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		callback		  : callback functor
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���player, targetEntity, success��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
		@return						  : None
		"""
		self.startMove()
		self.setActionState( ASTATE_PURSUE )
		self.__navigator.pursueEntity( entity, nearby, callback )

	def straightPursue( self, entity, nearby, callback = lambda player, entity, result : False ):
		"""
		pursue entity in straight moving.
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		callback		  : callback functor
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���player, targetEntity, result��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
		@return						  : None
		"""
		self.setActionState( ASTATE_PURSUE )
		return self._straightMoveMotor.chase(self, entity, nearby, callback)

	def pursuePosition( self, pos, nearby, callback = lambda player, entity, success : False ) :
		"""
		pursue entity
		@type		entity			  : instance
		@param		pos				  : pos you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		callback		  : callback functor
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���player, targetEntity, success��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
		@return						  : None
		"""
		self.startMove()
		self.setActionState( ASTATE_PURSUE )
		self.__navigator.pursuePosition( pos, nearby, callback )

	def onPursueOver( self, success ):
		"""
		׷��Ŀ���¼�������,navigator�ص��ú���
		@type		success: bool
		@param		success: �Ƿ���ٳɹ�
		"""
		self.stopMove()
		self.setActionState( ASTATE_CONTROL ) # Ѱ·��������Ҫ���°ѿ���״̬�޸�ΪĬ��״̬����ΪѰ·ǰ�Ѿ���״̬��ΪѰ·״̬��
		BigWorld.player().onMoveChanged( False )

	def isPursueState( self ):
		"""
		�жϵ�ǰ�Ƿ��ڸ���״̬
		"""
		return self.isActionState( ASTATE_PURSUE )

	# --------------------------------------------------
	# �Զ�Ѱ·
	# --------------------------------------------------
	def autoRun( self, position, nearby = 0.0, dstSpaceLabel = "" ) :
		"""
		@type			RETURN: bool
		@param			RETURN: Ŀ�ĵ��Ƿ���Եִ�
		@type			position   : Vector3
		@param			position   : Ŀ��λ��
		@type			nearby     : float
		@param			nearby     : �ƶ���Ŀ��λ�ø����ľ���
		@type			dstSpaceLabel   : string
		@param			dstSpaceLabel   : Ŀ��Space Name; Ĭ��ֵΪ""����ʾ�����ÿ糡������
		"""
		self.__naviPath = []
		player = BigWorld.player()
		if not self.allowMove():	# 18:26 2009-3-6��wsf
			if player.state == csdefine.ENTITY_STATE_VEND:
				player.statusMessage( csstatus.VEND_FORBIDDEN_MOVING )
			return
		self.onBeforeAutoRun()										# �Զ�Ѱ·ǰҪ��������
		self.startMove()
		self.__navigator.triggerRun( position, Functor( self.__autoRunCallback, None ), nearby, dstSpaceLabel )	# ����Ѱ·
		if self.__navigator.isRunning():
			self.startAutoRun( position )
			self.__naviPath = self.getAutoRunPathLst()
			self.addModelInList()
			return True
		else:
			self.stopMove()
			return False
			
	def addModelInList( self ):
		pathList = self.analysicsPathList( self.__naviPath, Const.AUTO_RUN_DISTANCE )
		for i in self.modeList_:
			self.delModel(i)		# �����һ�β���������Ѱ·ָ��,��������ָ��
		self.modeList_ = []
		for index,value in enumerate( pathList ):
			model = BigWorld.Model( Const.AUTO_RUN_GUIDE_MODEL_PATH )
			self.modeList_.append( model )
			self.addModel( model )
			model.position = value
			if index < len( pathList )-1:
				model.yaw = Math.Vector3(  pathList[ index + 1 ] - value ).yaw 
				model.pitch = Math.Vector3(  pathList[ index + 1 ] - value ).pitch
			else:
				model.yaw = Math.Vector3(  value - pathList[ index -1 ] ).yaw 
				model.pitch = Math.Vector3(  value - pathList[ index - 1 ] ).pitch
		if self.modeList_ and not self.__guideCBID:
			self.__guideCBID = Timer.addTimer( Const.AUTO_RUN_TIME_TICK, Const.AUTO_RUN_TIME_TICK, self.guideModelDetect_ )

	def analysicsPathList( self, pathList, minDis ):
		"""
		Ѱ··������
		�Ⱦ���·�����ȡ
		"""
		path = []
		index = 1
		tNode = newNode = pathList[0]
		more = 0 # ǰһ�������֮�����µľ���
		while( index < len( pathList ) ):
			temp = more
			st = csarithmetic.distancePP3( pathList[ index ], tNode )  # �µ�����һ��Ѱ·��֮��ľ���
			if st + more > 2 * minDis:     # ��ǰ����+���µľ���> 2���ı�׼���룬��ʾ��2���м���ж���Ⱦ���·����
				newNode = csarithmetic.getSeparatePoint3( tNode, pathList[ index ], minDis - more )
				temp = 0
				tNode = newNode        # ���������µȾ���·��������Ϊ��ǰ·����
				newPos = csarithmetic.getCollidePoint( self.spaceID, newNode, newNode + ( 0, -20, 0 ) )
				path.append( newPos )
			if st + more > minDis and st + more < 2 * minDis:
				newNode = csarithmetic.getSeparatePoint3( tNode, pathList[ index ], minDis - more )
				temp = st - minDis + temp
				tNode = pathList[ index ]
				index += 1
				newPos = csarithmetic.getCollidePoint( self.spaceID, newNode, newNode + ( 0, -20, 0 ) )
				path.append( newPos )
			if st + more < minDis:
				temp += st
				tNode = pathList[ index ]
				index += 1
			more = temp
		return path

	def getAutoRunPathLst( self ):
		"""
		��ȡ�Զ�Ѱ·��·���ڵ��б�
		"""
		return  self.__navigator.getNavPosLst( )
		
	def getAutoRunPathList( self ):
		"""
		��ȡ�Զ�Ѱ·��·���ڵ��б�
		"""
		return  self.__naviPath

	def getAutoRunGoalPosition( self ):
		"""
		��ȡ�Զ�Ѱ·��Ŀ��λ��
		"""
		return self.__navigator.getGoalPosition()

	def isAutoRunning( self ):
		"""
		�Ƿ����Զ�Ѱ·��
		"""
		return self.__navigator.isRunning()

	# --------------------------------------------------
	# ת��
	# --------------------------------------------------
	def turnaround( self, dstMatrix, callback = None ):
		"""
		ת��
		@type  			matrix : Matrix
		@param 			matrix : matrix of the role base to
		@type			func   : functor
		@param   		func   : it will be called, when turnaround is over
		@return				   : None
		"""
		if self.__turnaroundTimerID != 0 : return						# refused -- it is in moving
		physics = self.getPhysics()
		if physics is None : return
		physics.targetSource = self.matrix
		physics.targetDest = dstMatrix
		turnModelToEntity = self.am.turnModelToEntity
		old_param = [turnModelToEntity, physics.dcLocked]				# record the old coefficients for recovering when turnaround is over

		self.am.turnModelToEntity = True
		physics.dcLocked = True
		functor = Functor( self.__onTurnaroundOver, old_param, callback )
		self.__turnaroundTimerID = Timer.addTimer( 0.5, 0, functor )

	def resetNavigate( self ):
		"""
		���¼���navigate
		"""
		self.__navigator = None
		import navigate
		reload( navigate )
		from navigate import NavigateEx
		self.__navigator = NavigateEx( self )

	def resetStraightMoveMotor( self ):
		"""
		���¼���ֱ���ƶ�����
		"""
		self._straightMoveMotor = None
		import StraightMoveMotor
		reload( StraightMoveMotor )
		from StraightMoveMotor import StraightMoveMotor
		self._straightMoveMotor = StraightMoveMotor()

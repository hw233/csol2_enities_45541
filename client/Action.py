# -*- coding: gb18030 -*-
#
# $Id: Action.py,v 1.110 2008-08-09 10:10:22 huangdong Exp $

"""
actions manager

2006/10/09 : writen by huangyongwei
2008/12/20 : tidy up by huangyongwei
			 ① 独立出方向组合与移动状态（将移动状态与方向指示并在一起是错误的）
			 ② 对初始化的成员变量加以注释
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
# 全局定义( tidy up by hyw -- 2008.12.20 )
# 注意：关于方向指示，目前为止，应该只有以下这些，
#	    要增加其他功能组合时，请仔细思量那是否与方向相关
# --------------------------------------------------------------------
# 单向指示
DIRECT_NONE			= 0		# 没有方向指示	\
DIRECT_FORWARD		= 1		# 向前			|
DIRECT_LEFT			= 2		# 向左			 > 并列
DIRECT_BACKWARD		= 4		# 向后			|
DIRECT_RIGHT		= 8		# 向右			/
DIRECT_JUMPUP		= 16	# 向上，即跳 －－> 优先

# 混合方向指示
POINT_LEFT			= lambda du : ( du & DIRECT_LEFT ) and not ( du & DIRECT_RIGHT )		# 具有向左指示
POINT_RIGHT			= lambda du : ( du & DIRECT_RIGHT ) and not ( du & DIRECT_LEFT )		# 具有向右指示
POINT_FORWARD		= lambda du : ( du & DIRECT_FORWARD ) and not ( du & DIRECT_BACKWARD )	# 具有向前指示
POINT_BACKWARD		= lambda du : ( du & DIRECT_BACKWARD ) and not ( du & DIRECT_FORWARD )	# 具有向后指示
POINT_JUMPUP		= lambda du : du & DIRECT_JUMPUP										# 具有向上指示
POINT_UNQUITS		= lambda du : POINT_LEFT( du ) or POINT_RIGHT( du ) or \
								  POINT_FORWARD( du ) or POINT_BACKWARD( du ) 				# 是否有方向指示( 没有方向抵消 )

# -----------------------------------------------------
# 行为状态（这些状态不会共存）
ASTATE_CONTROL		= 1		# 玩家控制状态
ASTATE_DEST			= 2		# 移动到指定目的点
ASTATE_AUTOFORWARD	= 3		# 自动行走状态
ASTATE_NAVIGATE		= 4		# 自动寻路状态
ASTATE_FOLLOW		= 5		# 跟随状态
ASTATE_PURSUE		= 6		# 追踪目标状态


# --------------------------------------------------------------------
# implement Action class
# --------------------------------------------------------------------
class Action :
	def __init__( self ) :
		self.__speed = 0									# 移动速度
		self.__directUnion = DIRECT_NONE					# 方向组合
		self.__actionState = ASTATE_CONTROL					# 标记

		self.__navigator = NavigateEx( self )
		self.__turnaroundTimerID = 0						# 转身监测 timer ID
		self.__velocityCBID = 0
		self.__guideCBID = 0								# 指引timer

		self._straightMoveMotor = StraightMoveMotor()
		self.modeList_ = []

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onStraightMoveCallback( self, callback, destination, result ):
		"""直线移动到目标位置回调"""
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
		寻路移动到指定点回调
		"""
		self.stopMove( )
		if type(callback) == type((2,)):#tuple
			callback = callback[0]
		if callable( callback ) :
			callback( isSuccess )

	def __onStraightChaseCallback( self, callback, nearby, chaser, target, result ):
		"""采用直线追踪目标方式的回调"""
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
		自由寻路的回调函数
		@type		callback:  Functor
		@param		callback:  回调函数
		@type		isSuccess: bool
		@param		isSuccess: 是否抵达目的点
		"""
		self.stopMove()
		self.endAutoRun( isSuccess )
		if callable( callback ) :
			callback( isSuccess )

	def __onTurnaroundOver( self, old_param, callback ) :
		"""
		转身结束回调
		@param 		old_param : see also method turnaround() in old_param = ......
		@param   	callback  : callback specifies turnaround over，it must contain an argument, PlayerRole will be passed as the callback argument
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
		velocity 检测
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
		根据当前方向组合指示和相机方向计算角色面向
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
		当相机方向改变时被调用
		在这里实现，使用键盘移动过程中，角色走动的方向始终相对镜头方向而言
		"""
		if self.isMoving() and ( self.isActionState( ASTATE_CONTROL ) or self.isActionState( ASTATE_AUTOFORWARD ) ):
			BigWorld.dcursor().yaw = self.__calcYaw()

	# -------------------------------------------------
	def onBeforeAutoRun( self ):
		"""
		自动寻路之前做的事情
		"""
		pass

	def startAutoRun( self, position ):
		"""
		开始自动寻路，设置自动寻路状态，并做一些事情
		@type    position: Vector3
		@param   position: 自动寻路点
		"""
		self.setActionState( ASTATE_NAVIGATE )
		self.onStartAutoRun( position )

	def onStartAutoRun( self, position ):
		"""
		自动寻路后坐的事情。
		"""
		pass

	def endAutoRun( self, state ) :
		"""
		自动寻路是否到达目的地的回调通知，可以在此做一些事情
		@type    state: bool
		@param   state: 是否成功到达目的地
		wsf －－ 11:39 2008-7-25
		"""
		# 结束自动寻路状态
		self.setActionState( ASTATE_CONTROL )
		self.onEndAutoRun( state )

	def onEndAutoRun( self, state ):
		"""
		结束后做的事情
		virtual Method
		"""
		pass

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def getSpeed( self ) :
		"""
		获取移动速度
		"""
		return self.__speed

	def setSpeed( self, speed ) :
		"""
		设置移动速度
		@type			speed  : float
		@param			speed  : 速度值
		"""
		self.__speed = speed
		if self.isMoving() :
			self.updateVelocity()

	def getPhysics( self ):
		"""
		获取 Entity 的 physics
		"""
		if hasattr( self, "physics" ):
			return self.physics
		return None

	# -------------------------------------------------
	def updateDirection( self, flag, isset ) :
		"""
		更新方向标记
		@type			flag  : MACRO DEFINATION
		@param			flag  : 方向标记: DIRECT_*
		@type			isset : bool
		@param			isset : 指出是设置指定标记还是清除指定标记（为 True 则设定，反之清除）
		"""
		if isset :
			self.__directUnion |= flag
			if POINT_UNQUITS( self.__directUnion ) :		# 如果增加了移动标记（即方向指示，这种情况是因为可能玩家增在自动往前走，突然按下了方向键盘，则要停止其自动行走）
				self.__actionState = ASTATE_CONTROL			# 设置受控状态
				self.__directUnion &= ~DIRECT_JUMPUP		# 取消跳跃标记（注：在这里取消跳跃标记实际上是不合理的，
															# 但是这样可以防止跳跃后，标记有时不会被清除的问题，
															# 况且，跳跃标记在 entity 跳起来后就不起作用了，因此只要起跳了，其标记就可以清除）
		else :
			self.__directUnion &= ~flag						# 清除指定方向标记

	def testDirection( self, flag ) :
		"""
		检测当前是否有指定方向标记
		@type			flag : MACRO DEFINATION
		@param			flag : 方向标记: DIRECT_*
		"""
		return self.__directUnion & flag == flag

	def emptyDirection( self ) :
		"""
		清理方向标记（由 resumeAction 改名为 emptyDirection）
		"""
		self.__directUnion = DIRECT_NONE

	# ---------------------------------------
	def setActionState( self, state ) :
		"""
		设置行为状态
		"""
		self.__actionState = state
		if state != ASTATE_CONTROL :
			self.emptyDirection()

	def isActionState( self, state ) :
		"""
		指出某移动标志是否设置
		"""
		return self.__actionState == state

	# -------------------------------------------------
	def flushAction( self ) :
		"""
		根据行为状态和移动意图方向，更新行为动作（停止或按某个方向移动）
		"""
		if not self.allowMove() : return							# 如果不允许移动，则返回
		if self.__actionState != ASTATE_CONTROL : return			# 如果处于自动移动状态，则移动不受方向影响
		if POINT_UNQUITS( self.__directUnion ) :					# 是否有组合后的方向向量（有组合方向，或方向不抵消）
			BigWorld.dcursor().yaw = self.__calcYaw()	# 则，更改角色面向为指示方向
			self.startMove() # 让角色移动
		else:						# 否则
			self.stopMove( True )				# 停止移动状态

	def flushActionByKeyEvent( self ):
		"""
		根据键盘消息，更新行为动作（跳跃键暂不处理）
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
		触发角色 velocity
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
		判断自己是否能移动，允许重写
		"""
		return True

	def isMoving( self ):
		"""
		指出角色当前是否处于移动状态
		"""
		physics = self.getPhysics()
		return physics and physics.moving and Math.Vector3( physics.velocity ) != Math.Vector3( 0, 0, 0 )

	def startMove( self ):
		"""
		以角色当前的朝向向前移动
		"""
		self.stopMove(True)
		self.updateVelocity()
		if self.modeList_ or self.canShowGuideModel() or self.fubenGuideModel:
			self.__guideCBID = Timer.addTimer( Const.AUTO_RUN_TIME_TICK, Const.AUTO_RUN_TIME_TICK, self.guideModelDetect_ )

	def stopMove( self, isControl = False) :
		"""
		停止移动
		"""
		physics = self.getPhysics()
		if physics == None:
			return
		if self._straightMoveMotor.running():
			self._straightMoveMotor.stop()
		elif self.__navigator.isRunning():
			self.__navigator.forceStop()
		elif physics.seeking:									# 如果正在 seeking，则停之
			physics.setSeekCallBackFn( None )
			physics.seek( None, 0, 0, None )
		#如果在跳跃状态不更新速度
		if hasattr( self, "getJumpState" ) and self.getJumpState() != Const.STATE_JUMP_DEFAULT:
			physics.velocity = ( 0, physics.velocity[1], 0 )
		else:
			physics.stop()
		Timer.cancel( self.__guideCBID )
		self.__guideCBID = 0

	def stopVelocity( self ) :
		"""
		停止骑宠
		"""
		BigWorld.cancelCallback( self.__velocityCBID )
		self.getPhysics().stop()

	# -------------------------------------------------
	def seek( self, position, verticalRange, callback, isSeekToGoal = True, isFacetoPos = True ) :
		"""
		移动到指定位置，可以自定义跨越障碍高度
		@type 			position	  : Vector3
		@param			position	  : 目标位置
		@type			verticalRange : float
		@param			verticalRange : 障碍高度
		@type			callback	  : functor
		@param			callback	  : seek 结束回调
		@type			isSeekToGoal  : bool
		@param 			isSeekToGoal  : 是否强制到达指定位置， 为False时，采用平滑缓冲处理
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
		寻路状态中,当没有找到路径时,回调该函数
		@type		navExState: NAV_STATE @see navigate.py in NavigateEx class
		@param		navExState: 寻路的状态
		"""
		#ToDo：这里显示寻路失败的相关消息
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
		移动到指定位置
		@type			RETURN: bool
		@param			RETURN: 目的地是否可以抵达
		@type			position	  : Vector3
		@param			position	  : 目标位置
		@type			callback	  : functor / method with one parameter
		@param			callback	  : 移动结束回调
		"""
		if self.moveStraightTo(position, Functor(self.__onStraightMoveCallback, callback, position)):
			return True
		else:
			return self.navigateTo(position, Functor(self.__onNavigateCallback, callback))

	def moveStraightTo( self, position, callback = None ):
		"""
		寻路移动到指定位置
		@type			RETURN: bool
		@param			RETURN: 目的地是否可以抵达
		@type			position	  : Vector3
		@param			position	  : 目标位置
		@type			callback	  : functor / method with one parameters
		@param			callback	  : 移动结束回调
		"""
		return self._straightMoveMotor.seek(self, position, callback)

	def navigateTo( self, position, callback = None ):
		"""
		寻路移动到指定位置
		@type			RETURN: bool
		@param			RETURN: 目的地是否可以抵达
		@type			position	  : Vector3
		@param			position	  : 目标位置
		@type			callback	  : functor / method with one parameter
		@param			callback	  : 移动结束回调
		"""
		self.startMove()
		if self.__navigator.mouseCtrlRun( position, callback ):
			return True
		else:
			self.stopMove()
			return False

	def getSrcAndNearDstPos( self, dstPos ) :
		"""
		获取到目标点的路径列表
		"""
		return self.__navigator.getPathList( dstPos )

	def velocityTo( self, position, callback, tickCallback = None ) :
		"""
		用于直接无碰撞地刷一下到某个地方去,( 暂时没用 ) 11:02 2008-6-25 yk
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
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是player, targetEntity, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		if entity.__class__.__name__ == "MonsterBuilding": #如果带碰撞，靠近距离将重新计算
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
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是player, targetEntity, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
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
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是player, targetEntity, result，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
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
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是player, targetEntity, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		self.startMove()
		self.setActionState( ASTATE_PURSUE )
		self.__navigator.pursuePosition( pos, nearby, callback )

	def onPursueOver( self, success ):
		"""
		追踪目标事件结束后,navigator回调该函数
		@type		success: bool
		@param		success: 是否跟踪成功
		"""
		self.stopMove()
		self.setActionState( ASTATE_CONTROL ) # 寻路结束后需要重新把控制状态修改为默认状态（因为寻路前已经把状态置为寻路状态）
		BigWorld.player().onMoveChanged( False )

	def isPursueState( self ):
		"""
		判断当前是否处于跟踪状态
		"""
		return self.isActionState( ASTATE_PURSUE )

	# --------------------------------------------------
	# 自动寻路
	# --------------------------------------------------
	def autoRun( self, position, nearby = 0.0, dstSpaceLabel = "" ) :
		"""
		@type			RETURN: bool
		@param			RETURN: 目的地是否可以抵达
		@type			position   : Vector3
		@param			position   : 目标位置
		@type			nearby     : float
		@param			nearby     : 移动到目标位置附近的距离
		@type			dstSpaceLabel   : string
		@param			dstSpaceLabel   : 目标Space Name; 默认值为""，表示不启用跨场景搜索
		"""
		self.__naviPath = []
		player = BigWorld.player()
		if not self.allowMove():	# 18:26 2009-3-6，wsf
			if player.state == csdefine.ENTITY_STATE_VEND:
				player.statusMessage( csstatus.VEND_FORBIDDEN_MOVING )
			return
		self.onBeforeAutoRun()										# 自动寻路前要做的事情
		self.startMove()
		self.__navigator.triggerRun( position, Functor( self.__autoRunCallback, None ), nearby, dstSpaceLabel )	# 启动寻路
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
			self.delModel(i)		# 清除上一次产生的所有寻路指引,重新生成指引
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
		寻路路径分析
		等距离路径点获取
		"""
		path = []
		index = 1
		tNode = newNode = pathList[0]
		more = 0 # 前一个点计算之后余下的距离
		while( index < len( pathList ) ):
			temp = more
			st = csarithmetic.distancePP3( pathList[ index ], tNode )  # 新点与下一个寻路点之间的距离
			if st + more > 2 * minDis:     # 当前距离+余下的距离> 2倍的标准距离，表示该2点中间会有多个等距离路径点
				newNode = csarithmetic.getSeparatePoint3( tNode, pathList[ index ], minDis - more )
				temp = 0
				tNode = newNode        # 将产生的新等距离路径点设置为当前路径点
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
		获取自动寻路的路径节点列表
		"""
		return  self.__navigator.getNavPosLst( )
		
	def getAutoRunPathList( self ):
		"""
		获取自动寻路的路径节点列表
		"""
		return  self.__naviPath

	def getAutoRunGoalPosition( self ):
		"""
		获取自动寻路的目标位置
		"""
		return self.__navigator.getGoalPosition()

	def isAutoRunning( self ):
		"""
		是否在自动寻路中
		"""
		return self.__navigator.isRunning()

	# --------------------------------------------------
	# 转向
	# --------------------------------------------------
	def turnaround( self, dstMatrix, callback = None ):
		"""
		转身
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
		重新加载navigate
		"""
		self.__navigator = None
		import navigate
		reload( navigate )
		from navigate import NavigateEx
		self.__navigator = NavigateEx( self )

	def resetStraightMoveMotor( self ):
		"""
		重新加载直线移动引擎
		"""
		self._straightMoveMotor = None
		import StraightMoveMotor
		reload( StraightMoveMotor )
		from StraightMoveMotor import StraightMoveMotor
		self._straightMoveMotor = StraightMoveMotor()

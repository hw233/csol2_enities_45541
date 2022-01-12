# -*- coding: gb18030 -*-

"""
可走动对象的基础类
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
	计算两点是否在同一位置

	@param v1: 位置1
	@param v1: VECTOR3
	@param v2: 位置2
	@param v2: VECTOR3
	@return:   成功/失败
	@rtype:    BOOL
	"""
	return math.fabs(v1[0]-v2[0]) < 0.1 and math.fabs(v1[2]-v2[2]) < 0.1

class AmbulantObject:
	"""
	NPC基类
	"""
	def __init__( self ):
		"""
		"""
		# 默认关闭所有继承于此类的entity的坐标广播
		self.volatileInfo = VOLATILE_INFO_CLOSED

	# =======================================
	# 移动控制相关接口
	# =======================================
	def stopMoving( self ):
		"""
		停止当前的移动行为

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
		关闭坐标信息传送功能。
		由于这个模块会被不同的entity调用，而某些entity可能会需要以不同
		的方式或时机关闭这个行为，因此这个接口允许玩家重载。
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
		打开坐标信息传送功能
		由于这个模块会被不同的entity调用，而某些entity可能会需要以不同
		的方式或时机关闭这个行为，因此这个接口允许玩家重载。
		"""
		if self.volatileInfo == VOLATILE_INFO_OPENED:
			return
		if self.hasFlag( csdefine.ENTITY_VOLATILE_ALWAYS_CLOSE ):
			return
		self.volatileInfo = VOLATILE_INFO_OPENED
		self.planesAllClients( "restartFilterMoving", () )

	def doRandomRun( self, centerPos, radius ):
		"""
		走到centerPos为原点，radius为半径的随机采样点
		@param  centerPos: 原点
		@type   centerPos: Vector3
		@param  radius:    半径
		@type   radius:    FLOAT
		"""
		initRad = 2*math.pi * random.random()		# 随即选取一个初始角度
		for tryNum in xrange( 0, 8 ): #将原来的30次改为8次,从圆周上选取八个点
			rad = initRad + tryNum * 45.0
			pos = Math.Vector3( centerPos )
			distance = radius * random.random()
			if distance < 2: 					# 保证怪物与追击目标的距离大于两米
				distance = 2
			pos.x += distance * math.sin( rad )
			pos.z += distance * math.cos( rad )
			if self.gotoPosition(pos):
				return True

		return False

	def resetMoving( self ):
		"""
		停止当前移动行为，重新进行移动。
		如果entity当前没有移动，那么什么事也不做，否则将会根据当前的移动速度调整。
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
		仅仅封装了self.navigateStep()的一些错误处理，以及简化了一些调用参数。
		此方法不允许重载；

		@param    position: (Vector3) The destination point for the Entity to move towards
		@param    velocity: (float) The speed to move the Entity in m/s
		@param maxDistance: (float) Maximum distance to move
		@param    userData: (optional object) Data that can be passed to notification method.
		@return: ControlID，值为0表示失败
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
		移动到一个位置；
		此方法不允许重载；

		自定义移动接口的好处之一是可以让移动行为根据npc、怪物的移动速度来统一进行，省去了其它地方调用时的额外考虑。
		通过此函数移动结束后会自动调用onMovedOver()回调函数；
		在移动的过程中取消移动将不会触发onMovedOver()。

		注意：此函数与chaseEntity()以及引擎提供的相关移动函数一样，任何时刻只能有一个移动存在；

		@param position: 目标位置
		@type  position: VECTOR3
		@param faceTo: 是否面向
		@type  faceTo: BOOL
		@return: 返回此次接口调用是否成功
		@rtype:  BOOL
		"""
		self.stopMoving()
		if self.move_speed <= 0.0:	# 速度太小，不移动
			return False
		if self._goto_position( position, faceTo ):
			self.openVolatileInfo()
			return True
		else:
			return False

	def _goto_position( self, position, faceTo ):
		"""
		gotoPosition()的内部实现；参数说明详见：gotoPosition()
		此方法不允许重载；

		@return: 返回此次接口调用是否成功
		@rtype:  BOOL
		"""
		self.setTemp( "gotoPosition", tuple( position ) )
		self.setTemp( "faceTo", faceTo )
		self.movingControlID = self.navigateStepEx_( position, self.move_speed, 0xFF, ECBExtend.GOTO_POSITION_CBID, faceTo )
		if not self.movingControlID:
			return False
		self.setMovingType( Const.MOVE_TYPE_DEFAULE )		# 处于移动到指定位置状态中
		return True

	def onMovedFinish( self, controllerId, userData, state ):
		"""
		用于gotoPosition()函数在ECBExtend模块中的回调处理

		@param state: bool; 标识是否移动成功,但在1.72下,似乎总是成功的——哪怕根本无法移动到目标位置
		@param controllerId: 移动结束的控制器ID
		"""
		#DEBUG_MSG( self.id, controllerId, userData, state )
		if self.movingControlID == 0: return	# 似乎……正常情况下能调用到这里的都不可能为0

		if not state:
			# 移动失败，没有继续移动的必要了
			self.onMovedOver( False )
			return

		t = self.navigateTime
		self.navigateTime = BigWorld.time()
		#DEBUG_MSG( self.id, "moving delay", self.navigateTime - t )
		# 对于连续多次短时间内移动的判断时间长度问题，经测试，最小也需要为0.1，但不保险，因此设为0.5以为保险些。
		# 其实这个值设多少都不太合适，最合适的是c++底层对此进行封装，在无法移动到目标位置时给于移动失败状态。
		if self.navigateTime - t > 0.3:
			self.navigateCount = 0
		else:
			# 连续多次在短时间内移动则记录，用于下面做失败判断
			# 需要如此做的原因是navigateStep()或navigateFollow()函数无法到达一个地方时不返回False
			self.navigateCount += 1

		if self.navigateCount >= 10:
			# 多次在极短的时间内停止移动，我们认为它移动失败
			self.navigateTime = 0.0
			self.onMovedOver( False )
			return

		pos = self.queryTemp( "gotoPosition", None )	# 就理论而言，这里取值不可能为None，否则很可能有BUG，因此这里不作判断
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
		使用gotoPosition()移动结束通告

		@param state: 移动结果，表示是否成功
		@type  state: bool
		@return:      None
		"""
		self.stopMoving()


	def chaseEntity( self, entity, distance ):
		"""
		追踪一个entity；
		此方法不允许重载；

		自定义移动接口的好处之一是可以让移动行为根据npc、怪物的移动速度来统一进行，省去了其它地方调用时的额外考虑。
		通过此函数移动结束后会自动调用onChaseOver()回调函数；
		在移动的过程中取消移动将不会触发onChaseOver()。

		注意：此函数与gotoEntity()以及引擎提供的相关移动函数一样，任何时刻只能有一个移动存在；

		@param   entity: 被追赶的目标
		@type    entity: Entity
		@param distance: 离目标entity多远的距离停下来(米/秒)
		@type  distance: FLOAT
		@return: 返回此次接口调用是否成功
		@rtype:  BOOL
		"""
		self.stopMoving()     # 为了追击更流畅
		if self._chase_entity( entity, distance ):
			self.openVolatileInfo()
			return True
		else:
			return False

	def _chase_entity( self, entity, distance ):
		"""
		追踪一个entity；
		此方法不允许重载；

		@return: 返回此次接口调用是否成功
		@rtype:  BOOL
		"""
		self.chaseEntityID = entity.id
		self.setTemp( "chaseEntityDist", distance )
		self.movingControlID = self.navigateStepEx_( entity.position, self.move_speed, 1.5, ECBExtend.CHASE_ENTITY_CBID, True )
		if not self.movingControlID:
			return False
		self.setMovingType( Const.MOVE_TYPE_CHASE )		# 处于追击目标中
		return True

	def onChaseFinish( self, controllerId, userData, state ):
		"""
		用于chaseEntity()函数在ECBExtend模块中的回调处理
		"""
		#DEBUG_MSG( self.id, controllerId, userData, state )
		if self.movingControlID == 0: return	# 似乎……正常情况下能调用到这里的都不可能为0
		chaseEntityID = self.chaseEntityID		# 将目标 ID 保存下来，因为下面的 stopMoving 会将追踪目标 ID 清除掉（hyw--08.07.22）

		try:
			entity = BigWorld.entities[chaseEntityID]
		except KeyError:
			entity = None

		if (not state) or (not entity) or (entity.spaceID != self.spaceID):
			# 移动失败或目标已经不存在又或不在同一场景，就没有追踪的必要了
			self.onChaseOver( entity, False )
			return
		t = self.navigateTime
		self.navigateTime = BigWorld.time()
		#DEBUG_MSG( self.id, "moving delay", self.navigateTime - t )
		if self.navigateTime - t > 0.5:
			self.navigateCount = 0
		else:
			# 连续多次在短时间内移动则记录，用于下面做失败判断
			# 需要如此做的原因是navigateStep()或navigateFollow()函数无法到达一个地方时不返回False
			self.navigateCount += 1
		if self.navigateCount >= 2:
			# 多次在极短的时间内停止移动，我们认为它移动失败
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
		使用chaseEntity()移动结束通告

		@param   entity: 被追赶的目标，如果在结束时目标找不到（即目标消失了）则此值为None
		@type    entity: Entity
		@param    state: 移动结果，表示是否成功
		@type     state: bool
		@return:         None
		"""
		self.stopMoving()

	#-----------------------------------------------------------------------------------------------------
	# 巡逻相关  kb
	#-----------------------------------------------------------------------------------------------------
	def stopPatrol( self ):
		"""
		停止巡逻
		"""
		self.stopMoving()

	def doPatrol( self, patrolPathNode = '', patrolList = None ):
		"""
		virtual method.
		执行一个新的巡逻行为
		@param  patrolPathNode	:  patrolPathNode 开始出发的点
		@type   patrolPathNode	:  string
		@param  patrolList		: PatrolPath实例
		@type   patrolList		: PATROL_PATH
		"""
		if self.isMoving():
			if not self.isMovingType( Const.MOVE_TYPE_PATROL ):
				self.stopMoving()
				self.openVolatileInfo()
		else:
			self.openVolatileInfo()

		# 如果外部给了一个新的巡逻数据 那么这里应该改变巡逻数据
		if len( patrolPathNode ) > 0 and patrolList != None:
			self.setTemp( "patrolPathNode", patrolPathNode )
			self.patrolListRecord = patrolList
		else:
			# 如果没有相关的巡逻信息 那么退出
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

		# 得到下一个连接点
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
			# 如果只有一个连接点 ( 通常是单向连点 或者双向连点的一个分支末端的返回点 )
			self.setTemp( "Patrol_gotoNode", patrolInfo[ 0 ][ 0 ] )
			position = patrolInfo[0][1]
			if abs( position.x ) < 0.000001 and abs( position.y ) < 0.000001 and abs( position.z ) < 0.000001:				# 下一个点的坐标为0说明linkTo的点不存在，配置有误
				ERROR_MSG( " can not get the next patrol point!    className: %s, monster spaceName: %s, monster position: %s, patrolList: %s,current patrolNode is: %s"%( self.className, self.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ), str(self.position), patrolList.graphIDAsString(), patrolPathNode )  )
				self.canPatrol = False
				return False
			if not gotoPoint( position ):
				ERROR_MSG( " gotoPoint is failed." )
				self.canPatrol = False
				return False
		elif patrolCount >= 2:
			# 这里通常是多向连点
			patrolInfoList = list( patrolInfo )
			while patrolCount > 0:
				idx = random.randint( 0, patrolCount - 1 )
				if patrolInfoList[ idx ][ 0 ] in [ patrolPathNode, self.queryTemp( "Patrol_OldNode" ) ]:
					patrolInfoList.pop( idx )
					patrolCount -= 1
					continue
				self.setTemp( "Patrol_gotoNode", patrolInfoList[ idx ][ 0 ] )
				position = patrolInfoList[ idx ][ 1 ]
				if abs( position.x ) < 0.000001 and abs( position.y ) < 0.000001 and abs( position.z ) < 0.000001:				# 下一个点的坐标为0说明linkTo的点不存在，配置有误
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

		self.setMovingType( Const.MOVE_TYPE_PATROL )		# 处于巡逻中
		self.canPatrol = True
		return True

	def onPatrolToPointFinish( self, controllerId, userData, state ):
		"""
		用于doPatrol()函数在ECBExtend模块中的回调处理

		@param state: bool; 标识是否移动成功,但在1.72下,似乎总是成功的——哪怕根本无法移动到目标位置
		@param controllerId: 移动结束的控制器ID
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
		用于onPatrolToPointFinish()函数在ECBExtend模块中的回调处理

		@param command: 巡逻到一个点所得到的命令参数
		"""
		if BigWorld.time() - self.queryTemp( "patrol_moving_start_time" )  < 0.01:
			return False
		return True


	#-----------------------------------------------------------------------------------------------------
	# 直线运动相关,考虑运动方向碰撞与地面碰撞
	#-----------------------------------------------------------------------------------------------------
	def lineToPoint( self, dstPos, moveSpeed, faceMovement ):
		"""
		virtual method.
		运动至某点，考虑运动方向碰撞与地面碰撞,故entity最终点不一定是dstPos。
		@param dstPos			: 运动目标点
		@type dstPos			: Vector3
		@param faceMovement		: entity朝向是否和运动方向一致
		@type faceMovement		: Bool
		"""
		self.stopMoving()
		self.openVolatileInfo()
		self.setMovingType( Const.MOVE_TYPE_BACK )
		try:
			# moveToPointObstacle_cpp:带碰撞功能的moveToPoint。
			# crossHight参数默认0.5，为跨越障碍的高度；distance参数默认0.5，碰撞反弹的距离,避免表现上entity嵌入碰撞体内部。
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
		移动至某点回调
		"""
		self.stopMoving()

	def moveRadiFollow( self, targetID, angle, distanceRange ):
		"""
		怪物的游荡行为
		
		@param angle: 角度
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
		怪物的靠近或者远离游荡行为
		@param angle: 角度
		
		此处用navigateStep的原因有：1、navigateFollow与navigateStep的差别仅在于一个是围绕entity运动，一个是围绕目标点运动。
		2、调用self.navigateFollow( target, angle_new, distance_a, speed, distance_a, distance_a*2,0, 0.5,ECBExtend.MOVE_RADI_FOLLOW_CBID )，通过调整angle_new的值，
		想要达到远离的效果，发现就算是同一个角度，也会导致很多时候远离了，然后又靠近了。不能达到远离的效果。
		为了保证远离游荡以及靠近游荡是
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
		Monster.navigateFollow的回调函数
		"""
		self.stopMoving()
		
	def onMoveNearRaidFollowCB( self, controllerId, userData, state ):
		"""
		Monster.navigateFollow的回调函数
		"""
		self.stopMoving()
		AICommandID = self.queryTemp( "NearFollow_AICommandID", 0 )
		if AICommandID:
			self.sendAICommand( self.id, AICommandID )
			
	def onMoveFarRaidFollowCB( self, controllerId, userData, state ):
		"""
		Monster.navigateFollow的回调函数
		"""
		self.stopMoving()
		AICommandID = self.queryTemp( "FarFollow_AICommandID", 0 )
		if AICommandID:
			self.sendAICommand( self.id, AICommandID )
		
	def changeYaw( self, controllerId, userData ):
		"""
		没有限制的同步朝向
		"""
		targetPos = self.queryTemp( "targetPos", self.position )
		yaw = ( targetPos - self.position ).yaw
		self.direction = ( 0, 0, yaw )

	def moveBack( self, targetID, distance ):
		"""
		后退一段距离
		"""
		if self.isMoving() and self.isMovingType( Const.MOVE_TYPE_BACK ):		# 正在退就不管它
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
		if random.randint( 1, 10 ) < 4:  # 70%概率执行run_back,30%概率向后移动的时候执行跳跃动作
			self.planesAllClients( "jumpBackFC", () )
		self._moveBack( speed, targetPos )
	
	def _moveBack( self, speed, targetPos ):
		"""
		run_back
		"""
		self.lineToPoint( targetPos, speed, False )
		
	def calDstDirection( self, positionX, positionY, angle ):
		"""
		根据坐标以及偏移得到最终的方向
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
		判断entity当前是否正在移动中

		@return: BOOL
		@rtype:  BOOL
		"""
		return self.movingControlID != 0


	def setMovingType( self, movingType ):
		"""
		设置移动类型
		"""
		self.lastMovingType = self.movingType
		self.movingType = movingType
		self.onMovingTypeChange()


	def isMovingType( self, movingType ):
		"""
		判断是否是某个移动类型
		"""
		return self.movingType == movingType

	def isLastMovingType( self, lastMovingType ):
		"""
		判断之前的移动类型是否某类型
		"""
		return self.lastMovingType == lastMovingType


	def onMovingTypeChange( self ):
		"""
		"""
		if self.isMovingType( Const.MOVE_TYPE_STOP ):
			# 在巡逻的话 得停止巡逻
			if self.isLastMovingType( Const.MOVE_TYPE_PATROL ):
				self.canPatrol = False
	
			# 在游荡的话 得停止游荡
			elif self.isLastMovingType( Const.MOVE_TYPE_ROUND ):
				cbidTag = self.popTemp("cbidTag")
				if cbidTag:
					self.cancel( cbidTag )
			elif self.isLastMovingType( Const.MOVE_TYPE_CHASE ):
			 	self.chaseEntityID = 0



	
#--------------------------------------------------------
# 转向
#--------------------------------------------------------
	def rotateToPos( self, position ):
		"""
		转向一个坐标
		"""
		disPos = position - self.position
		self.direction = (0,0,disPos.yaw)
		self.planesAllClients( "setFilterYaw", (disPos.yaw,) )
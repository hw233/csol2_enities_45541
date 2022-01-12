# -*- coding: gb18030 -*-

import time
import weakref
import BigWorld
import Math
import Timer
from bwdebug import *


STRAIGHT_MOVE_SUCCESS	= 1
STRAIGHT_MOVE_CANCEL	= 2
STRAIGHT_MOVE_COLLIDE	= 3

class StraightMoveMotor:

	def __init__( self ):
		self._seeker = StraightSeeker()
		self._chaser = StraightChaser()

	def seek( self, player, position, callback ):
		"""
		@type		player			  : instance
		@param		player			  : player role
		@type		position		  : float
		@param		position		  : seek position
		@type		callback		  : callback functor
		@param		callback		  : 当pursue结束时回调，该回调必须有两个参数，分别是 position, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		self.stop()

		if self._travelUnblocked(player, position):
			return self._seeker.seek(player, position, callback)
		else:
			return False

	def chase( self, chaser, target, nearby, callback = None ):
		"""
		@type		chaser			  : instance
		@param		chaser			  : entity of chaser
		@type		target			  : instance
		@param		target			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		callback		  : callback functor
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是entity, targetEntity, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		if self._seeker.running():
			self._seeker.stop()

		if self._travelUnblocked(chaser, target.position):
			self._chaser.chase(chaser, target, nearby, callback)
			return True
		else:
			return False

	def stop( self ):
		if self._seeker.running():
			self._seeker.stop()
		if self._chaser.running():
			self._chaser.stop()

	def running( self ):
		return self._seeker.running() or self._chaser.running()

	def _travelUnblocked( self, entity, dst ):
		"""检测entity到目标位置之间是否有阻挡"""
		src = Math.Vector3(entity.position)
		src.y += 0.5									# 最高能跨越0.5米高的障碍（实际测试的数据，不精确，非官方）
		dst = Math.Vector3(dst)
		dst.y = src.y
		return BigWorld.collide(entity.spaceID, src, dst) == None


#---------------------------------------------------------------------
# Implement StraightSeeker
#---------------------------------------------------------------------
class StraightSeeker:

	def __init__( self ):
		self._running = False
		self._wref_player = None
		self._destination = None
		self._callbackFunc = None
		self._collisionDetector = CollisionDetector()

	def seek( self, player, position, callback ):
		"""开始移动"""
		self.stop()

		physics = player.physics
		if physics:
			self._wref_player = weakref.ref(player)
			self._destination = position
			self._callbackFunc = callback

			physics.setSeekCallBackFn( None )	# 把旧的回调清除，防止调用seek时触发旧回调
			physics.setSeekCollisionCallBackFn( self._onSeekCollisionCallback )
			player.startMove()
			player.seek(position, 1000, self._onSeekCallback)

			self._collisionDetector.start(player, self._onSeekCollided)

			self._running = True
			return True
		return False

	def stop( self ):
		"""停止移动"""
		self._shutDown()
		self._feedBack(STRAIGHT_MOVE_CANCEL)

	def running( self ):
		"""是否在启动中"""
		return self._running

	def _feedBack( self, result ):
		if self._callbackFunc is not None:
			callback = self._callbackFunc
			self._callbackFunc = None
			callback(result)

	def _shutDown( self ):
		"""关闭所有侦测，停止移动"""
		self._running = False
		self._collisionDetector.stop()
		if self._wref_player is not None:
			player = self._wref_player()
			if player is not None:
				physics = player.physics
				physics.setSeekCallBackFn( None )
				physics.setSeekCollisionCallBackFn( None )
				physics.seek(None, 0, 0, None)						# 必须用这个方式让entity停止移动，否则会出问题。例如移动过程按下其他方向键，
				physics.stop()										# entity不会马上停止移动，而是走到目标点了才往指定的方向移动。

	def _onSeekCallback( self, success ):
		"""seek的回调"""
		self._shutDown()
		if success:
			self._feedBack(STRAIGHT_MOVE_SUCCESS)
		else:
			self._feedBack(STRAIGHT_MOVE_COLLIDE)

	def _onSeekCollisionCallback( self ):
		"""seek过程发生被卡住时回调"""
		pass

	def _onSeekCollided( self ):
		"""collision detector 侦测到被卡住时回调"""
		self._shutDown()
		self._feedBack(STRAIGHT_MOVE_COLLIDE)


#---------------------------------------------------------------------
# Implement StraightChaser
#---------------------------------------------------------------------
class StraightChaser:

	def __init__( self ):
		self._wref_chaser = None
		self._wref_target = None
		self._running = False
		self._chaseNearby = 0.0
		self._chaseCallback = None
		self._chaseTimerID = 0
		self._collisionDetector = CollisionDetector()

	#	# public ----------------------------------------------------
	# ---------------------------------------------------------------
	def chase( self, chaser, target, nearby, callback = None ):
		"""
		@type		chaser			  : instance
		@param		chaser			  : chaser entity
		@type		target			  : instance
		@param		target			  : entity chaser want to chase
		@type		nearby			  : float
		@param		nearby			  : at the distance indicated by nearby considered arriving.
		@type		callback		  : callback functor
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是entity, targetEntity, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		self._wref_chaser = weakref.ref(chaser)
		self._wref_target = weakref.ref(target)
		self._chaseNearby = nearby
		self._chaseCallback = callback

		self._running = True
		self._collisionDetector.start(chaser, self._onChaseCollided)
		self._addChaseTimer()

	def stop( self ):
		"""停止移动"""
		self._shutDown()
		self._chaseCallback = None

	def running( self ):
		"""是否在启动中"""
		return self._running

	def _shutDown( self ):
		"""关闭所有侦测，停止移动"""
		self._running = False
		self._cancelChaseTimer()
		self._collisionDetector.stop()
		if self._wref_chaser is not None:
			chaser = self._wref_chaser()
			if chaser is not None:
				physics = chaser.physics
				physics.setSeekCallBackFn( None )
				physics.seek(None, 0, 0, None)						# 必须用这个方式让entity停止移动，否则会出问题。例如移动过程按下其他方向键，
				physics.stop()										# entity不会马上停止移动，而是走到目标点了才往指定的方向移动。

	def _onChaseTimer( self ):
		"""on chase timer callback"""
		if self._arrive():
			self._shutDown()
			self._feedBack(STRAIGHT_MOVE_SUCCESS)
		elif not self._chase():
			self._shutDown()
			self._feedBack(STRAIGHT_MOVE_CANCEL)

	def _addChaseTimer( self ):
		"""start a new chase timer"""
		self._cancelChaseTimer()
		self._chaseTimerID = Timer.addTimer( 0.0, 0.2, self._onChaseTimer )

	def _cancelChaseTimer( self ):
		"""cancel chase timer"""
		if self._chaseTimerID:
			Timer.cancel(self._chaseTimerID)
			self._chaseTimerID = 0

	def _arrive( self ):
		"""distance between chaser and target is less than chase nearby"""
		chaser = self._wref_chaser()
		if chaser is None:
			return False
		target = self._wref_target()
		if target is None:
			return False
		return chaser.position.distTo(target.position) <= self._chaseNearby

	def _feedBack( self, result ):
		"""invoke callback function to feed back result"""
		if self._chaseCallback is not None:
			callback = self._chaseCallback
			self._chaseCallback = None
			callback( self._wref_chaser(), self._wref_target(), result )

	def _chase( self ):
		"""chase the target"""
		chaser = self._wref_chaser()
		if chaser is None:
			return False
		target = self._wref_target()
		if target is None:
			return False
		chaser.physics.setSeekCallBackFn( None )	# 把旧的回调清除，防止调用seek时触发旧回调
		chaser.updateVelocity()
		dir = chaser.position - target.position 
		dir.normalise()
		desPos = target.position + dir * self._chaseNearby
		chaser.seek( desPos, 1000, self._onSeekCallback )
		return True

	def _onSeekCallback( self, success ):
		"""seek callback"""
		self._shutDown()
		if success:
			self._feedBack(STRAIGHT_MOVE_SUCCESS)
		else:
			self._feedBack(STRAIGHT_MOVE_COLLIDE)

	def _onChaseCollided( self ):
		"""collision detector 侦测到被卡住时回调"""
		self._shutDown()
		self._feedBack(STRAIGHT_MOVE_COLLIDE)


#---------------------------------------------------------------------
# Implement CollisionDetector
#---------------------------------------------------------------------
class CollisionDetector:

	_DETECT_INTERVAL = 0.2						# 侦测回调频率（秒/次）
	_VALID_TRAVEL_RATE = 0.5					# 实际路程和理论路程的有效比率
	_COLLISION_TOLERANCE = 2					# 连续被卡住的最大容忍次数

	def __init__( self ):
		self._wref_entity = None
		self._collisionCallback = None
		self._counter = 0
		self._detectTimerID = 0
		self._lastPos = None
		self._lastTime = 0

	def start( self, entity, callback ):
		self._wref_entity = weakref.ref(entity)
		self._collisionCallback = callback

		self._counter = 0
		self._lastPos = entity.position
		self._lastTime = time.time()
		self._addDetectTimer()

	def stop( self ):
		self._collisionCallback = None
		self._cancelDetectTimer()

	def updateSpeed( self, speed ):
		pass

	def _addDetectTimer( self ):
		self._cancelDetectTimer()
		self._detectTimerID = BigWorld.callback(self._DETECT_INTERVAL, self._onDetectTimer)

	def _cancelDetectTimer( self ):
		if self._detectTimerID != 0:
			BigWorld.cancelCallback(self._detectTimerID)
			self._detectTimerID = 0

	def _onDetectTimer( self ):
		entity = self._wref_entity()
		if entity:
			now = time.time()
			passTime = now - self._lastTime
			desiredTravel = passTime * entity.getSpeed()
			actualTravel = entity.position.distTo(self._lastPos)

			if actualTravel/desiredTravel <= self._VALID_TRAVEL_RATE:	# 当实际路程跟理论路程相差超过一定范围时，
				self._counter += 1										# 计数器自动增长，
			else:
				self._counter = 0										# 否则计数器清除。

			if self._counter >= self._COLLISION_TOLERANCE:				# 如果出现连续几次实际路程跟理论路程相差超过一定范围时，
				self._onCollision()										# 报告被卡住。
			else:
				self._lastPos = entity.position
				self._lastTime = now
				self._addDetectTimer()
		else:
			self._cancelDetectTimer()
			self._onCollision()

	def _onCollision( self ):
		callback = self._collisionCallback
		self._collisionCallback = None
		if callable( callback ):
			callback()

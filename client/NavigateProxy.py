# -*- coding: gb18030 -*-

# written by gjx 2013/6/13

import weakref
import BigWorld
import Timer
from bwdebug import *
from navigate import NavigateEx, NavDataMgr

_callback_1args = lambda arg1 : None
_callback_2args = lambda arg1, arg2 : None
_callback_3args = lambda arg1, arg2, arg3 : None

class INavigator:

	#	# public ----------------------------------------------------
	# ---------------------------------------------------------------
	def pursueEntity( self, entity, nearby, speed, callback = _callback_3args ):
		"""
		pursue entity
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		speed			  : float
		@param		speed			  : 追踪速度
		@type		callback		  : callback functor
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是entity, targetEntity, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		pass

	def pursuePosition( self, pos, nearby, speed, callback = _callback_3args ) :
		"""
		pursue entity
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		speed			  : float
		@param		speed			  : 追踪速度
		@type		callback		  : callback functor
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是entity, targetEntity, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		pass

	def updateVelocity( self, speed ) :
		"""
		刷新速度
		"""
		pass

	def isMoving( self ):
		"""是否正在移动：追踪或者跟随"""
		return False

	def stop( self ) :
		"""
		停止一切navigate移动
		"""
		pass

	def slipping( self ):
		"""是否在滑动状态，引擎有个问题"""
		return False


# **
# 寻路行为代理，客户端使用NavigateEx处理entity的寻路
# 行为，并且要求entity提供使用NavigateEx所必须的属性
# 和接口，为了让entity不用去关心这些特定相关的属性和
# 接口，使用这个代理对entity进行封装，作为entity的寻
# 路代理传给NavigateEx，从而将entity和NavigateEx的耦
# 合度降至最低。
# 注意：只适合在客户端有physics的entity。
#
# 与委托者(consigner)约定的属性：
# position	: Vector3
# spaceID	: int
# yaw		: float
# physics	: Physics
# **
class NavigateProxy(INavigator):
	"""客户端寻路代理，负责操纵navigate控制客户端entity
	移动，追踪，必须是客户端控制的entity才有效"""

	def __init__( self, consigner ):
		self._isPursue = False
		self._pursueSpeed = 0.0
		self._seekCallback = None
		self._consigner = weakref.proxy(consigner)
		self._navigator = NavigateEx(self)

#	# methods and properties referenced by navigator  ---------------
	# ---------------------------------------------------------------
	@property
	def position( self ):
		return self._consigner.position

	@property
	def spaceID( self ):
		return self._consigner.spaceID

	@property
	def yaw( self ):
		return self._consigner.yaw

	def onNavigateExNoPathFind( self, navExState ):
		pass

	def endAutoRun( self, state ) :
		"""
		自动寻路是否到达目的地的回调通知，可以在此做一些事情
		@type    state: bool
		@param   state: 是否成功到达目的地
		"""
		pass

	def getPhysics( self ):
		"""
		获取physics
		"""
		return getattr(self._consigner, "physics", None)

	def onPursueOver( self, success ):
		"""
		提供给navigator回调的方法
		"""
		self.stop()

	def seek( self, position, verticalRange, callback, isSeekToGoal = True ) :
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
		self._seekCallback = callback
		x, y, z = position
		decVector = position - self.position
		distance = decVector.length
		timeout = 0
		physics = self.getPhysics()
		try:
			timeout = 3 * distance / self._pursueSpeed
		except ZeroDivisionError:
			ERROR_MSG( "you can't move, your speed value is zero!" )

		physics.velocity = ( 0.0, 0.0, self._pursueSpeed )
		destination = ( x, y, z, decVector.yaw )
		physics.seek( destination, timeout, verticalRange, self._onSeekCallback, True )

	def isPursueState( self ):
		"""
		提供给navigator检测entity pursue状态的方法
		"""
		return self._isPursue

	# ---------------------------------------------------------------
	# end - methods and properties referenced by navigator
	# ---------------------------------------------------------------

#	# seek callback -------------------------------------------------
	# ---------------------------------------------------------------
	def _onSeekCallback( self, isSuccess ):
		"""physics的seek的回调方法"""
		physics = self.getPhysics()
		if physics:
			physics.stop()								# 为防止滑动，寻路到达时，马上停止一切移动
		if callable(self._seekCallback):
			self._seekCallback(isSuccess)

#	# pursue --------------------------------------------------------
	# ---------------------------------------------------------------
	def pursueEntity( self, entity, nearby, speed, callback = _callback_3args ):
		"""
		pursue entity
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		speed			  : float
		@param		speed			  : 追踪速度
		@type		callback		  : callback functor
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是entity, targetEntity, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		self.stop()
		self._isPursue = True
		self.updateVelocity(speed)
		#self._pursueCallback = callback
		# 因为传入navigate的callback是以BigWorld.callable(0, callback)的异步方式
		# 回调的，会出现很多异步问题，因此在同步回调方法onPursueOver中通知回调
		self._navigator.pursueEntity( entity, nearby, callback )

	def pursuePosition( self, pos, nearby, speed, callback = _callback_3args ) :
		"""
		pursue entity
		@type		entity			  : instance
		@param		entity			  : entity you want to pursue
		@type		nearby			  : float
		@param		nearby			  : move to the position nearby target
		@type		speed			  : float
		@param		speed			  : 追踪速度
		@type		callback		  : callback functor
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是entity, targetEntity, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		self.stop()
		self._isPursue = True
		self.updateVelocity(speed)
		#self._pursueCallback = callback
		# 因为传入navigate的callback是以BigWorld.callable(0, callback)的异步方式
		# 回调的，会出现很多异步问题，因此在同步回调方法onPursueOver中通知回调
		self._navigator.pursuePosition( pos, nearby, callback )

	def updateVelocity( self, speed ) :
		"""
		刷新速度
		"""
		self._pursueSpeed = speed
		self.getPhysics().velocity = ( 0.0, 0.0, speed )

	def isMoving( self ):
		"""是否正在移动：追踪或者跟随"""
		return self._navigator.isRunning()

	def stop( self ) :
		"""
		停止一切navigate移动
		"""
		self._isPursue = False
		self._pursueSpeed = 0.0
		self._seekCallback = None
		if self._navigator.isRunning():
			self._navigator.forceStop()
		physics = self.getPhysics()
		if physics:
			physics.setSeekCallBackFn( None )
			physics.seek( None, 0, 0, None )
			physics.stop()

	def slipping( self ):
		"""是否在滑动状态，引擎有个问题：
		如果physics的velocity的任一个方向有速度，
		并且当前不是seeking或者chasing状态，则绑
		定到physics的entity就会处于滑动的状态"""
		physics = self.getPhysics()
		return physics\
			and not physics.seeking\
			and not physics.chasing\
			and (physics.velocity.x > 0.0\
				or physics.velocity.z > 0.0)


# **
# 负责对追踪目标、跟随目标的行为进行封装，让这些行为
# 对使用者是透明的，使用者通过调用对应的方法获得期望
# 的行为效果，也能传入回调得知行为结果，但不需要关心
# 具体的行为是如何开展的
# **
class Chaser:
	"""追踪器"""

	def __init__( self, consigner, navigator ):
		self._consigner = weakref.proxy(consigner)
		assert isinstance(navigator, INavigator), "navigator must be instance of INavigator"
		self._navigator = navigator

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def chaseEntity( self, entity, nearby, speed, callback = _callback_3args ):
		"""追踪目标"""
		self.stop()
		self._chaseEntity(entity, nearby, speed, callback)

	def chasePosition( self, pos, nearby, speed, callback = _callback_3args ):
		"""追踪地点"""
		self.stop()
		self._chasePosition(pos, nearby, speed, callback)

	def crossAreaChase( self, pos, nearby, speed, dstSpaceLabel, callback = _callback_2args ):
		"""跨区域地点追踪"""
		assert 0, "Not yet provided."

	def updateSpeed( self, speed ):
		"""更新追踪速度"""
		if self.isMoving():
			self._navigator.updateVelocity(speed)

	def isMoving( self ):
		"""是否正在移动中"""
		return self._navigator.isMoving()

	def slipping( self ):
		"""是否正在滑动（漂移）的状态"""
		return self._navigator.slipping()

	def stop( self ):
		"""停止追踪和跟随行为"""
		self._navigator.stop()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def _chaseEntity( self, entity, nearby, speed, callback = _callback_3args ):
		"""追踪目标，仅仅负责发起追踪，不记录参数"""
		self._navigator.pursueEntity(entity, nearby, speed, callback)

	def _chasePosition( self, pos, nearby, speed, callback = _callback_3args ):
		"""追踪地点，仅仅负责发起追踪，不记录参数"""
		self._navigator.pursuePosition(pos, nearby, speed, callback)


class FollowChaser( Chaser ):
	"""带跟随功能的追踪器，不要直接使用这个追踪器
	因为这个追踪器还未实现跟随的功能，只作为基类使用"""

	def __init__( self, consigner, navigator ):
		Chaser.__init__( self, consigner, navigator )
		self._pausing = False
		self._followSpeed = 0.0
		self._followNearby = 0.0
		self._followTarget = None
		self._followNotifier = None

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def followEntity( self, entity, nearby, speed, callback = _callback_1args ):
		"""跟随目标"""
		self.stop()
		self._followSpeed = speed
		self._followNearby = nearby
		self._followTarget = weakref.ref(entity)
		self._followNotifier = callback					# 注意，这里可能产生交叉引用
		self.resumeFollow()

	def resumeFollow( self ):
		"""唤醒暂停的跟随"""
		self._pausing = False

	def pauseFollow( self ):
		"""暂停跟随，不取消当前的跟随目标"""
		self._pausing = True

	def isFollowing( self ):
		"""是否正在跟随中"""
		return False

	def updateSpeed( self, speed ):
		"""更新追踪速度"""
		self._followSpeed = speed
		if self.isMoving():
			self._navigator.updateVelocity(speed)

	def stop( self ):
		"""停止追踪和跟随行为"""
		Chaser.stop(self)
		self._pausing = False
		self._followSpeed = 0.0
		self._followNearby = 0.0
		self._followNotifier = None
		self._followTarget = None

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def _arrive( self, pos ):
		"""是否到达pos"""
		return self._consigner.position.distTo(pos) <= self._followNearby

	def _onFollowBroken( self ):
		"""跟随中断"""
		if callable(self._followNotifier):
			target = self._followTarget()
			self._followNotifier(target and target.id or None)


class CallbackChaser( FollowChaser ):
	"""由周期回调驱动的跟随追踪"""

	def __init__( self, consigner, navigator ):
		FollowChaser.__init__(self, consigner, navigator)
		self._cbInterval = 0.5						# 回调间隔
		self._callbackID = None

	def stop( self ):
		"""停止追踪和跟随行为"""
		FollowChaser.stop(self)
		self._cancelFollowCallback()

	def resumeFollow( self ):
		"""唤醒暂停的跟随"""
		FollowChaser.resumeFollow(self)
		self._resumeFollowCallback()

	def pauseFollow( self ):
		"""暂停跟随，不取消当前的跟随目标"""
		FollowChaser.pauseFollow(self)
		self._navigator.stop()
		self._cancelFollowCallback()

	def isFollowing( self ):
		"""是否正在跟随中"""
		return self._callbackID != None

	def _onFollowCallback( self ):
		"""跟随回调检测"""
		target = self._followTarget()
		if target and BigWorld.entities.has_key(target.id) and\
			target.spaceID == self._consigner.spaceID:
				if not self._arrive(target.position):
					self._chaseEntity(target, self._followNearby, self._followSpeed)
				if not self._pausing:
					self.resumeFollow()
		else:
			self._onFollowBroken()

	def _cancelFollowCallback( self ):
		"""取消跟随回调"""
		if self._callbackID != None:
			BigWorld.cancelCallback(self._callbackID)
			self._callbackID = None

	def _resumeFollowCallback( self ):
		"""开启跟随回调"""
		self._cancelFollowCallback()
		self._callbackID = BigWorld.callback(self._cbInterval, self._onFollowCallback)


class ITimer:

	def __init__( self ):
		self._cbInterval = 0.5						# 回调间隔
		self._callbackID = None

	def resume( self ):
		self.cancel()
		self._callbackID = BigWorld.callback(self._cbInterval, self._onCallback)

	def cancel( self ):
		if self._callbackID != None:
			BigWorld.cancelCallback(self._callbackID)
			self._callbackID = None

	def _onCallback( self ):
		pass

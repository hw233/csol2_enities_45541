# -*- coding: gb18030 -*-

import weakref
import random
import math
import time
import Math
import utils
import Timer
import BigWorld
from bwdebug import *
from Function import Functor
from navigate import NavDataMgr
from NavigateProxy import FollowChaser, INavigator, _callback_3args


class PetNavigator(INavigator):

	SYNC_INTERVAL = 0.1										# 每隔多少秒向服务器同步位置

	def __init__( self, consigner ):
		self._consigner = weakref.proxy(consigner)
		self._navPaths = []									# 寻路系统生成的全部寻路点
		self._sectPaths = []								# 当前路段拆分后的路点
		self._syncTimer = None								# 往服务器同步位置的timer
		self._chaseTimer = None								# 追踪entity的timer
		self._pursueSpeed = 0.0
		self._pursueNearby = 0.0
		self._pursueTarget = None
		self._pursueCallback = None
		self._latestSyncPos = consigner.position			# 记录最近一次同步的位置
		self._latestSyncTime = 0.0
		self._latestActualPos = consigner.position			# 记录同步之前consigner的实际位置

#	# protected -----------------------------------------------------
	# ---------------------------------------------------------------
	def _verifySyncPos( self ):
		"""验证最后一次同步的位置，防止出现传送等导致
		实际位置与客户端最后同步的位置不一致的情况"""
		if time.time() - self._latestSyncTime > 1.0 and\
			self._latestSyncPos.distTo(self._consigner.position) > 0.5:
				self._latestSyncPos = self._consigner.position

	def _verifyActualPos( self ):
		"""验证实际的位置，防止出现在移动过程中发生传送等导致
		实际位置与客户端最后同步的位置不一致的情况，验证规则：
		目前的实际位置与上次同步前记下的位置距离较远并且与上次
		同步的位置也距离较远，判定为验证失败"""
		return True
		curPos = self._consigner.position
		if self._latestActualPos.distTo(curPos) > 0.5 and\
			self._latestSyncPos.distTo(curPos) > 0.5:
				return False
		return True

	def _moveTo( self, dstPos, step, interval ) :
		"""采用往服务器同步位置的方式，移动到目标位置
		@param dstPos	: Vector3, 目标位置
		@param step		: Float, 每次移动的距离
		@param interval	: Float, 每隔多少秒往服务器同步一次
		"""
		self._stopSync()
		self._sectPaths = self._splitPath(self._latestSyncPos, dstPos, step)
		self._syncTimer = Timer.addTimer(0.0, 0.01, self._onSyncTimer)

	def _onSyncTimer( self ):
		"""位置同步timer回调"""
		if self._arriveGoal():
			self._stopAndCallback(True)
		elif self._sectPaths:
			now = time.time()
			if now - self._latestSyncTime >= self.SYNC_INTERVAL:
				pos = self._sectPaths.pop(0)
				self._syncPosition(pos)
		else:
			self._navigate()

	def _syncPosition( self, position ):
		"""执行同步位置操作"""
		consigner = self._consigner
		self._latestSyncTime = time.time()
		self._latestActualPos = consigner.position
		self._latestSyncPos = utils.posOnGround(consigner.spaceID, position, default=position)
		consigner.onWaterPosToServer( position )

	def _splitPath( self, srcPos, dstPos, step ):
		"""将两点之间的直线路径拆分成长度为step的多段路径"""
		paths = []
		dir = dstPos - srcPos
		dir.normalise()
		length = srcPos.distTo(dstPos)
		amount = int(length/step)
		for i in xrange(1, amount + 1):
			pos = srcPos + (i * step * dir)
			paths.append(pos)
		if length % step != 0:
			paths.append(dstPos)
		return paths

	def _stopSync( self ):
		"""停止同步timer"""
		if self._syncTimer:
			Timer.cancel(self._syncTimer)
			self._syncTimer = None

	def _generatePaths( self, goalPos ):
		"""生成寻路路径"""
		navMgr = NavDataMgr.instance()
		self._navPaths = navMgr.tryBestFindPath( self._latestSyncPos, goalPos, self._consigner.spaceID )
		# 如果无法从上次同步位置找到到达目标位置的路径，则尝试以下方式，
		# 在起始点（即上次同步的位置）附近抽取一个随机位置，重新搜索路径
		# 在尝试了一定次数后还是无法找到可行路径，则宣布失败
		if len(self._navPaths) == 0:
			for i in xrange(5):
				adjustPos = self._adjustPosition(self._latestSyncPos, 0.5, 1.0)
				adjustPos = utils.posOnGround(self._consigner.spaceID, adjustPos)
				if adjustPos is None:
					continue
				self._navPaths = navMgr.tryBestFindPath( adjustPos, goalPos, self._consigner.spaceID )
				if len(self._navPaths) > 0:
					break
		return len(self._navPaths) > 0

	def _adjustPosition( self, pos, minR, maxR ):
		"""以pos为圆心，在最小半径minR和最大半径maxR
		之间的区域内找到一个随机位置"""
		ranYaw = random.random() * math.pi * 2
		ranRad = minR + (maxR - minR) * random.random()
		newPos = Math.Vector3(pos)
		newPos.x = pos.x + ranRad * math.sin(ranYaw)
		newPos.z = pos.z + ranRad * math.cos(ranYaw)
		return newPos

	def _navigate( self ):
		"""寻路移动"""
		if self._navPaths:
			goalPos = self._navPaths.pop(0)
			step = self.SYNC_INTERVAL * self._pursueSpeed			# 根据追踪速度和同步频率计算相邻两次同步位置的间距
			self._moveTo(goalPos, step, self.SYNC_INTERVAL)
		else:
			self._stopAndCallback(True)

	def _enterChasing( self ):
		"""进入追踪目标"""
		self._stopChasing()
		self._chaseTimer = Timer.addTimer(0.1, 0.5, self._onChasing)

	def _onChasing( self ):
		"""追踪目标timer回调"""
		if self._arrive(self._pursueTarget.position):
			self._stopAndCallback(True)
		elif self._generatePaths(self._pursueTarget.position):
			self._navigate()
		else:
			self._stopAndCallback(False)

	def _stopChasing( self ):
		"""停止追踪目标"""
		if self._chaseTimer:
			Timer.cancel(self._chaseTimer)
			self._chaseTimer = None

	def _arrive( self, goalPos ):
		"""是否到达指定位置"""
		return self._consigner.position.distTo(goalPos) <= self._pursueNearby

	def _arriveGoal( self ):
		"""是否到达目标位置"""
		if type(self._pursueTarget) is Math.Vector3:
			return self._arrive(self._pursueTarget)
		elif self._pursueTarget:
			return self._arrive(self._pursueTarget.position)
		else:
			return False

	def _stopAndCallback( self, result ):
		"""回调并停止一切移动"""
		target = self._pursueTarget
		callback = self._pursueCallback
		self.stop()
		if callback:
			BigWorld.callback(0, Functor(callback, self._consigner, target, result))
			#callback(self._consigner, target, result)

#	# public --------------------------------------------------------
	# ---------------------------------------------------------------
	def teleportPosition( self, position ):
		"""将宠物传送到指定位置"""
		self.stop()
		self._syncPosition(position)

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
		self.updateVelocity(speed)
		self._pursueNearby = nearby
		self._pursueTarget = entity
		self._pursueCallback = callback
		self._verifySyncPos()
		self._enterChasing()

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
		@param		callback		  : 当pursue结束时回调，该回调必须有三个参数，分别是entity, targetPosition, success，
										success为bool值，True表示追踪成功，否则表示失败；
										如果targetEntity值为None则表示目标已不存在；
		@return						  : None
		"""
		self.stop()
		self.updateVelocity(speed)
		self._pursueNearby = nearby
		self._pursueTarget = pos
		self._pursueCallback = callback
		self._verifySyncPos()
		if self._generatePaths(pos):
			self._navigate()
		else:
			self._stopAndCallback(False)

	def updateVelocity( self, speed ) :
		"""
		刷新速度
		"""
		self._pursueSpeed = speed
		if len(self._sectPaths) > 1:
			nextPos = self._sectPaths[0]
			goalPos = self._sectPaths[-1]
			step = self.SYNC_INTERVAL * self._pursueSpeed
			self._sectPaths = self._splitPath(nextPos, goalPos, step)
			self._sectPaths.insert(0, nextPos)

	def isMoving( self ):
		"""是否正在移动：追踪或者跟随"""
		return self._syncTimer != None

	def stop( self ) :
		"""
		停止一切navigate移动
		"""
		self._stopSync()
		self._stopChasing()
		self._pursueSpeed = 0.0
		self._pursueNearby = 0.0
		self._pursueTarget = None
		self._pursueCallback = None
		self._navPaths = []
		self._sectPaths = []

	def slipping( self ):
		""""""
		return False

	@property
	def latestSyncPos( self ):
		"""最后向服务器同步的位置"""
		return self._latestSyncPos


class PetChaser( FollowChaser ):
	"""宠物专用追踪器，跟随处理有一个特点：
	将跟随追踪过程分开为两个阶段，第一个是
	预追踪阶段，追踪的目标位置离真正的位置
	还有一小段距离，这小段距离留给第二段用
	一个较低的速度跟上"""
	PREV_CHASE_OFFSET = 0.6						# 预追踪阶段，到距离目标位置多远时停一下，再用低速跟上
	PREV_CHASE_NEARBY = 3.0						# 预追踪阶段设定的离目标点多远时认为到达的距离
	DST_HEIGHT_TOLERANCE = 3.0					# 移动的目标位置高度方向上与跟随目标的最大差值

	def __init__( self, consigner, navigator ):
		FollowChaser.__init__(self, consigner, navigator)
		self._potID = None
		self._timer = None
		self._prevChasePos = None
		self._prevChaseSpeed = 0.0
		self._prevChaseNearby = 0.0

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def teleportPosition( self, position ):
		"""同地图将宠物传送到指定位置"""
		self._navigator.teleportPosition(position)
		self.stop()

	def resumeFollow( self ):
		"""唤醒暂停的跟随"""
		FollowChaser.resumeFollow(self)
		self._addPot(self._followNearby)
		self._addTimer()

	def pauseFollow( self ):
		"""暂停跟随，不取消当前的跟随目标"""
		FollowChaser.pauseFollow(self)
		self._delPot()
		self._cancelTimer()
		self._navigator.stop()

	def isFollowing( self ):
		"""是否正在跟随中"""
		return self._potID != None

	def stop( self ):
		"""停止追踪和跟随行为"""
		FollowChaser.stop(self)
		self._delPot()
		self._cancelTimer()
		self._navigator.stop()
		self._prevChasePos = None
		self._prevChaseSpeed = 0.0
		self._prevChaseNearby = 0.0

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def _calcPrevChaseNearbyMax( self ):
		"""预追踪阶段距离目标多远认为到达的距离的最大值"""
		return self._followNearby - self._followTarget().position.distTo(self._prevChasePos)

	def _calcPrevChaseNearby( self ):
		"""更新预追踪阶段距离目标多远认为到达的距离的最大值"""
		return min(self.PREV_CHASE_NEARBY, self._calcPrevChaseNearbyMax())

	def _stayRange( self ):
		"""追踪目标位置的偏移"""
		return self._followNearby*0.6

	def _searchPrevFollowPosition( self ):
		"""搜索预追踪位置"""
		target = self._followTarget()
		pos = self._getFollowPosition()
		pos = self._formatPosition(pos, target.yaw, -self.PREV_CHASE_OFFSET)
		pos = utils.posOnGround(target.spaceID, pos)
		# 如果在上下指定高度上没有地面点或者位置判断为无效，则让尝试让跟在目标身后
		if pos is None or self._dstInvalid(pos):
			pos = self._formatPosition(target.position, target.yaw, -self._stayRange())
			pos = utils.posOnGround(target.spaceID, pos, default=target.position)
			# 如果在目标身后也取不到合适的点，则直接跟到目标的位置
			if self._dstInvalid(pos):
				pos = target.position
		return pos

	def _getFollowPosition( self ):
		"""获取追踪位置"""
		target = self._followTarget()
		if target:
			return self._formatPosition(target.position, target.yaw+math.pi/2, self._stayRange())
		else:
			return self._consigner.position

	def _formatPosition( self, pos, yaw, offset ):
		"""根据yaw和offset计算新的位置"""
		rx, ry, rz = pos
		x = rx + offset * math.sin(yaw)
		z = rz + offset * math.cos(yaw)
		return Math.Vector3( x, ry, z )

	def _dstInvalid( self, dstPosition ):
		"""检查目标位置是否不合适"""
		targetPosition = self._followTarget().position
		# 检测目标位置是否不在nearby范围之内
		if targetPosition.distTo(dstPosition) > self._followNearby:
			return True
		# 检测目标位置与跟随目标的位置的高度差是否过大
		if abs(dstPosition.y - targetPosition.y) > self.DST_HEIGHT_TOLERANCE:
			return True
		# 检测目标位置与跟随目标的位置在水平方向上是否隔着带碰撞的物体，
		# 以此判断宠物可能会走进墙体或者遮挡后面
		apos = Math.Vector3(targetPosition)
		apos.y += self._followTarget().getBoundingBox().y/2.0
		# 取中心高度位置
		bpos = Math.Vector3(dstPosition)
		bpos.y += self._consigner.getBoundingBox().y/2.0
		# 用两个点进行碰撞检测，看是否有阻隔
		if BigWorld.collide(self._followTarget().spaceID, apos, bpos) != None:
			return True
		return False

	def _chaseFollowTarget( self ):
		"""追踪跟随的目标"""
		self._chasePosition(self._prevChasePos, self._prevChaseNearby, self._prevChaseSpeed, self._onChasePosOver)

	def _updatePrevChase( self ):
		"""更新预追踪位置和速度"""
		self._prevChasePos = self._searchPrevFollowPosition()
		# 预追踪位置重新获取后，重新计算最大跟随到达距离
		self._prevChaseNearby = self._calcPrevChaseNearby()
		# 速度设置：1.2秒之内能跟上目标的速度和设定的跟随速度之中的较大值
		self._prevChaseSpeed = max(self._followSpeed, self._consigner.position.distTo(self._prevChasePos)/1.2)

	def _onChasePosOver( self, owner, pos, success ):
		"""追踪位置结束"""
		target = self._followTarget() if self._followTarget else None
		if target is None:
			self._cancelTimer()
		elif self._arrive(target.position):
			dstPos = self._formatPosition(pos, target.yaw, self.PREV_CHASE_OFFSET - 0.1)
			dstPos = utils.posOnGround(target.spaceID, dstPos, default=pos)
			# 目标位置有效性检查
			if self._dstInvalid(dstPos):
				dstPos = self._formatPosition(target.position, target.yaw, -self._stayRange())
				dstPos = utils.posOnGround(target.spaceID, dstPos, default=target.position)
				# 如果在目标身后也取不到合适的点，则直接跟到目标的位置
				if self._dstInvalid(dstPos):
					dstPos = target.position
			self._chasePosition(dstPos, 0.2, 1.2)			# 追踪到目的地后，让宠物根据目标的朝向继续前进，以调整宠物的朝向
			self.stop()
		elif success:										# 当回调成功而实际却未到达时，马上启动追踪，否则等下一次timer，防止因找不到路径导致客户端卡住
			self._updatePrevChase()
			self._chaseFollowTarget()

	# -------------------------------------------------
	# protected for pot trigger
	# -------------------------------------------------
	def _addPot( self, radius ):
		"""添加一个专门针对PlayerRole的陷阱"""
		self._delPot()
		self._potID = BigWorld.addPot(self._consigner.matrix, radius, self._onPotHit)

	def _delPot( self ):
		"""移除陷阱"""
		if self._potID is not None:
			BigWorld.delPot(self._potID)
			self._potID = None

	def _onPotHit( self, enteredPot, handle ):
		"""陷阱触发"""
		if not enteredPot and not self._pausing:
			self._addTimer()

	# -------------------------------------------------
	# protected for callback
	# -------------------------------------------------
	def _addTimer( self ):
		"""开始追踪后启动timer不停追踪目标，以避免宠物
		被拉向一边的问题"""
		self._cancelTimer()
		self._timer = Timer.addTimer( 0.1, 1.0, self._onTimer )

	def _cancelTimer( self ):
		if self._timer is not None:
			Timer.cancel(self._timer)
			self._timer = None

	def _onTimer( self ):
		"""回调到达，继续追踪目标位置"""
		self._updatePrevChase()
		self._chaseFollowTarget()

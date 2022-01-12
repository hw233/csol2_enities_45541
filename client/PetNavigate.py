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

	SYNC_INTERVAL = 0.1										# ÿ���������������ͬ��λ��

	def __init__( self, consigner ):
		self._consigner = weakref.proxy(consigner)
		self._navPaths = []									# Ѱ·ϵͳ���ɵ�ȫ��Ѱ·��
		self._sectPaths = []								# ��ǰ·�β�ֺ��·��
		self._syncTimer = None								# ��������ͬ��λ�õ�timer
		self._chaseTimer = None								# ׷��entity��timer
		self._pursueSpeed = 0.0
		self._pursueNearby = 0.0
		self._pursueTarget = None
		self._pursueCallback = None
		self._latestSyncPos = consigner.position			# ��¼���һ��ͬ����λ��
		self._latestSyncTime = 0.0
		self._latestActualPos = consigner.position			# ��¼ͬ��֮ǰconsigner��ʵ��λ��

#	# protected -----------------------------------------------------
	# ---------------------------------------------------------------
	def _verifySyncPos( self ):
		"""��֤���һ��ͬ����λ�ã���ֹ���ִ��͵ȵ���
		ʵ��λ����ͻ������ͬ����λ�ò�һ�µ����"""
		if time.time() - self._latestSyncTime > 1.0 and\
			self._latestSyncPos.distTo(self._consigner.position) > 0.5:
				self._latestSyncPos = self._consigner.position

	def _verifyActualPos( self ):
		"""��֤ʵ�ʵ�λ�ã���ֹ�������ƶ������з������͵ȵ���
		ʵ��λ����ͻ������ͬ����λ�ò�һ�µ��������֤����
		Ŀǰ��ʵ��λ�����ϴ�ͬ��ǰ���µ�λ�þ����Զ�������ϴ�
		ͬ����λ��Ҳ�����Զ���ж�Ϊ��֤ʧ��"""
		return True
		curPos = self._consigner.position
		if self._latestActualPos.distTo(curPos) > 0.5 and\
			self._latestSyncPos.distTo(curPos) > 0.5:
				return False
		return True

	def _moveTo( self, dstPos, step, interval ) :
		"""������������ͬ��λ�õķ�ʽ���ƶ���Ŀ��λ��
		@param dstPos	: Vector3, Ŀ��λ��
		@param step		: Float, ÿ���ƶ��ľ���
		@param interval	: Float, ÿ����������������ͬ��һ��
		"""
		self._stopSync()
		self._sectPaths = self._splitPath(self._latestSyncPos, dstPos, step)
		self._syncTimer = Timer.addTimer(0.0, 0.01, self._onSyncTimer)

	def _onSyncTimer( self ):
		"""λ��ͬ��timer�ص�"""
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
		"""ִ��ͬ��λ�ò���"""
		consigner = self._consigner
		self._latestSyncTime = time.time()
		self._latestActualPos = consigner.position
		self._latestSyncPos = utils.posOnGround(consigner.spaceID, position, default=position)
		consigner.onWaterPosToServer( position )

	def _splitPath( self, srcPos, dstPos, step ):
		"""������֮���ֱ��·����ֳɳ���Ϊstep�Ķ��·��"""
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
		"""ֹͣͬ��timer"""
		if self._syncTimer:
			Timer.cancel(self._syncTimer)
			self._syncTimer = None

	def _generatePaths( self, goalPos ):
		"""����Ѱ··��"""
		navMgr = NavDataMgr.instance()
		self._navPaths = navMgr.tryBestFindPath( self._latestSyncPos, goalPos, self._consigner.spaceID )
		# ����޷����ϴ�ͬ��λ���ҵ�����Ŀ��λ�õ�·�����������·�ʽ��
		# ����ʼ�㣨���ϴ�ͬ����λ�ã�������ȡһ�����λ�ã���������·��
		# �ڳ�����һ�����������޷��ҵ�����·����������ʧ��
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
		"""��posΪԲ�ģ�����С�뾶minR�����뾶maxR
		֮����������ҵ�һ�����λ��"""
		ranYaw = random.random() * math.pi * 2
		ranRad = minR + (maxR - minR) * random.random()
		newPos = Math.Vector3(pos)
		newPos.x = pos.x + ranRad * math.sin(ranYaw)
		newPos.z = pos.z + ranRad * math.cos(ranYaw)
		return newPos

	def _navigate( self ):
		"""Ѱ·�ƶ�"""
		if self._navPaths:
			goalPos = self._navPaths.pop(0)
			step = self.SYNC_INTERVAL * self._pursueSpeed			# ����׷���ٶȺ�ͬ��Ƶ�ʼ�����������ͬ��λ�õļ��
			self._moveTo(goalPos, step, self.SYNC_INTERVAL)
		else:
			self._stopAndCallback(True)

	def _enterChasing( self ):
		"""����׷��Ŀ��"""
		self._stopChasing()
		self._chaseTimer = Timer.addTimer(0.1, 0.5, self._onChasing)

	def _onChasing( self ):
		"""׷��Ŀ��timer�ص�"""
		if self._arrive(self._pursueTarget.position):
			self._stopAndCallback(True)
		elif self._generatePaths(self._pursueTarget.position):
			self._navigate()
		else:
			self._stopAndCallback(False)

	def _stopChasing( self ):
		"""ֹͣ׷��Ŀ��"""
		if self._chaseTimer:
			Timer.cancel(self._chaseTimer)
			self._chaseTimer = None

	def _arrive( self, goalPos ):
		"""�Ƿ񵽴�ָ��λ��"""
		return self._consigner.position.distTo(goalPos) <= self._pursueNearby

	def _arriveGoal( self ):
		"""�Ƿ񵽴�Ŀ��λ��"""
		if type(self._pursueTarget) is Math.Vector3:
			return self._arrive(self._pursueTarget)
		elif self._pursueTarget:
			return self._arrive(self._pursueTarget.position)
		else:
			return False

	def _stopAndCallback( self, result ):
		"""�ص���ֹͣһ���ƶ�"""
		target = self._pursueTarget
		callback = self._pursueCallback
		self.stop()
		if callback:
			BigWorld.callback(0, Functor(callback, self._consigner, target, result))
			#callback(self._consigner, target, result)

#	# public --------------------------------------------------------
	# ---------------------------------------------------------------
	def teleportPosition( self, position ):
		"""�����ﴫ�͵�ָ��λ��"""
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
		@param		speed			  : ׷���ٶ�
		@type		callback		  : callback functor
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���entity, targetEntity, success��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
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
		@param		speed			  : ׷���ٶ�
		@type		callback		  : callback functor
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���entity, targetPosition, success��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
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
		ˢ���ٶ�
		"""
		self._pursueSpeed = speed
		if len(self._sectPaths) > 1:
			nextPos = self._sectPaths[0]
			goalPos = self._sectPaths[-1]
			step = self.SYNC_INTERVAL * self._pursueSpeed
			self._sectPaths = self._splitPath(nextPos, goalPos, step)
			self._sectPaths.insert(0, nextPos)

	def isMoving( self ):
		"""�Ƿ������ƶ���׷�ٻ��߸���"""
		return self._syncTimer != None

	def stop( self ) :
		"""
		ֹͣһ��navigate�ƶ�
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
		"""����������ͬ����λ��"""
		return self._latestSyncPos


class PetChaser( FollowChaser ):
	"""����ר��׷���������洦����һ���ص㣺
	������׷�ٹ��̷ֿ�Ϊ�����׶Σ���һ����
	Ԥ׷�ٽ׶Σ�׷�ٵ�Ŀ��λ����������λ��
	����һС�ξ��룬��С�ξ��������ڶ�����
	һ���ϵ͵��ٶȸ���"""
	PREV_CHASE_OFFSET = 0.6						# Ԥ׷�ٽ׶Σ�������Ŀ��λ�ö�Զʱͣһ�£����õ��ٸ���
	PREV_CHASE_NEARBY = 3.0						# Ԥ׷�ٽ׶��趨����Ŀ����Զʱ��Ϊ����ľ���
	DST_HEIGHT_TOLERANCE = 3.0					# �ƶ���Ŀ��λ�ø߶ȷ����������Ŀ�������ֵ

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
		"""ͬ��ͼ�����ﴫ�͵�ָ��λ��"""
		self._navigator.teleportPosition(position)
		self.stop()

	def resumeFollow( self ):
		"""������ͣ�ĸ���"""
		FollowChaser.resumeFollow(self)
		self._addPot(self._followNearby)
		self._addTimer()

	def pauseFollow( self ):
		"""��ͣ���棬��ȡ����ǰ�ĸ���Ŀ��"""
		FollowChaser.pauseFollow(self)
		self._delPot()
		self._cancelTimer()
		self._navigator.stop()

	def isFollowing( self ):
		"""�Ƿ����ڸ�����"""
		return self._potID != None

	def stop( self ):
		"""ֹͣ׷�ٺ͸�����Ϊ"""
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
		"""Ԥ׷�ٽ׶ξ���Ŀ���Զ��Ϊ����ľ�������ֵ"""
		return self._followNearby - self._followTarget().position.distTo(self._prevChasePos)

	def _calcPrevChaseNearby( self ):
		"""����Ԥ׷�ٽ׶ξ���Ŀ���Զ��Ϊ����ľ�������ֵ"""
		return min(self.PREV_CHASE_NEARBY, self._calcPrevChaseNearbyMax())

	def _stayRange( self ):
		"""׷��Ŀ��λ�õ�ƫ��"""
		return self._followNearby*0.6

	def _searchPrevFollowPosition( self ):
		"""����Ԥ׷��λ��"""
		target = self._followTarget()
		pos = self._getFollowPosition()
		pos = self._formatPosition(pos, target.yaw, -self.PREV_CHASE_OFFSET)
		pos = utils.posOnGround(target.spaceID, pos)
		# ���������ָ���߶���û�е�������λ���ж�Ϊ��Ч�����ó����ø���Ŀ�����
		if pos is None or self._dstInvalid(pos):
			pos = self._formatPosition(target.position, target.yaw, -self._stayRange())
			pos = utils.posOnGround(target.spaceID, pos, default=target.position)
			# �����Ŀ�����Ҳȡ�������ʵĵ㣬��ֱ�Ӹ���Ŀ���λ��
			if self._dstInvalid(pos):
				pos = target.position
		return pos

	def _getFollowPosition( self ):
		"""��ȡ׷��λ��"""
		target = self._followTarget()
		if target:
			return self._formatPosition(target.position, target.yaw+math.pi/2, self._stayRange())
		else:
			return self._consigner.position

	def _formatPosition( self, pos, yaw, offset ):
		"""����yaw��offset�����µ�λ��"""
		rx, ry, rz = pos
		x = rx + offset * math.sin(yaw)
		z = rz + offset * math.cos(yaw)
		return Math.Vector3( x, ry, z )

	def _dstInvalid( self, dstPosition ):
		"""���Ŀ��λ���Ƿ񲻺���"""
		targetPosition = self._followTarget().position
		# ���Ŀ��λ���Ƿ���nearby��Χ֮��
		if targetPosition.distTo(dstPosition) > self._followNearby:
			return True
		# ���Ŀ��λ�������Ŀ���λ�õĸ߶Ȳ��Ƿ����
		if abs(dstPosition.y - targetPosition.y) > self.DST_HEIGHT_TOLERANCE:
			return True
		# ���Ŀ��λ�������Ŀ���λ����ˮƽ�������Ƿ���Ŵ���ײ�����壬
		# �Դ��жϳ�����ܻ��߽�ǽ������ڵ�����
		apos = Math.Vector3(targetPosition)
		apos.y += self._followTarget().getBoundingBox().y/2.0
		# ȡ���ĸ߶�λ��
		bpos = Math.Vector3(dstPosition)
		bpos.y += self._consigner.getBoundingBox().y/2.0
		# �������������ײ��⣬���Ƿ������
		if BigWorld.collide(self._followTarget().spaceID, apos, bpos) != None:
			return True
		return False

	def _chaseFollowTarget( self ):
		"""׷�ٸ����Ŀ��"""
		self._chasePosition(self._prevChasePos, self._prevChaseNearby, self._prevChaseSpeed, self._onChasePosOver)

	def _updatePrevChase( self ):
		"""����Ԥ׷��λ�ú��ٶ�"""
		self._prevChasePos = self._searchPrevFollowPosition()
		# Ԥ׷��λ�����»�ȡ�����¼��������浽�����
		self._prevChaseNearby = self._calcPrevChaseNearby()
		# �ٶ����ã�1.2��֮���ܸ���Ŀ����ٶȺ��趨�ĸ����ٶ�֮�еĽϴ�ֵ
		self._prevChaseSpeed = max(self._followSpeed, self._consigner.position.distTo(self._prevChasePos)/1.2)

	def _onChasePosOver( self, owner, pos, success ):
		"""׷��λ�ý���"""
		target = self._followTarget() if self._followTarget else None
		if target is None:
			self._cancelTimer()
		elif self._arrive(target.position):
			dstPos = self._formatPosition(pos, target.yaw, self.PREV_CHASE_OFFSET - 0.1)
			dstPos = utils.posOnGround(target.spaceID, dstPos, default=pos)
			# Ŀ��λ����Ч�Լ��
			if self._dstInvalid(dstPos):
				dstPos = self._formatPosition(target.position, target.yaw, -self._stayRange())
				dstPos = utils.posOnGround(target.spaceID, dstPos, default=target.position)
				# �����Ŀ�����Ҳȡ�������ʵĵ㣬��ֱ�Ӹ���Ŀ���λ��
				if self._dstInvalid(dstPos):
					dstPos = target.position
			self._chasePosition(dstPos, 0.2, 1.2)			# ׷�ٵ�Ŀ�ĵغ��ó������Ŀ��ĳ������ǰ�����Ե�������ĳ���
			self.stop()
		elif success:										# ���ص��ɹ���ʵ��ȴδ����ʱ����������׷�٣��������һ��timer����ֹ���Ҳ���·�����¿ͻ��˿�ס
			self._updatePrevChase()
			self._chaseFollowTarget()

	# -------------------------------------------------
	# protected for pot trigger
	# -------------------------------------------------
	def _addPot( self, radius ):
		"""���һ��ר�����PlayerRole������"""
		self._delPot()
		self._potID = BigWorld.addPot(self._consigner.matrix, radius, self._onPotHit)

	def _delPot( self ):
		"""�Ƴ�����"""
		if self._potID is not None:
			BigWorld.delPot(self._potID)
			self._potID = None

	def _onPotHit( self, enteredPot, handle ):
		"""���崥��"""
		if not enteredPot and not self._pausing:
			self._addTimer()

	# -------------------------------------------------
	# protected for callback
	# -------------------------------------------------
	def _addTimer( self ):
		"""��ʼ׷�ٺ�����timer��ͣ׷��Ŀ�꣬�Ա������
		������һ�ߵ�����"""
		self._cancelTimer()
		self._timer = Timer.addTimer( 0.1, 1.0, self._onTimer )

	def _cancelTimer( self ):
		if self._timer is not None:
			Timer.cancel(self._timer)
			self._timer = None

	def _onTimer( self ):
		"""�ص��������׷��Ŀ��λ��"""
		self._updatePrevChase()
		self._chaseFollowTarget()

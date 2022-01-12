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
		@param		speed			  : ׷���ٶ�
		@type		callback		  : callback functor
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���entity, targetEntity, success��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
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
		@param		speed			  : ׷���ٶ�
		@type		callback		  : callback functor
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���entity, targetEntity, success��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
		@return						  : None
		"""
		pass

	def updateVelocity( self, speed ) :
		"""
		ˢ���ٶ�
		"""
		pass

	def isMoving( self ):
		"""�Ƿ������ƶ���׷�ٻ��߸���"""
		return False

	def stop( self ) :
		"""
		ֹͣһ��navigate�ƶ�
		"""
		pass

	def slipping( self ):
		"""�Ƿ��ڻ���״̬�������и�����"""
		return False


# **
# Ѱ·��Ϊ�����ͻ���ʹ��NavigateEx����entity��Ѱ·
# ��Ϊ������Ҫ��entity�ṩʹ��NavigateEx�����������
# �ͽӿڣ�Ϊ����entity����ȥ������Щ�ض���ص����Ժ�
# �ӿڣ�ʹ����������entity���з�װ����Ϊentity��Ѱ
# ·������NavigateEx���Ӷ���entity��NavigateEx����
# �϶Ƚ�����͡�
# ע�⣺ֻ�ʺ��ڿͻ�����physics��entity��
#
# ��ί����(consigner)Լ�������ԣ�
# position	: Vector3
# spaceID	: int
# yaw		: float
# physics	: Physics
# **
class NavigateProxy(INavigator):
	"""�ͻ���Ѱ·�����������navigate���ƿͻ���entity
	�ƶ���׷�٣������ǿͻ��˿��Ƶ�entity����Ч"""

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
		�Զ�Ѱ·�Ƿ񵽴�Ŀ�ĵصĻص�֪ͨ�������ڴ���һЩ����
		@type    state: bool
		@param   state: �Ƿ�ɹ�����Ŀ�ĵ�
		"""
		pass

	def getPhysics( self ):
		"""
		��ȡphysics
		"""
		return getattr(self._consigner, "physics", None)

	def onPursueOver( self, success ):
		"""
		�ṩ��navigator�ص��ķ���
		"""
		self.stop()

	def seek( self, position, verticalRange, callback, isSeekToGoal = True ) :
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
		�ṩ��navigator���entity pursue״̬�ķ���
		"""
		return self._isPursue

	# ---------------------------------------------------------------
	# end - methods and properties referenced by navigator
	# ---------------------------------------------------------------

#	# seek callback -------------------------------------------------
	# ---------------------------------------------------------------
	def _onSeekCallback( self, isSuccess ):
		"""physics��seek�Ļص�����"""
		physics = self.getPhysics()
		if physics:
			physics.stop()								# Ϊ��ֹ������Ѱ·����ʱ������ֹͣһ���ƶ�
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
		@param		speed			  : ׷���ٶ�
		@type		callback		  : callback functor
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���entity, targetEntity, success��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
		@return						  : None
		"""
		self.stop()
		self._isPursue = True
		self.updateVelocity(speed)
		#self._pursueCallback = callback
		# ��Ϊ����navigate��callback����BigWorld.callable(0, callback)���첽��ʽ
		# �ص��ģ�����ֺܶ��첽���⣬�����ͬ���ص�����onPursueOver��֪ͨ�ص�
		self._navigator.pursueEntity( entity, nearby, callback )

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
		@param		callback		  : ��pursue����ʱ�ص����ûص������������������ֱ���entity, targetEntity, success��
										successΪboolֵ��True��ʾ׷�ٳɹ��������ʾʧ�ܣ�
										���targetEntityֵΪNone���ʾĿ���Ѳ����ڣ�
		@return						  : None
		"""
		self.stop()
		self._isPursue = True
		self.updateVelocity(speed)
		#self._pursueCallback = callback
		# ��Ϊ����navigate��callback����BigWorld.callable(0, callback)���첽��ʽ
		# �ص��ģ�����ֺܶ��첽���⣬�����ͬ���ص�����onPursueOver��֪ͨ�ص�
		self._navigator.pursuePosition( pos, nearby, callback )

	def updateVelocity( self, speed ) :
		"""
		ˢ���ٶ�
		"""
		self._pursueSpeed = speed
		self.getPhysics().velocity = ( 0.0, 0.0, speed )

	def isMoving( self ):
		"""�Ƿ������ƶ���׷�ٻ��߸���"""
		return self._navigator.isRunning()

	def stop( self ) :
		"""
		ֹͣһ��navigate�ƶ�
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
		"""�Ƿ��ڻ���״̬�������и����⣺
		���physics��velocity����һ���������ٶȣ�
		���ҵ�ǰ����seeking����chasing״̬�����
		����physics��entity�ͻᴦ�ڻ�����״̬"""
		physics = self.getPhysics()
		return physics\
			and not physics.seeking\
			and not physics.chasing\
			and (physics.velocity.x > 0.0\
				or physics.velocity.z > 0.0)


# **
# �����׷��Ŀ�ꡢ����Ŀ�����Ϊ���з�װ������Щ��Ϊ
# ��ʹ������͸���ģ�ʹ����ͨ�����ö�Ӧ�ķ����������
# ����ΪЧ����Ҳ�ܴ���ص���֪��Ϊ�����������Ҫ����
# �������Ϊ����ο�չ��
# **
class Chaser:
	"""׷����"""

	def __init__( self, consigner, navigator ):
		self._consigner = weakref.proxy(consigner)
		assert isinstance(navigator, INavigator), "navigator must be instance of INavigator"
		self._navigator = navigator

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def chaseEntity( self, entity, nearby, speed, callback = _callback_3args ):
		"""׷��Ŀ��"""
		self.stop()
		self._chaseEntity(entity, nearby, speed, callback)

	def chasePosition( self, pos, nearby, speed, callback = _callback_3args ):
		"""׷�ٵص�"""
		self.stop()
		self._chasePosition(pos, nearby, speed, callback)

	def crossAreaChase( self, pos, nearby, speed, dstSpaceLabel, callback = _callback_2args ):
		"""������ص�׷��"""
		assert 0, "Not yet provided."

	def updateSpeed( self, speed ):
		"""����׷���ٶ�"""
		if self.isMoving():
			self._navigator.updateVelocity(speed)

	def isMoving( self ):
		"""�Ƿ������ƶ���"""
		return self._navigator.isMoving()

	def slipping( self ):
		"""�Ƿ����ڻ�����Ư�ƣ���״̬"""
		return self._navigator.slipping()

	def stop( self ):
		"""ֹͣ׷�ٺ͸�����Ϊ"""
		self._navigator.stop()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def _chaseEntity( self, entity, nearby, speed, callback = _callback_3args ):
		"""׷��Ŀ�꣬����������׷�٣�����¼����"""
		self._navigator.pursueEntity(entity, nearby, speed, callback)

	def _chasePosition( self, pos, nearby, speed, callback = _callback_3args ):
		"""׷�ٵص㣬����������׷�٣�����¼����"""
		self._navigator.pursuePosition(pos, nearby, speed, callback)


class FollowChaser( Chaser ):
	"""�����湦�ܵ�׷��������Ҫֱ��ʹ�����׷����
	��Ϊ���׷������δʵ�ָ���Ĺ��ܣ�ֻ��Ϊ����ʹ��"""

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
		"""����Ŀ��"""
		self.stop()
		self._followSpeed = speed
		self._followNearby = nearby
		self._followTarget = weakref.ref(entity)
		self._followNotifier = callback					# ע�⣬������ܲ�����������
		self.resumeFollow()

	def resumeFollow( self ):
		"""������ͣ�ĸ���"""
		self._pausing = False

	def pauseFollow( self ):
		"""��ͣ���棬��ȡ����ǰ�ĸ���Ŀ��"""
		self._pausing = True

	def isFollowing( self ):
		"""�Ƿ����ڸ�����"""
		return False

	def updateSpeed( self, speed ):
		"""����׷���ٶ�"""
		self._followSpeed = speed
		if self.isMoving():
			self._navigator.updateVelocity(speed)

	def stop( self ):
		"""ֹͣ׷�ٺ͸�����Ϊ"""
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
		"""�Ƿ񵽴�pos"""
		return self._consigner.position.distTo(pos) <= self._followNearby

	def _onFollowBroken( self ):
		"""�����ж�"""
		if callable(self._followNotifier):
			target = self._followTarget()
			self._followNotifier(target and target.id or None)


class CallbackChaser( FollowChaser ):
	"""�����ڻص������ĸ���׷��"""

	def __init__( self, consigner, navigator ):
		FollowChaser.__init__(self, consigner, navigator)
		self._cbInterval = 0.5						# �ص����
		self._callbackID = None

	def stop( self ):
		"""ֹͣ׷�ٺ͸�����Ϊ"""
		FollowChaser.stop(self)
		self._cancelFollowCallback()

	def resumeFollow( self ):
		"""������ͣ�ĸ���"""
		FollowChaser.resumeFollow(self)
		self._resumeFollowCallback()

	def pauseFollow( self ):
		"""��ͣ���棬��ȡ����ǰ�ĸ���Ŀ��"""
		FollowChaser.pauseFollow(self)
		self._navigator.stop()
		self._cancelFollowCallback()

	def isFollowing( self ):
		"""�Ƿ����ڸ�����"""
		return self._callbackID != None

	def _onFollowCallback( self ):
		"""����ص����"""
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
		"""ȡ������ص�"""
		if self._callbackID != None:
			BigWorld.cancelCallback(self._callbackID)
			self._callbackID = None

	def _resumeFollowCallback( self ):
		"""��������ص�"""
		self._cancelFollowCallback()
		self._callbackID = BigWorld.callback(self._cbInterval, self._onFollowCallback)


class ITimer:

	def __init__( self ):
		self._cbInterval = 0.5						# �ص����
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
